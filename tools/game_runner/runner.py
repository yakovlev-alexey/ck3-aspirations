"""Owned-session CK3 runner. Reports contain measured native state."""
import hashlib
import json
import os
import secrets
import shutil
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from .protocol import LogCursor, ProtocolError, Telemetry, atomic_request, safe_path
from .windows import WindowsBackend


@dataclass
class Config:
    game_executable: Path
    user_data: Path
    baseline_save: Path
    output_root: Path
    startup_timeout: float = 90
    request_timeout: float = 15
    startup_settle_seconds: float = 25

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        allowed = set(cls.__dataclass_fields__)
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError("Unknown configuration fields")
        for key in ("game_executable", "user_data", "baseline_save", "output_root"):
            if key not in data or not isinstance(data[key], str) or not Path(data[key]).is_absolute():
                raise ValueError("Configuration paths must be explicit and absolute")
            data[key] = Path(data[key])
        result = cls(**data)
        result.validate()
        return result

    def validate(self):
        for key in ("game_executable", "user_data", "baseline_save", "output_root"):
            setattr(self, key, safe_path(getattr(self, key)))
        if not self.game_executable.is_file() or self.game_executable.name.lower() != "ck3.exe":
            raise ValueError("Configured CK3 executable is missing")
        if not self.user_data.is_dir() or not self.baseline_save.is_file() or self.baseline_save.suffix != ".ck3":
            raise ValueError("Existing user data and explicit disposable baseline save are required")
        if self.baseline_save.name.startswith(("autosave", "ironman")):
            raise ValueError("A disposable baseline is required")
        repository = Path(__file__).resolve().parents[2]
        if not self.output_root.is_relative_to(repository / ".local"):
            raise ValueError("Output must be under this repository's ignored .local directory")
        if any(type(value) not in (int, float) or not 0 < value <= 180 for value in (self.startup_timeout, self.request_timeout, self.startup_settle_seconds)):
            raise ValueError("Timeouts must be positive and bounded by 180 seconds")
        if any(char in str(self.baseline_save) for char in ('"', "\n", "\r")):
            raise ValueError("Unsupported baseline path")


class SessionGuard:
    def __init__(self, root):
        self.path = safe_path(root) / ".asp-automation.lock"
        self.owned = False

    def acquire(self):
        if self.owned:
            return
        try:
            self.path.mkdir()
        except FileExistsError as error:
            raise RuntimeError("Another runner owns this CK3 user-data session; stale locks require explicit inspection") from error
        self.owned = True
        (self.path / "owner.json").write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")

    def close(self):
        if self.owned:
            (self.path / "owner.json").unlink(missing_ok=True)
            self.path.rmdir()
            self.owned = False


class GameRunner:
    def __init__(self, config, *, backend=None, clock=time.monotonic, sleep=time.sleep):
        self.config = Config.load(config) if isinstance(config, (str, Path)) else config
        self.config.validate()
        self.clock, self.sleep = clock, sleep
        self.backend = backend or WindowsBackend(self.config)
        self.guard = SessionGuard(self.config.user_data)
        self.flight = threading.Lock()
        self.session = None
        self.request = 0
        self.request_root = self.config.user_data / "run"
        self.request_path = self.request_root / "asp_automation_request.txt"
        self.created_request_root = False
        self.launch_save = None
        self.original_request = None
        self.file_owned = False
        self.run_directory = None
        self.baseline_hash = hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest()

    def _wait(self, cursor, parser, timeout, *, ack=False):
        deadline = self.clock() + timeout
        while self.clock() < deadline:
            messages = parser.feed(cursor.read())
            if ack and any(message["kind"] == "ACK" for message in messages):
                return None
            if parser.terminal is not None:
                if ack:
                    raise ProtocolError("Native advance completed without an ACK")
                return parser.terminal
            self.sleep(min(0.1, max(0, deadline - self.clock())))
        raise TimeoutError("Native completion timed out; an ACK is not completion")

    def _directory(self):
        if self.run_directory is None:
            self.config.output_root.mkdir(parents=True, exist_ok=True)
            self.run_directory = self.config.output_root / (time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4))
            self.run_directory.mkdir()
        return self.run_directory

    def _start(self):
        if self.session is not None:
            return
        self.guard.acquire()
        if self.launch_save is None:
            save_root = safe_path(self.config.user_data / "save games")
            if not save_root.is_dir():
                raise ValueError("Existing CK3 save games directory is required")
            candidate = save_root / ("asp_automation_" + secrets.token_hex(8) + ".ck3")
            with self.config.baseline_save.open("rb") as source, candidate.open("xb") as target:
                self.launch_save = candidate  # Ownership begins only after exclusive creation.
                shutil.copyfileobj(source, target)
        if not self.file_owned:
            safe_path(self.request_root)
            if not self.request_root.exists():
                self.request_root.mkdir()
                self.created_request_root = True
            safe_path(self.request_path)
            self.original_request = self.request_path.read_bytes() if self.request_path.exists() else None
            self.file_owned = True
        self.backend.start(self.launch_save.name)
        # The native bridge is the readiness check. Do not type while a save is loading.
        deadline = self.clock() + self.config.startup_settle_seconds
        while self.clock() < deadline:
            self.sleep(min(0.2, deadline - self.clock()))
        self.backend.validate()
        self.backend.open_console()
        self.session = secrets.randbelow(80000000) + 10000000
        self.request = 0
        self._send("bootstrap")

    def _send(self, operation, days=0, replay=False):
        if not replay:
            self.request += 1
        session, request = self.session, self.request
        if operation == "bootstrap":
            effect = f"asp_test_automation_bootstrap_effect = {{ VERSION = 1 SESSION = {session} REQUEST = {request} }}"
        else:
            effect = f"asp_test_automation_request_effect = {{ VERSION = 1 SESSION = {session} REQUEST = {request} OP = {operation} DAYS = {days} }}"
        cursor = LogCursor(self.config.user_data / "logs" / "debug.log")
        parser = Telemetry(session, request)
        atomic_request(self.request_root, self.request_path, "hidden_effect = { " + effect + " }\n")
        self.backend.command("run asp_automation_request.txt")
        if operation == "advance" and not replay:
            # tick_day is a bounded native console command; delayed event verifies elapsed date.
            self._wait(cursor, parser, self.config.request_timeout, ack=True)
            self.backend.command(f"tick_day {days}")
        result = self._wait(cursor, parser, self.config.request_timeout)
        evidence = self._directory() / f"{session}-{request}{'-replay' if replay else ''}.json"
        evidence.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

    def _snapshot_logs(self, index):
        directory = self._directory() / f"logs-{index}"
        directory.mkdir(exist_ok=True)
        for name in ("debug.log", "error.log", "game.log"):
            source = self.config.user_data / "logs" / name
            if source.exists():
                shutil.copyfile(source, directory / name)
        return str(directory)

    def _report_operation(self, operation, days=0):
        if not self.flight.acquire(blocking=False):
            return {"status": "transport_error", "error": "Concurrent operation rejected"}
        try:
            self._start()
            initial = self._send("observe")
            final = self._send(operation, days) if operation != "observe" else initial
            assertions = []
            if operation == "advance":
                assertions.append({"name": "measured_day_delta", "passed": final["date"] - initial["date"] == days})
            return {"status": "passed" if all(item["passed"] for item in assertions) else "assertion_failed", "version": 1, "operation": operation, "initial": initial, "final": final, "assertions": assertions, "evidence": str(self._directory())}
        except (RuntimeError, ValueError, OSError, TimeoutError) as error:
            self.backend.stop()
            self.session = None
            return {"status": "timeout" if isinstance(error, TimeoutError) else "transport_error", "error": str(error), "version": 1, "operation": operation}
        finally:
            self.flight.release()

    def observe(self):
        return self._report_operation("observe")

    def advance_days(self, days):
        if type(days) is not int or not 1 <= days <= 30:
            raise ValueError("days must be an integer from 1 through 30")
        return self._report_operation("advance", days)

    def run_scenario(self, name, repeat=1):
        if name != "automation-smoke" or type(repeat) is not int or not 1 <= repeat <= 10:
            raise ValueError("Only automation-smoke with repeat 1 through 10 is implemented")
        if not self.flight.acquire(blocking=False):
            return {"status": "transport_error", "error": "Concurrent operation rejected"}
        self.run_directory = None
        report = {"status": "passed", "scenario": name, "version": 1, "repeat": repeat, "runs": [], "baseline_sha256": self.baseline_hash}
        try:
            for index in range(1, repeat + 1):
                self.backend.stop()
                self.session = None
                self._start()
                initial = self._send("observe")
                mutation = self._send("mutate")
                duplicate = self._send("mutate", replay=True)
                observed = self._send("observe")
                final = self._send("advance", 1)
                assertions = [
                    {"name": "baseline_counter", "passed": initial["counter"] == 0},
                    {"name": "single_mutation", "passed": mutation["counter"] - initial["counter"] == 7},
                    {"name": "duplicate_identity_and_result", "passed": duplicate == mutation},
                    {"name": "no_repeated_mutation", "passed": observed["counter"] == mutation["counter"]},
                    {"name": "actual_day_advanced", "passed": final["date"] - observed["date"] == 1},
                    {"name": "same_baseline_date", "passed": not report["runs"] or initial["date"] == report["runs"][0]["initial"]["date"]},
                    {"name": "fresh_session", "passed": all(initial["session"] != run["initial"]["session"] for run in report["runs"])},
                    {"name": "baseline_unchanged", "passed": hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest() == self.baseline_hash},
                ]
                run = {"index": index, "initial": initial, "mutation": mutation, "duplicate": duplicate, "observed": observed, "final": final, "assertions": assertions, "logs": self._snapshot_logs(index)}
                report["runs"].append(run)
                if not all(item["passed"] for item in assertions):
                    report["status"] = "assertion_failed"
                    break
            try:
                self.backend.screenshot(self._directory() / "final.png")
            except (ImportError, OSError):
                pass
        except (RuntimeError, ValueError, OSError, TimeoutError) as error:
            report["status"] = "timeout" if isinstance(error, TimeoutError) else "transport_error"
            report["error"] = str(error)
            self._snapshot_logs("failure")
            try:
                self.backend.screenshot(self._directory() / "failure.png")
            except (ImportError, OSError, RuntimeError):
                pass
            self.backend.stop()
            self.session = None
        finally:
            try:
                report["owned_pids"] = list(getattr(self.backend, "started_pids", []))
                report["evidence"] = str(self._directory())
                (self._directory() / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            except OSError as error:
                report["status"] = "transport_error"
                report["error"] = "Could not persist evidence: " + str(error)
            finally:
                self.flight.release()
        return report

    def close(self):
        if not self.flight.acquire(blocking=False):
            raise RuntimeError("Cannot close while an operation is running")
        try:
            self.backend.stop()
            self.session = None
            if self.file_owned:
                safe_path(self.request_path)
                if self.original_request is None:
                    self.request_path.unlink(missing_ok=True)
                else:
                    # Restore only the dedicated request file captured by this instance.
                    temporary = self.request_path.with_suffix(".restore")
                    safe_path(temporary)
                    with temporary.open("xb") as stream:
                        stream.write(self.original_request)
                    os.replace(temporary, self.request_path)
                self.file_owned = False
            if self.launch_save is not None:
                safe_path(self.launch_save).unlink(missing_ok=True)
                self.launch_save = None
            if self.created_request_root:
                if not any(self.request_root.iterdir()):
                    self.request_root.rmdir()
                self.created_request_root = False
            self.guard.close()
            return {"status": "passed", "closed": True}
        finally:
            self.flight.release()

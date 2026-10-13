"""Owned-session CK3 runner. Reports contain measured native state."""
import hashlib
import json
import os
import re
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
        parser = Telemetry(session, request, operation=operation)
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
        if name not in ("automation-smoke", "core-regression", "vengeance-regression", "lifecycle-regression", "recovery-regression") or type(repeat) is not int or not 1 <= repeat <= 10:
            raise ValueError("Only registered scenarios with repeat 1 through 10 are implemented")
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
                if name == "core-regression":
                    core = self._send("core_regression")
                    duplicate = self._send("core_regression", replay=True)
                    assertions = [
                        {"name": "C01_exact_caps_and_rejection", "passed": core["c01"] == 1 and core["c01_ambitions"] == 3 and core["c01_desires"] == 5 and core["c01_rejected"] == 1},
                        {"name": "C02_exactly_once_stress_and_slot", "passed": core["c02"] == 1 and core["c02_before"] > 20 and core["c02_delta"] == -20 and core["c02_callbacks"] == 1 and core["c02_slots_before"] == 1 and core["c02_slots_after"] == 0},
                        {"name": "C09_forgiveness_cost", "passed": core["c09"] == 1 and core["c09_delta"] == core["c09_expected"]},
                        {"name": "C10_suspended_policy", "passed": core["c10"] == 1 and core["c10_delta"] == 0 and core["c10_policy_none"] == 1},
                        {"name": "C11_ineligible_AI_landless", "passed": core["c11"] == 1 and core["c11_landless"] == 1 and core["c11_ai"] == 1 and core["c11_active"] == 0},
                        {"name": "duplicate_identity_and_measurements", "passed": duplicate == core},
                        {"name": "same_baseline_date", "passed": not report["runs"] or initial["date"] == report["runs"][0]["initial"]["date"]},
                        {"name": "fresh_session", "passed": all(initial["session"] != run["initial"]["session"] for run in report["runs"])},
                        {"name": "baseline_unchanged", "passed": hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest() == self.baseline_hash},
                    ]
                    run = {"index": index, "initial": initial, "core": core, "duplicate": duplicate, "assertions": assertions, "logs": self._snapshot_logs(index)}
                    report["runs"].append(run)
                    if not all(item["passed"] for item in assertions):
                        report["status"] = "assertion_failed"
                        break
                    continue
                if name == "recovery-regression":
                    recovery = self._send("recovery_regression")
                    duplicate = self._send("recovery_regression", replay=True)
                    assertions = [
                        {"name": "H01_incident_and_legal_origin", "passed": recovery["h01"] == 1 and recovery["origin_control"] == 69},
                        {"name": "H02_two_milestones_once", "passed": recovery["h02"] == 1 and recovery["reward_stress"] == -20 and recovery["reward_xp"] == 100 and recovery["modifier_count"] == 1 and recovery["replayed"] == 0},
                        {"name": "H03_original_payer_and_start_identity", "passed": recovery["h03"] == 1 and recovery["unproven"] == 0 and recovery["foreign"] == 0 and recovery["cancelled"] == 0},
                        {"name": "H04_loss_and_independent_native_costs", "passed": recovery["h04"] == 1 and recovery["loss_stress"] == recovery["loss_control"] and recovery["loss_control"] > 0 and recovery["pledge_stress"] == recovery["pledge_control"] and recovery["pledge_control"] > 0 and recovery["pledge_prestige"] == -100},
                        {"name": "H05_declaration_and_repeat_incident", "passed": recovery["h05"] == 1},
                        {"name": "duplicate_identity_and_measurements", "passed": duplicate == recovery},
                        {"name": "same_baseline_date", "passed": not report["runs"] or initial["date"] == report["runs"][0]["initial"]["date"]},
                        {"name": "fresh_session", "passed": all(initial["session"] != run["initial"]["session"] for run in report["runs"])},
                        {"name": "baseline_unchanged", "passed": hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest() == self.baseline_hash},
                    ]
                    run = {"index": index, "initial": initial, "recovery": recovery, "duplicate": duplicate, "assertions": assertions, "logs": self._snapshot_logs(index)}
                    errors = Path(run["logs"]) / "error.log"
                    diagnostics = errors.read_text(encoding="utf-8-sig", errors="replace") if errors.exists() else ""
                    blocks = re.split(r"(?=\[.*?\]\[E\])", diagnostics)
                    aspiration_errors = [block for block in blocks if "asp_" in block and any(tag in block for tag in ("Script system error!", "pdx_persistent_reader.cpp", "Unknown trigger:", "Unknown effect:", "Failed to parse", "Data error in", "triggered but has no valid options"))]
                    assertions.append({"name": "aspiration_runtime_diagnostics_absent", "passed": not aspiration_errors})
                    run["aspiration_runtime_error_count"] = len(aspiration_errors)
                    report["runs"].append(run)
                    if not all(item["passed"] for item in assertions):
                        report["status"] = "assertion_failed"
                        break
                    continue
                if name == "lifecycle-regression":
                    lifecycle = self._send("lifecycle_regression")
                    duplicate = self._send("lifecycle_regression", replay=True)
                    assertions = [
                        {"name": "P01_review_origin_and_free_release", "passed": lifecycle["p01"] == 1 and lifecycle["release_delta"] == 0},
                        {"name": "P02_declaration_age_and_custody", "passed": lifecycle["p02"] == 1},
                        {"name": "P03_settlement_precedence", "passed": lifecycle["p03"] == 1 and lifecycle["ui_replay"] == 1 and lifecycle["penalty_prestige"] == -100 and lifecycle["penalty_stress"] == lifecycle["penalty_control"] and lifecycle["penalty_control"] > 0},
                        {"name": "P04_return_exactly_once", "passed": lifecycle["p04"] == 1 and lifecycle["return_prestige"] == -100 and lifecycle["return_stress"] == lifecycle["penalty_control"]},
                        {"name": "P05_absent_fulfillment_no_reward_and_death", "passed": lifecycle["p05"] == 1 and lifecycle["absent_stress"] == 0},
                        {"name": "P06_explicit_replacement", "passed": lifecycle["p06"] == 1 and lifecycle["replacement_count"] == 3 and lifecycle["replacement_delta"] == lifecycle["replacement_control"] and lifecycle["replacement_control"] > 0},
                        {"name": "duplicate_identity_and_measurements", "passed": duplicate == lifecycle},
                        {"name": "same_baseline_date", "passed": not report["runs"] or initial["date"] == report["runs"][0]["initial"]["date"]},
                        {"name": "fresh_session", "passed": all(initial["session"] != run["initial"]["session"] for run in report["runs"])},
                        {"name": "baseline_unchanged", "passed": hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest() == self.baseline_hash},
                    ]
                    # Calendar starts from a fresh baseline: logic fixtures intentionally cause deaths.
                    # Preserve both intervals; do not let their delayed vanilla grief contaminate boundary costs.
                    logic_logs = self._snapshot_logs(str(index) + "-logic")
                    self.backend.stop()
                    self.session = None
                    self._start()
                    calendar_setup = self._send("lifecycle_calendar")
                    reload_precondition = self._send("lifecycle_reload_assert")
                    calendar_day = self._send("advance", 1)
                    calendar = self._send("lifecycle_calendar_assert")
                    calendar_duplicate = self._send("lifecycle_calendar_assert", replay=True)
                    assertions.extend([
                        {"name": "exact_saved_state_precondition", "passed": reload_precondition["reload_identity"] == 1},
                        {"name": "actual_calendar_day", "passed": calendar_day["date"] - calendar_setup["date"] == 1 and calendar["calendar_after"] - calendar["calendar_before"] == 1},
                        {"name": "P01_actual_review_boundary", "passed": calendar["calendar_reviews"] == 2},
                        {"name": "P02_actual_minimum_age_boundary", "passed": calendar["calendar_declare"] == 1},
                        {"name": "P03_actual_deadline_boundary", "passed": calendar["calendar_prestige"] == -100 and calendar["calendar_stress"] == calendar["calendar_control"] and calendar["calendar_control"] > 0},
                        {"name": "calendar_duplicate_identity", "passed": calendar == calendar_duplicate},
                    ])
                    run = {"index": index, "initial": initial, "lifecycle": lifecycle, "duplicate": duplicate, "logic_logs": logic_logs, "reload_precondition": reload_precondition, "calendar_setup": calendar_setup, "calendar_day": calendar_day, "calendar": calendar, "calendar_duplicate": calendar_duplicate, "assertions": assertions, "logs": self._snapshot_logs(index)}
                    errors = Path(run["logs"]) / "error.log"
                    diagnostics = errors.read_text(encoding="utf-8-sig", errors="replace") if errors.exists() else ""
                    logic_errors = Path(logic_logs) / "error.log"
                    if logic_errors.exists():
                        diagnostics += "\n" + logic_errors.read_text(encoding="utf-8-sig", errors="replace")
                    runtime_blocks = re.split(r"(?=\[.*?\]\[E\])", diagnostics)
                    aspiration_errors = [block for block in runtime_blocks if "asp_" in block and any(tag in block for tag in ("Script system error!", "pdx_persistent_reader.cpp", "Unknown trigger:", "Unknown effect:", "Failed to parse", "Data error in", "triggered but has no valid options"))]
                    assertions.append({"name": "aspiration_runtime_diagnostics_absent", "passed": not aspiration_errors})
                    run["aspiration_runtime_error_count"] = len(aspiration_errors)
                    report["runs"].append(run)
                    if not all(item["passed"] for item in assertions):
                        report["status"] = "assertion_failed"
                        break
                    continue
                if name == "vengeance-regression":
                    vengeance = self._send("vengeance_regression")
                    duplicate = self._send("vengeance_regression", replay=True)
                    assertions = [
                        {"name": "V01_consumed_known_origin", "passed": vengeance["v01"] == 1 and vengeance["v01_created"] == 1 and vengeance["v01_replayed"] == 0},
                        {"name": "V02_knowledge_gated_discovery", "passed": vengeance["v02"] == 1 and vengeance["v02_hidden"] == 0 and vengeance["v02_known"] == 1 and vengeance["v02_exposed"] == 0},
                        {"name": "V03_death_precedence_and_memories", "passed": vengeance["v03"] == 1 and vengeance["v03_personal_delta"] == -20 and vengeance["v03_impossible_delta"] == 0 and vengeance["v03_memories"] == 2},
                        {"name": "V04_new_custody_only", "passed": vengeance["v04"] == 1 and vengeance["v04_stress_delta"] == -20 and vengeance["v04_prestige_delta"] == 100 and vengeance["v04_preexisting"] == 0},
                        {"name": "V05_eligibility_and_trait_costs", "passed": vengeance["v05"] == 1 and vengeance["v05_content"] == 1 and vengeance["v05_exclusions"] == 3 and vengeance["v05_costs"] == 1},
                        {"name": "V06_vanilla_stress_separate_from_closure", "passed": vengeance["v06"] == 1 and vengeance["v06_action_delta"] > 0 and vengeance["v06_closure_delta"] == -20 and vengeance["v06_total_delta"] == vengeance["v06_action_delta"] - 20},
                        {"name": "duplicate_identity_and_measurements", "passed": duplicate == vengeance},
                        {"name": "same_baseline_date", "passed": not report["runs"] or initial["date"] == report["runs"][0]["initial"]["date"]},
                        {"name": "fresh_session", "passed": all(initial["session"] != run["initial"]["session"] for run in report["runs"])},
                        {"name": "baseline_unchanged", "passed": hashlib.sha256(self.config.baseline_save.read_bytes()).hexdigest() == self.baseline_hash},
                    ]
                    run = {"index": index, "initial": initial, "vengeance": vengeance, "duplicate": duplicate, "assertions": assertions, "logs": self._snapshot_logs(index)}
                    report["runs"].append(run)
                    if not all(item["passed"] for item in assertions):
                        report["status"] = "assertion_failed"
                        break
                    continue
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
            except (ImportError, OSError, RuntimeError, ValueError):
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

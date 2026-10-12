import tempfile
import threading
import unittest
from pathlib import Path

try:
    from tools.game_runner.runner import GameRunner, Config, SessionGuard
    from tools.game_runner.windows import FocusError, validate_foreground
except ImportError:
    GameRunner = None


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(GameRunner, "runner implementation is absent")

    def test_single_flight_shared_across_instances_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = SessionGuard(root), SessionGuard(root)
            first.acquire()
            with self.assertRaises(RuntimeError):
                second.acquire()
            first.close()
            second.acquire()
            second.close()
            self.assertFalse((root / ".asp-automation.lock").exists())

    def test_focus_rejection_never_calls_sender(self):
        calls = []
        with self.assertRaises(FocusError):
            validate_foreground(42, 100, 43, 100)
            calls.append("typed")
        self.assertEqual(calls, [])
        with self.assertRaises(FocusError):
            validate_foreground(42, 100, 42, 101)

    def test_timeout_uses_injected_clock_and_ack_cannot_pass(self):
        runner = GameRunner.__new__(GameRunner)
        time = [0.0]
        runner.clock = lambda: time[0]
        runner.sleep = lambda seconds: time.__setitem__(0, time[0] + seconds)
        class Empty:
            def read(self):
                return b"ASP_AUTOMATION|1|123|2|ACK\n"
        from tools.game_runner.protocol import Telemetry
        with self.assertRaises(TimeoutError):
            runner._wait(Empty(), Telemetry(123, 2), 0.5)
        self.assertGreaterEqual(time[0], 0.5)
        self.assertLess(time[0], 0.8)

    def test_modifier_is_released_when_input_loses_focus(self):
        from tools.game_runner.windows import WindowsBackend
        class LosingFocus(WindowsBackend):
            def __init__(self):
                self.pressed = set()
            def validate(self):
                pass
            def _input(self, vk=0, char=0, flags=0, release=False):
                if vk == 0x41:
                    raise FocusError("focus changed during chord")
                if flags & 2:
                    self.pressed.discard(vk)
                else:
                    self.pressed.add(vk)
        backend = LosingFocus()
        with self.assertRaises(FocusError):
            backend.command("observe")
        self.assertEqual(backend.pressed, set())

    def test_stop_only_terminates_exact_owned_process(self):
        import subprocess
        import sys
        from tools.game_runner.windows import WindowsBackend
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        first = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], creationflags=flags)
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], creationflags=flags)
        backend = WindowsBackend.__new__(WindowsBackend)
        backend.process = first
        backend.hwnd = 42
        try:
            backend.stop()
            self.assertIsNotNone(first.poll())
            self.assertIsNone(unrelated.poll())
            self.assertIsNone(backend.process)
        finally:
            if first.poll() is None:
                first.terminate()
            unrelated.terminate()
            first.wait(timeout=5)
            unrelated.wait(timeout=5)

    def test_failed_bootstrap_invalidates_session(self):
        runner = GameRunner.__new__(GameRunner)
        runner.flight = threading.Lock()
        runner.session = 123
        class Backend:
            def stop(self):
                pass
        runner.backend = Backend()
        runner._start = lambda: None
        def fail(operation, days=0):
            raise TimeoutError("bootstrap failed")
        runner._send = fail
        result = runner.observe()
        self.assertEqual(result["status"], "timeout")
        self.assertIsNone(runner.session)

    def test_advance_requires_ack_before_tick(self):
        from tools.game_runner.protocol import Telemetry, ProtocolError
        runner = GameRunner.__new__(GameRunner)
        runner.clock = lambda: 0
        runner.sleep = lambda seconds: None
        class DoneWithoutAck:
            def read(self):
                return b"ASP_AUTOMATION|1|123|2|DONE|counter=7|date=43000\n"
        with self.assertRaises(ProtocolError):
            runner._wait(DoneWithoutAck(), Telemetry(123, 2), 1, ack=True)

    def test_key_releases_owned_key_after_focus_changes(self):
        from tools.game_runner.windows import WindowsBackend
        class LostAfterDown(WindowsBackend):
            def __init__(self):
                self.pressed = set()
            def validate(self):
                raise FocusError("lost after key down")
            def _input(self, vk=0, char=0, flags=0, release=False):
                if flags & 2:
                    if not release:
                        raise FocusError("lost before key up")
                    self.pressed.discard(vk)
                else:
                    self.pressed.add(vk)
        backend = LostAfterDown()
        with self.assertRaises(FocusError):
            backend.key(0x41)
        self.assertEqual(backend.pressed, set())

    def test_process_inventory_timeout_is_bounded_transport_failure(self):
        import subprocess
        from unittest.mock import patch
        from tools.game_runner.windows import WindowsBackend
        backend = WindowsBackend.__new__(WindowsBackend)
        backend.process = None
        backend.preflight = lambda: None
        with patch("tools.game_runner.windows.subprocess.run", side_effect=subprocess.TimeoutExpired("tasklist", 10)):
            with self.assertRaises(TimeoutError):
                backend.start("asp_automation_0123456789abcdef.ck3")
        self.assertIsNone(backend.process)

    def test_invalid_arguments_have_no_backend_side_effect(self):
        runner = GameRunner.__new__(GameRunner)
        for name, repeat in [("arbitrary", 1), ("automation-smoke", 0), ("automation-smoke", True), ("automation-smoke", 11)]:
            with self.assertRaises(ValueError):
                runner.run_scenario(name, repeat)
        for days in [0, -1, 31, True, "1"]:
            with self.assertRaises(ValueError):
                runner.advance_days(days)

    def test_missing_game_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save = root / "test.ck3"
            save.write_bytes(b"disposable")
            with self.assertRaises(ValueError):
                Config(root / "missing.exe", root, save, root / "output").validate()


class NativeIOBoundary:
    """Deterministic native boundary; actual request files and log cursor stay real."""
    def __init__(self, config):
        self.config = config
        self.starts = 0
        self.running = False
        self.cached = None
        self.pending = None
        self.fail_once = False

    def start(self, save_name):
        self.starts += 1
        self.running = True
        self.counter, self.date = 0, 43000
        self.cached = None
        (self.config.user_data / "logs" / "debug.log").write_bytes(b"fresh game startup\n")

    def stop(self):
        self.running = False

    def validate(self):
        if not self.running:
            raise RuntimeError("not running")

    def open_console(self):
        self.validate()

    def screenshot(self, path):
        raise ImportError("optional capture unavailable")

    def command(self, command):
        import re
        log = self.config.user_data / "logs" / "debug.log"
        if command.startswith("tick_day"):
            self.date += int(command.split()[1])
            session, request = self.pending
            self.emit(log, session, request, "DONE")
            return
        text = (self.config.user_data / "run" / "asp_automation_request.txt").read_text(encoding="utf-8-sig")
        session = int(re.search(r"SESSION = (\d+)", text)[1])
        request = int(re.search(r"REQUEST = (\d+)", text)[1])
        if self.fail_once:
            self.fail_once = False
            return
        if self.cached and self.cached[:2] == (session, request):
            with log.open("ab") as stream:
                stream.write(self.cached[2])
            return
        if "OP = advance" in text:
            self.pending = (session, request)
            self.emit(log, session, request, "ACK")
            return
        if "OP = mutate" in text:
            self.counter += 7
        self.emit(log, session, request, "DONE")

    def emit(self, log, session, request, kind):
        line = f"ASP_AUTOMATION|1|{session}|{request}|{kind}"
        if kind == "DONE":
            line += f"|counter={self.counter}|date={self.date}"
        data = (line + "\n").encode()
        with log.open("ab") as stream:
            stream.write(data)
        if kind == "DONE":
            self.cached = (session, request, data)


class RunnerIOTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        local = Path(__file__).resolve().parents[3] / ".local"
        local.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=local)
        self.root = Path(self.temporary.name)
        self.game = self.root / "ck3.exe"
        self.game.write_bytes(b"configured fake native boundary")
        self.baseline = self.root / "baseline.ck3"
        self.baseline.write_bytes(b"disposable baseline")
        (self.root / "logs").mkdir()
        (self.root / "save games").mkdir()
        self.config = Config(self.game, self.root, self.baseline, self.root / "output", startup_settle_seconds=0.01, request_timeout=0.3)
        self.backend = NativeIOBoundary(self.config)
        time = [0.0]
        self.runner = GameRunner(self.config, backend=self.backend, clock=lambda: time[0], sleep=lambda seconds: time.__setitem__(0, time[0] + seconds))

    def tearDown(self):
        self.runner.close()
        self.temporary.cleanup()

    def test_three_runs_reset_and_restore_owned_files(self):
        (self.root / "run").mkdir()
        request = self.root / "run" / "asp_automation_request.txt"
        request.write_bytes(b"original dedicated request content")
        report = self.runner.run_scenario("automation-smoke", 3)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["runs"]), 3)
        self.assertEqual([run["initial"]["counter"] for run in report["runs"]], [0, 0, 0])
        self.assertEqual([run["final"]["date"] for run in report["runs"]], [43001, 43001, 43001])
        self.runner.close()
        self.assertFalse(self.backend.running)
        self.assertEqual(request.read_bytes(), b"original dedicated request content")
        self.assertEqual(list((self.root / "save games").iterdir()), [])
        self.assertFalse((self.root / ".asp-automation.lock").exists())

    def test_staged_save_name_collision_never_deletes_existing_save(self):
        from unittest.mock import patch
        existing = self.root / "save games" / "asp_automation_0123456789abcdef.ck3"
        existing.write_bytes(b"pre-existing owned by user")
        with patch("tools.game_runner.runner.secrets.token_hex", return_value="0123456789abcdef"):
            self.assertEqual(self.runner.observe()["status"], "transport_error")
            self.runner.close()
        self.assertEqual(existing.read_bytes(), b"pre-existing owned by user")

    def test_two_scenario_calls_keep_distinct_evidence(self):
        first = self.runner.run_scenario("automation-smoke")
        first_path = Path(first["evidence"]) / "report.json"
        original = first_path.read_bytes()
        second = self.runner.run_scenario("automation-smoke")
        self.assertEqual(second["status"], "passed")
        self.assertNotEqual(first["evidence"], second["evidence"])
        self.assertEqual(first_path.read_bytes(), original)

    def test_timeout_then_observe_starts_fresh_session(self):
        self.backend.fail_once = True
        self.assertEqual(self.runner.observe()["status"], "timeout")
        self.assertFalse(self.backend.running)
        self.assertEqual(self.runner.observe()["status"], "passed")
        self.assertEqual(self.backend.starts, 2)


if __name__ == "__main__":
    unittest.main()

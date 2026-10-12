import tempfile
import unittest
from pathlib import Path

try:
    from tools.game_runner.protocol import ProtocolError, Telemetry, LogCursor, atomic_request
except ImportError:
    Telemetry = None


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Telemetry, "protocol implementation is absent")
        self.parser = Telemetry(123, 2)

    def test_identity_filter_and_partial_utf8(self):
        self.assertEqual(self.parser.feed(b"old ASP_AUTOMATION|1|122|2|DONE|counter=7|date=43000\n"), [])
        self.assertEqual(self.parser.feed("unrelated cafÃ©\nASP_AUTOMATION|1|123|2|DO".encode()[:-1]), [])
        messages = self.parser.feed(b"ONE|counter=7|date=43000\n")
        self.assertEqual(messages[-1]["counter"], 7)
        self.assertEqual(messages[-1]["date"], 43000)

    def test_large_integer_measurement_is_not_rounded(self):
        result = self.parser.feed(b"ASP_AUTOMATION|1|123|2|DONE|counter=9007199254740993|date=43000\n")
        self.assertEqual(result[0]["counter"], 9007199254740993)

    def test_split_utf8_and_terminal_duplicate(self):
        self.parser.feed(b"caf\xc3")
        self.parser.feed(b"\xa9\n")
        line = b"ASP_AUTOMATION|1|123|2|DONE|counter=7|date=43000\n"
        self.assertEqual(len(self.parser.feed(line)), 1)
        self.assertEqual(self.parser.feed(line), [])
        with self.assertRaises(ProtocolError):
            self.parser.feed(line.replace(b"counter=7", b"counter=14"))

    def test_ack_is_not_completion_and_malformed_cannot_pass(self):
        self.assertEqual(self.parser.feed(b"ASP_AUTOMATION|1|123|2|ACK\n")[0]["kind"], "ACK")
        self.assertIsNone(self.parser.terminal)
        with self.assertRaises(ProtocolError):
            self.parser.feed(b"ASP_AUTOMATION|1|123|2|DONE|counter=seven|date=43000\n")

    def test_large_complete_unrelated_tick_logs_do_not_hide_terminal(self):
        data = b"unrelated native daily output\n" * 50000
        data += b"ASP_AUTOMATION|1|123|2|DONE|counter=7|date=43001\n"
        self.assertEqual(self.parser.feed(data)[-1]["date"], 43001)

    def test_log_freshness_truncation_and_rotation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "debug.log"
            path.write_bytes(b"old\n")
            cursor = LogCursor(path)
            self.assertEqual(cursor.read(), b"")
            with path.open("ab") as stream:
                stream.write(b"new\n")
            self.assertEqual(cursor.read(), b"new\n")
            path.write_bytes(b"x")
            with self.assertRaises(ProtocolError):
                cursor.read()
            cursor = LogCursor(path)
            path.rename(path.with_suffix(".old"))
            path.write_bytes(b"fresh\n")
            with self.assertRaises(ProtocolError):
                cursor.read()

    @unittest.skipUnless(__import__("os").name == "nt", "Windows junction boundary")
    def test_windows_junction_root_is_rejected(self):
        import subprocess
        from tools.game_runner.protocol import safe_path
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, link = root / "target", root / "junction"
            target.mkdir()
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            with self.assertRaises(ValueError):
                safe_path(link / "request.txt")
            self.assertTrue(target.is_dir())

    def test_request_atomic_bom_and_path_containment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "asp_automation_request.txt"
            atomic_request(root, target, "hello")
            self.assertEqual(target.read_bytes(), b"\xef\xbb\xbfhello")
            with self.assertRaises(ValueError):
                atomic_request(root, root.parent / "escape.txt", "bad")
            self.assertEqual(sorted(p.name for p in root.iterdir()), [target.name])


if __name__ == "__main__":
    unittest.main()

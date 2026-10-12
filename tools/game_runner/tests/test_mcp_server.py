"""Real stdio subprocess coverage; no game process or desktop input."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}}
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}
FAKE = '''
import sys
from tools.game_runner.mcp_server import serve
class Runner:
    def run_scenario(self, scenario, repeat=1):
        print("backend diagnostic")
        return {"status": "passed", "scenario": scenario, "repeat": repeat}
    def observe(self):
        MODE
        return {"status": "passed", "operation": "observe"}
    def advance_days(self, days):
        return {"status": "passed", "days": days}
    def close(self):
        print("closed", file=sys.stderr)
        CLOSE
sys.exit(serve(Runner()))
'''


def request(identity, method, **params):
    return {"jsonrpc": "2.0", "id": identity, "method": method, "params": params}


class MCPTests(unittest.TestCase):
    def exchange(self, messages, *, mode="pass", raw=None, close_fail=False):
        behavior = {"pass": "pass", "fail": 'raise RuntimeError("fake backend failure")',
                    "timeout": 'return {"status": "timeout", "error": "no DONE"}'}[mode]
        code = textwrap.dedent(FAKE.replace("MODE", behavior).replace("CLOSE", 'raise RuntimeError("fake cleanup failure")' if close_fail else "pass"))
        payload = raw if raw is not None else b"".join((json.dumps(item) + "\n").encode() for item in messages)
        result = subprocess.run([sys.executable, "-c", code], input=payload, capture_output=True,
                                cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=10,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.assertIn(b"closed", result.stderr, result.stderr.decode(errors="replace"))
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        for reply in replies:
            self.assertEqual(reply["jsonrpc"], "2.0")
            self.assertEqual(len(set(reply) & {"result", "error"}), 1)
        return result, replies

    def test_lifecycle_list_ping_and_eof_cleanup(self):
        result, replies = self.exchange([INIT, READY, request(2, "tools/list"), request(3, "ping")])
        self.assertEqual(result.returncode, 0)
        self.assertEqual([item["id"] for item in replies], [1, 2, 3])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(replies[0]["result"]["capabilities"], {"tools": {"listChanged": False}})
        tools = replies[1]["result"]["tools"]
        self.assertEqual([tool["name"] for tool in tools], ["aspirations_run_scenario", "aspirations_observe", "aspirations_advance_days"])
        self.assertTrue(all(tool["inputSchema"]["additionalProperties"] is False for tool in tools))
        self.assertEqual(replies[2]["result"], {})

    def test_actual_cli_entrypoint_lists_tools_without_launching(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as directory:
            root = Path(directory)
            executable = root / "ck3.exe"
            executable.write_bytes(b"not executable: listing must not launch")
            user = root / "user"
            (user / "save games").mkdir(parents=True)
            baseline = root / "baseline.ck3"
            baseline.write_bytes(b"disposable")
            config = root / "config.json"
            config.write_text(json.dumps({"game_executable": str(executable), "user_data": str(user),
                                          "baseline_save": str(baseline), "output_root": str(root / "output")}), encoding="utf-8")
            payload = "".join(json.dumps(item) + "\n" for item in [INIT, READY, request(2, "tools/list")]).encode()
            result = subprocess.run([sys.executable, "-m", "tools.game_runner", "--config", str(config), "mcp"],
                                    input=payload, capture_output=True, cwd=ROOT, timeout=10,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.assertEqual(result.returncode, 0, result.stderr)
            replies = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual(len(replies[-1]["result"]["tools"]), 3)
            self.assertFalse((user / ".asp-automation.lock").exists())
            self.assertEqual(list((user / "save games").iterdir()), [])

    def test_supported_version_fallback(self):
        init = {**INIT, "params": {**INIT["params"], "protocolVersion": "2099-01-01"}}
        _, replies = self.exchange([init, READY, request(2, "tools/list")])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertIn("tools", replies[1]["result"])

    def test_all_calls_delegate_and_stdout_is_protocol_only(self):
        _, replies = self.exchange([INIT, READY,
            request(2, "tools/call", name="aspirations_run_scenario", arguments={"scenario": "automation-smoke", "repeat": 2}),
            request(3, "tools/call", name="aspirations_observe"),
            request(4, "tools/call", name="aspirations_advance_days", arguments={"days": 30})])
        expected = [{"status": "passed", "scenario": "automation-smoke", "repeat": 2},
                    {"status": "passed", "operation": "observe"}, {"status": "passed", "days": 30}]
        for reply, report in zip(replies[1:], expected):
            self.assertEqual(reply["result"]["structuredContent"], report)
            self.assertEqual(json.loads(reply["result"]["content"][0]["text"]), report)
            self.assertFalse(reply["result"]["isError"])

    def test_core_regression_is_a_bounded_registered_scenario(self):
        _, replies = self.exchange([INIT, READY,
            request(2, "tools/call", name="aspirations_run_scenario", arguments={"scenario": "core-regression"})])
        self.assertEqual(replies[-1]["result"]["structuredContent"],
                         {"status": "passed", "scenario": "core-regression", "repeat": 1})

    def test_requires_initialize_and_ready_before_side_effects(self):
        _, replies = self.exchange([request(2, "tools/call", name="aspirations_observe"), INIT,
                                   request(3, "tools/call", name="aspirations_observe"), READY,
                                   request(4, "tools/call", name="aspirations_observe")])
        self.assertEqual(replies[0]["error"]["code"], -32000)
        self.assertEqual(replies[2]["error"]["code"], -32000)
        self.assertFalse(replies[3]["result"]["isError"])

    def test_invalid_arguments_have_no_backend_side_effects(self):
        cases = [("aspirations_observe", {"shell": "no"}),
                 ("aspirations_run_scenario", {}), ("aspirations_run_scenario", {"scenario": "arbitrary"}),
                 ("aspirations_run_scenario", {"scenario": "automation-smoke", "repeat": True}),
                 ("aspirations_run_scenario", {"scenario": "automation-smoke", "repeat": 11}),
                 ("aspirations_advance_days", {"days": 0}), ("aspirations_advance_days", {"days": 31}),
                 ("aspirations_advance_days", {"days": "1"}), ("aspirations_advance_days", {"days": 1.0})]
        _, replies = self.exchange([INIT, READY] + [request(i + 2, "tools/call", name=name, arguments=args) for i, (name, args) in enumerate(cases)])
        for reply in replies[1:]:
            self.assertTrue(reply["result"]["isError"])
            self.assertEqual(reply["result"]["structuredContent"]["status"], "invalid_arguments")

    def test_unknown_tools_and_malformed_call_are_protocol_errors(self):
        _, replies = self.exchange([INIT, READY, request(2, "tools/call", name="shell"),
                                   request(3, "tools/call", name="aspirations_observe", arguments=[]),
                                   request(4, "not_a_method")])
        self.assertEqual([reply["error"]["code"] for reply in replies[1:]], [-32602, -32602, -32601])

    def test_backend_exceptions_and_failed_reports_are_tool_errors(self):
        for mode, status in [("fail", "transport_error"), ("timeout", "timeout")]:
            with self.subTest(mode=mode):
                _, replies = self.exchange([INIT, READY, request(2, "tools/call", name="aspirations_observe")], mode=mode)
                self.assertTrue(replies[-1]["result"]["isError"])
                self.assertEqual(replies[-1]["result"]["structuredContent"]["status"], status)

    def test_notifications_never_execute_tools_or_reply(self):
        _, replies = self.exchange([INIT, READY, {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "aspirations_observe"}},
                                   {"jsonrpc": "2.0", "method": "unknown"}, request(2, "ping")], mode="fail")
        self.assertEqual([item["id"] for item in replies], [1, 2])

    def test_invalid_initialize_and_tool_metadata(self):
        invalid = {**INIT, "params": {"protocolVersion": "2025-11-25"}}
        _, replies = self.exchange([invalid, {**INIT, "id": 2}, READY,
                                   request(3, "tools/call", name="aspirations_observe", _meta={"progressToken": "ignored"}),
                                   request(4, "tools/list", cursor="unsupported"), request(5, "initialize", **INIT["params"])])
        self.assertEqual(replies[0]["error"]["code"], -32602)
        self.assertFalse(replies[2]["result"]["isError"])
        self.assertEqual(replies[3]["error"]["code"], -32602)
        self.assertEqual(replies[4]["error"]["code"], -32602)

    def test_malformed_utf8_json_batch_envelope_and_duplicate_ids(self):
        payload = b'\xff\n{bad}\n[]\n{"jsonrpc":"2.0","id":true,"method":"ping"}\n'
        payload += (json.dumps(INIT) + '\n' + json.dumps(READY) + '\n').encode()
        payload += b'{"jsonrpc":"2.0","id":2,"method":"ping"}\n' * 2
        _, replies = self.exchange([], raw=payload)
        self.assertEqual([item.get("error", {}).get("code") for item in replies], [-32700, -32700, -32600, -32600, None, None, -32600])

    def test_unicode_and_escaped_surrogate_ids_remain_protocol_safe(self):
        result, replies = self.exchange([INIT, READY, request("\ud800", "ping"), request("日本語", "ping")])
        self.assertEqual(result.returncode, 0)
        self.assertEqual([reply["id"] for reply in replies[1:]], ["\ud800", "日本語"])
        self.assertTrue(all(reply["result"] == {} for reply in replies[1:]))

    def test_oversized_and_unterminated_input_close_boundedly(self):
        for payload, code in [(b"x" * 65537, -32600), (b'{}', -32700)]:
            with self.subTest(code=code):
                result, replies = self.exchange([], raw=payload)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(replies[0]["error"]["code"], code)

    def test_clean_empty_eof_and_cleanup_failure_exit_codes(self):
        result, replies = self.exchange([])
        self.assertEqual((result.returncode, replies), (0, []))
        result, replies = self.exchange([], close_fail=True)
        self.assertEqual((result.returncode, replies), (1, []))
        self.assertIn(b"cleanup", result.stderr)


if __name__ == "__main__":
    unittest.main()

"""Narrow MCP 2025-11-25 stdio adapter over the owned-session runner."""
from contextlib import redirect_stdout
import json
import sys

PROTOCOL_VERSION = "2025-11-25"
MAX_LINE_BYTES = 65536
MAX_REQUESTS = 10000
TOOLS = [
    {"name": "aspirations_run_scenario", "description": "Run a registered disposable measured CK3 scenario; resets the owned session.",
     "inputSchema": {"type": "object", "properties": {
         "scenario": {"type": "string", "enum": ["automation-smoke", "core-regression", "vengeance-regression", "lifecycle-regression", "recovery-regression", "bond-regression"]},
         "repeat": {"type": "integer", "minimum": 1, "maximum": 10, "default": 1}},
         "required": ["scenario"], "additionalProperties": False}},
    {"name": "aspirations_observe", "description": "Observe native fixture state, lazily starting the configured disposable session.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "aspirations_advance_days", "description": "Advance the disposable session by bounded debug days; require measured native completion.",
     "inputSchema": {"type": "object", "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 30}},
                     "required": ["days"], "additionalProperties": False}},
]


class RPCError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def tool_result(report):
    return {"content": [{"type": "text", "text": json.dumps(report, ensure_ascii=False, allow_nan=False)}],
            "structuredContent": report, "isError": report.get("status") != "passed"}


def call_tool(runner, params):
    name = params.get("name")
    if not isinstance(name, str) or name not in {tool["name"] for tool in TOOLS}:
        raise RPCError(-32602, "Unknown tool")
    if set(params) - {"name", "arguments", "_meta"} or not isinstance(params.get("arguments", {}), dict):
        raise RPCError(-32602, "Malformed tools/call parameters")
    arguments = params.get("arguments", {})
    schema = next(tool["inputSchema"] for tool in TOOLS if tool["name"] == name)
    try:
        if set(arguments) - set(schema["properties"]) or set(schema.get("required", [])) - set(arguments):
            raise ValueError("Unexpected or missing tool arguments")
        if name == "aspirations_run_scenario":
            repeat = arguments.get("repeat", 1)
            if arguments["scenario"] not in ("automation-smoke", "core-regression", "vengeance-regression", "lifecycle-regression", "recovery-regression", "bond-regression") or type(repeat) is not int or not 1 <= repeat <= 10:
                raise ValueError("Only registered scenarios with repeat 1 through 10 are implemented")
            operation = lambda: runner.run_scenario(arguments["scenario"], repeat)
        elif name == "aspirations_advance_days":
            days = arguments["days"]
            if type(days) is not int or not 1 <= days <= 30:
                raise ValueError("days must be an integer from 1 through 30")
            operation = lambda: runner.advance_days(days)
        else:
            operation = runner.observe
    except ValueError as error:
        return tool_result({"status": "invalid_arguments", "error": str(error)})
    try:
        # Keep runner/backend diagnostics out of the protocol stream.
        with redirect_stdout(sys.stderr):
            report = operation()
        return tool_result(report)
    except Exception as error:
        print("Tool execution failed: " + str(error), file=sys.stderr)
        return tool_result({"status": "transport_error", "error": str(error)})


class Server:
    def __init__(self, runner):
        self.runner = runner
        self.initialized = False
        self.ready = False
        self.ids = set()

    def dispatch(self, message):
        identity = message.get("id") if isinstance(message, dict) else None
        valid_id = type(identity) in (str, int)
        if (not isinstance(message, dict) or message.get("jsonrpc") != "2.0"
                or not isinstance(message.get("method"), str)
                or ("id" in message and not valid_id)
                or "result" in message or "error" in message):
            raise RPCError(-32600, "Invalid JSON-RPC request")
        notification = "id" not in message
        params = message.get("params", {})
        if notification:
            if message["method"] == "notifications/initialized" and self.initialized and isinstance(params, dict):
                self.ready = True
            return None
        if identity in self.ids or len(self.ids) >= MAX_REQUESTS:
            raise RPCError(-32600, "Request ID reused or session request limit reached; reconnect")
        self.ids.add(identity)
        if not isinstance(params, dict):
            raise RPCError(-32602, "Parameters must be an object")
        method = message["method"]
        if method == "ping":
            return {}
        if method == "initialize":
            info = params.get("clientInfo")
            if (self.initialized or not isinstance(params.get("protocolVersion"), str)
                    or not isinstance(params.get("capabilities"), dict) or not isinstance(info, dict)
                    or not isinstance(info.get("name"), str) or not isinstance(info.get("version"), str)):
                raise RPCError(-32602, "Invalid or repeated initialization")
            self.initialized = True
            return {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "aspirations-game-runner", "version": "1.0.0"}}
        if not self.ready:
            raise RPCError(-32000, "Initialize and send notifications/initialized before using tools")
        if method == "tools/list":
            if set(params) - {"_meta"}:
                raise RPCError(-32602, "This fixed tool list has no pagination cursor")
            return {"tools": TOOLS}
        if method == "tools/call":
            return call_tool(self.runner, params)
        raise RPCError(-32601, "Method not found")


def _reject_constant(value):
    raise ValueError("Non-finite JSON number")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def serve(runner):
    """Serial dispatch; EOF waits for bounded work, then closes owned resources."""
    server = Server(runner)
    status = 0
    output = sys.stdout.buffer
    try:
        while True:
            line = sys.stdin.buffer.readline(MAX_LINE_BYTES + 1)
            if not line:
                break
            identity, fatal = None, False
            try:
                if len(line) > MAX_LINE_BYTES:
                    fatal = True
                    raise RPCError(-32600, "Input line exceeds 65536 bytes; closing connection")
                if not line.endswith(b"\n"):
                    fatal = True
                    raise RPCError(-32700, "Stdio messages require a terminating newline")
                try:
                    message = json.loads(line.decode("utf-8"), parse_constant=_reject_constant, object_pairs_hook=_unique_object)
                except (UnicodeError, ValueError, RecursionError) as error:
                    raise RPCError(-32700, "Malformed UTF-8 JSON message") from error
                if isinstance(message, dict) and type(message.get("id")) in (str, int):
                    identity = message["id"]
                result = server.dispatch(message)
                if result is None:
                    continue
                reply = {"jsonrpc": "2.0", "id": identity, "result": result}
            except RPCError as error:
                reply = {"jsonrpc": "2.0", "id": identity, "error": {"code": error.code, "message": str(error)}}
            output.write((json.dumps(reply, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8"))
            output.flush()
            if fatal:
                status = 1
                break
    except (BrokenPipeError, KeyboardInterrupt, OSError) as error:
        print("MCP transport stopped: " + str(error), file=sys.stderr)
        status = 1
    finally:
        try:
            with redirect_stdout(sys.stderr):
                runner.close()
        except Exception as error:
            print("MCP cleanup failed: " + str(error), file=sys.stderr)
            status = 1
    return status

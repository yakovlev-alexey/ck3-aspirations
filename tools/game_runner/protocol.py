"""Fresh byte-log transport with identity-bound terminal results."""
import os
import re
import tempfile
from pathlib import Path

MARKER = "ASP_AUTOMATION|"
CORE_FIELDS = (
    "c01", "c01_ambitions", "c01_desires", "c01_rejected",
    "c02", "c02_before", "c02_delta", "c02_callbacks", "c02_slots_before", "c02_slots_after",
    "c09", "c09_delta", "c09_expected",
    "c10", "c10_delta", "c10_policy_none",
    "c11", "c11_landless", "c11_ai", "c11_active",
)
VENGEANCE_FIELDS = ('v01', 'v01_created', 'v01_replayed', 'v02', 'v02_hidden', 'v02_known', 'v02_exposed', 'v03', 'v03_personal_delta', 'v03_impossible_delta', 'v03_memories', 'v04', 'v04_stress_delta', 'v04_prestige_delta', 'v04_preexisting', 'v05', 'v05_content', 'v05_exclusions', 'v05_costs', 'v06', 'v06_action_delta', 'v06_closure_delta', 'v06_total_delta')


LIFECYCLE_FIELDS = ('p01', 'p02', 'p03', 'p04', 'p05', 'p06', 'release_delta', 'penalty_prestige', 'penalty_stress', 'penalty_control', 'return_prestige', 'return_stress', 'absent_stress', 'replacement_count', 'replacement_delta', 'replacement_control', 'ui_replay')


CALENDAR_FIELDS = ('calendar_before', 'calendar_after', 'calendar_reviews', 'calendar_declare', 'calendar_prestige', 'calendar_stress', 'calendar_control')


RECOVERY_FIELDS = ('h01', 'h02', 'h03', 'h04', 'h05', 'reward_stress', 'reward_xp', 'modifier_count', 'loss_stress', 'loss_control', 'pledge_stress', 'pledge_control', 'pledge_prestige', 'unproven', 'foreign', 'cancelled', 'replayed', 'origin_control')


RELOAD_FIELDS = ("reload_identity",)


class ProtocolError(RuntimeError):
    pass


def safe_path(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        try:
            metadata = part.lstat()  # stat() follows Windows junctions and loses their reparse flag.
        except FileNotFoundError:
            continue
        if part.is_symlink() or getattr(metadata, "st_file_attributes", 0) & 0x400:
            raise ValueError("Reparse paths are not allowed")
    return path.resolve()


def atomic_request(root, target, text):
    root, target = safe_path(root), safe_path(target)
    if target.parent != root or target.name != "asp_automation_request.txt":
        raise ValueError("Request must use the owned name directly under user data")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=root, prefix=".asp-request-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text.encode("utf-8-sig"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


class Telemetry:
    def __init__(self, session, request, operation=None):
        self.session, self.request = session, request
        self.operation = operation
        self.buffer = b""
        self.terminal = None

    def feed(self, data):
        self.buffer += data
        lines = self.buffer.split(b"\n")
        self.buffer = lines.pop()
        if len(self.buffer) > 1024 * 1024:
            raise ProtocolError("Oversized or unterminated log record")
        messages = []
        for raw in lines:
            if b"ASP_AUTOMATION|" not in raw:
                continue
            try:
                line = raw.decode("utf-8", errors="strict")
                fields = line[line.index(MARKER) + len(MARKER):].strip().split("|")
                version, session, request = map(int, fields[:3])
                if (session, request) != (self.session, self.request):
                    continue
                if version != 1 or len(fields) < 4 or fields[3] not in ("ACK", "DONE", "ERROR"):
                    raise ValueError("Unsupported message")
                result = {"version": version, "session": session, "request": request, "kind": fields[3]}
                for field in fields[4:]:
                    key, value = field.split("=", 1)
                    allowed = {"counter", "date", "reason"}
                    if self.operation == "core_regression":
                        allowed.update(CORE_FIELDS)
                    if self.operation == "vengeance_regression":
                        allowed.update(VENGEANCE_FIELDS)
                    if self.operation == "recovery_regression":
                        allowed.update(RECOVERY_FIELDS)
                    if self.operation == "lifecycle_regression":
                        allowed.update(LIFECYCLE_FIELDS)
                    if self.operation == "lifecycle_calendar_assert":
                        allowed.update(CALENDAR_FIELDS)
                    if self.operation == "lifecycle_reload_assert":
                        allowed.update(RELOAD_FIELDS)
                    if key in result or key not in allowed:
                        raise ValueError("Invalid or duplicate field")
                    if key != "reason" and not re.fullmatch(r"-?\d+(?:\.0+)?", value):
                        raise ValueError("Non-integral measurement")
                    result[key] = value if key == "reason" else int(value.split(".", 1)[0])
                if result["kind"] == "ERROR":
                    raise ProtocolError("Native request rejected: " + result.get("reason", "unknown"))
                if result["kind"] == "DONE":
                    required = {"version", "session", "request", "kind", "counter", "date"}
                    if self.operation == "core_regression":
                        required.update(CORE_FIELDS)
                    if self.operation == "vengeance_regression":
                        required.update(VENGEANCE_FIELDS)
                    if self.operation == "recovery_regression":
                        required.update(RECOVERY_FIELDS)
                    if self.operation == "lifecycle_regression":
                        required.update(LIFECYCLE_FIELDS)
                    if self.operation == "lifecycle_calendar_assert":
                        required.update(CALENDAR_FIELDS)
                    if self.operation == "lifecycle_reload_assert":
                        required.update(RELOAD_FIELDS)
                    if set(result) != required:
                        raise ValueError("Incomplete measured terminal")
                    if self.terminal is not None:
                        if self.terminal != result:
                            raise ProtocolError("Conflicting duplicate terminal")
                        continue
                    self.terminal = result
                messages.append(result)
            except (ValueError, UnicodeError, IndexError) as error:
                raise ProtocolError("Malformed tagged telemetry") from error
        return messages


class LogCursor:
    def __init__(self, path):
        self.path = safe_path(path)
        self.identity = None
        self.offset = 0
        self.anchor = b""
        if self.path.exists():
            stat = self.path.stat()
            self.identity = (stat.st_dev, stat.st_ino)
            self.offset = stat.st_size
            with self.path.open("rb") as stream:
                stream.seek(max(0, self.offset - 64))
                self.anchor = stream.read(64)

    def read(self):
        if not self.path.exists():
            if self.identity is not None:
                raise ProtocolError("Log disappeared")
            return b""
        stat = self.path.stat()
        identity = (stat.st_dev, stat.st_ino)
        if self.identity is not None and (identity != self.identity or stat.st_size < self.offset):
            raise ProtocolError("Log rotated or truncated")
        self.identity = identity
        with self.path.open("rb") as stream:
            if self.anchor:
                stream.seek(self.offset - len(self.anchor))
                if stream.read(len(self.anchor)) != self.anchor:
                    raise ProtocolError("Log replaced in place")
            stream.seek(self.offset)
            data = stream.read(1024 * 1024)
            self.offset = stream.tell()
            stream.seek(max(0, self.offset - 64))
            self.anchor = stream.read(64)
        return data

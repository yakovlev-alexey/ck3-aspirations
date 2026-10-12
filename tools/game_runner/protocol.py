"""Fresh byte-log transport with identity-bound terminal results."""
import os
import re
import tempfile
from pathlib import Path

MARKER = "ASP_AUTOMATION|"


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
    def __init__(self, session, request):
        self.session, self.request = session, request
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
                    if key in result or key not in ("counter", "date", "reason"):
                        raise ValueError("Invalid or duplicate field")
                    if key != "reason" and not re.fullmatch(r"-?\d+(?:\.0+)?", value):
                        raise ValueError("Non-integral measurement")
                    result[key] = value if key == "reason" else int(value.split(".", 1)[0])
                if result["kind"] == "ERROR":
                    raise ProtocolError("Native request rejected: " + result.get("reason", "unknown"))
                if result["kind"] == "DONE":
                    if set(result) != {"version", "session", "request", "kind", "counter", "date"}:
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

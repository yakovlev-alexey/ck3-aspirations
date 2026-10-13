"""Bounded UI geometry and independent native postcondition/evidence checks.

Sending input never establishes success. The registered UI scenario must supply
identity-bound native telemetry and fresh captures after each real operation.
"""
import dataclasses
import hashlib
import math
import struct
import time
import zlib
from pathlib import Path


class UIError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class WindowGeometry:
    hwnd: int
    pid: int
    dpi: int
    client_width: int
    client_height: int
    image_width: int
    image_height: int
    screen_x: int
    screen_y: int

    def __post_init__(self):
        integers = dataclasses.astuple(self)
        if any(type(value) is not int for value in integers):
            raise ValueError('Window geometry requires integer measurements')
        if self.hwnd <= 0 or self.pid <= 0 or not 96 <= self.dpi <= 240:
            raise ValueError('Missing window ownership or unsupported DPI')
        if not all(0 < value <= 8192 for value in integers[3:7]):
            raise ValueError('Unsupported client or capture dimensions')
        scale_x = self.image_width / self.client_width
        scale_y = self.image_height / self.client_height
        if not math.isclose(scale_x, scale_y, abs_tol=0.002):
            raise ValueError('Capture and client have different aspect ratios')
        # An aware caller receives physical client units; a virtualized caller
        # receives DPI-scaled client units. Never apply an unconditional DPI factor.
        if not any(math.isclose(scale_x, scale, abs_tol=0.002) for scale in (1.0, self.dpi / 96)):
            raise ValueError('Capture/client scaling does not match measured DPI')

    def image_to_client(self, x, y):
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in (x, y)):
            raise ValueError('Image coordinates must be finite numbers')
        if not 0 <= x < self.image_width or not 0 <= y < self.image_height:
            raise ValueError('Image coordinate lies outside the captured client')
        return (min(self.client_width - 1, int(x * self.client_width / self.image_width)),
                min(self.client_height - 1, int(y * self.client_height / self.image_height)))

    def image_to_screen(self, x, y):
        client_x, client_y = self.image_to_client(x, y)
        return self.screen_x + client_x, self.screen_y + client_y

    def require_unchanged(self, current):
        if self != current:
            raise UIError('Window ownership or geometry changed since capture')

    def metadata(self):
        return dataclasses.asdict(self)


UI_FIELDS = ('first_id', 'second_id', 'selected_id', 'ambitions', 'declared_count',
             'first_identity', 'second_identity', 'first_declared', 'second_declared',
             'deadline_days', 'choice_second', 'eligible_count', 'origin_delta', 'review_delta', 'stress_delta', 'prestige_delta')


def validate_setup(values, *, opened=False):
    if not isinstance(values, dict) or set(values) != set(UI_FIELDS) or any(type(value) is not int for value in values.values()):
        raise UIError('Incomplete or malformed UI setup state')
    if not 0 < values['first_id'] < values['second_id']:
        raise UIError('UI setup did not create distinct allocated Stories')
    expected = dict(values, selected_id=0, ambitions=2, declared_count=0,
                    first_identity=1, second_identity=1, first_declared=0,
                    second_declared=0, deadline_days=0, choice_second=int(opened),
                    eligible_count=2, origin_delta=0, review_delta=0,
                    stress_delta=0, prestige_delta=0)
    if values != expected:
        raise UIError('Native deterministic UI setup/selector identity failed')
    return dict(values)


def validate_declaration(first_id, second_id, values):
    """Compare real declaration measurements to the independently captured setup."""
    if (type(first_id) is not int or type(second_id) is not int or
            not 0 < first_id < second_id):
        raise UIError('Expected distinct positive allocated Story identities')
    if not isinstance(values, dict) or set(values) != set(UI_FIELDS) or any(type(value) is not int for value in values.values()):
        raise UIError('Incomplete or malformed measured UI state')
    expected = dict(first_id=first_id, second_id=second_id, selected_id=second_id,
                    ambitions=2, declared_count=1, first_identity=1, second_identity=1,
                    first_declared=0, second_declared=1, deadline_days=1825,
                    choice_second=1, eligible_count=1, origin_delta=0, review_delta=0, stress_delta=0, prestige_delta=0)
    differences = [key for key in UI_FIELDS if values[key] != expected[key]]
    if differences:
        raise UIError('Native exact Story declaration failed: ' + ', '.join(differences))
    return dict(values)


def validate_reload(before, after):
    """The actual reloaded campaign must retain the measured state without setup."""
    if not isinstance(before, dict) or 'first_id' not in before or 'second_id' not in before:
        raise UIError('Missing pre-save native declaration state')
    validate_declaration(before['first_id'], before['second_id'], before)
    validate_declaration(before['first_id'], before['second_id'], after)
    if before != after:
        raise UIError('Native UI state changed across save and reload')
    return dict(after)


def _png_dimensions(data):
    """Validate complete ordinary RGB/RGBA PNG chunks and bounded decoded rows."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise UIError('Capture is not a PNG')
    offset, chunks, compressed, dimensions, channels = 8, 0, [], None, None
    ended = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise UIError('Truncated PNG chunk')
        length = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise UIError('Truncated PNG payload')
        payload = data[offset + 8:offset + 8 + length]
        checksum = struct.unpack_from('>I', data, offset + 8 + length)[0]
        if zlib.crc32(kind + payload) != checksum:
            raise UIError('PNG checksum mismatch')
        if kind == b'IHDR':
            if chunks or length != 13:
                raise UIError('Malformed PNG header')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            if not 0 < width <= 8192 or not 0 < height <= 8192 or depth != 8 or color not in (2, 6) or any((compression, filtering, interlace)):
                raise UIError('Unsupported PNG encoding')
            dimensions, channels = (width, height), 3 if color == 2 else 4
        elif kind == b'IDAT':
            compressed.append(payload)
        elif kind == b'IEND':
            if length or end != len(data):
                raise UIError('Malformed PNG ending')
            ended = True
        offset, chunks = end, chunks + 1
    if not ended or not dimensions or not compressed:
        raise UIError('Incomplete PNG')
    width, height = dimensions
    stride = width * channels + 1
    expected = stride * height
    decoder = zlib.decompressobj()
    try:
        rows = decoder.decompress(b''.join(compressed), expected + 1)
    except zlib.error as error:
        raise UIError('Undecodable PNG image') from error
    if len(rows) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise UIError('Incomplete or oversized PNG image')
    if any(rows[index] > 4 for index in range(0, expected, stride)):
        raise UIError('Invalid PNG row filter')
    return dimensions


def validate_frame(path, evidence_root, geometry, started_unix, operation):
    path, root = Path(path).resolve(), Path(evidence_root).resolve()
    if not path.is_relative_to(root) or path.suffix.lower() != '.png' or not path.is_file():
        raise UIError('Missing or outside UI screenshot evidence')
    stat = path.stat()
    if stat.st_mtime < started_unix or not 0 < stat.st_size <= 64 * 1024 * 1024:
        raise UIError('Stale or oversized UI screenshot evidence')
    data = path.read_bytes()
    width, height = _png_dimensions(data)
    if (width, height) != (geometry.image_width, geometry.image_height):
        raise UIError('UI screenshot dimensions disagree with measured geometry')
    return {'operation': operation, 'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
            'width': width, 'height': height, 'captured_unix': stat.st_mtime,
            'geometry': geometry.metadata()}


def wait_for_saved_campaign(path, baseline_hash, timeout, *, clock=time.monotonic, sleep=time.sleep):
    """Require stable new bytes; native post-reload telemetry proves persistence.

    The caller must choose a fresh owned filename before opening native Save Game.
    The helper never writes, removes or adopts a save and never treats existence as
    proof of Story persistence.
    """
    if type(timeout) not in (int, float) or not 0 < timeout <= 180:
        raise ValueError('Save wait must be bounded by 180 seconds')
    path, deadline = Path(path), clock() + timeout
    previous, stable_since = None, None
    while clock() < deadline:
        if path.is_file():
            stat = path.stat()
            if 0 < stat.st_size <= 1024 * 1024 * 1024:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest == baseline_hash:
                    raise UIError('UI save is unchanged baseline data')
                current = stat.st_size, stat.st_mtime_ns, digest
                if previous == current:
                    if clock() - stable_since >= 0.2:
                        return {'path': str(path.resolve()), 'sha256': digest, 'bytes': stat.st_size}
                else:
                    previous, stable_since = current, clock()
        sleep(min(0.1, max(0, deadline - clock())))
    raise TimeoutError('Native disposable campaign save did not stabilize')

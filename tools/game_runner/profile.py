"""Targeted, reversible profile preparation for a managed disposable session."""
import json
import re
import secrets
from pathlib import Path
from .protocol import safe_path


def autosave_span(raw):
    text = raw.decode('utf-8-sig')
    pattern = re.compile(r'\s+|#[^\n]*|"(?:[^"\\]|\\.)*"|[{}=]|[^\s{}="#]+')
    tokens = []
    position = 0
    while position < len(text):
        match = pattern.match(text, position)
        if match is None:
            raise ValueError('Malformed settings')
        position = match.end()
        if not match.group().isspace() and not match.group().startswith('#'):
            tokens.append(match)
    index = 0
    spans = {}
    def block(path=(), nested=False):
        nonlocal index
        if len(path) > 32:
            raise ValueError('Settings nesting exceeds bound')
        keys = set()
        while index < len(tokens):
            token = tokens[index]
            if token.group() == '}':
                if not nested:
                    raise ValueError('Unexpected closing brace')
                index += 1
                return
            key = token.group().strip('"')
            index += 1
            if key in keys or index >= len(tokens) or tokens[index].group() != '=':
                raise ValueError('Duplicate or malformed settings')
            keys.add(key)
            index += 1
            if index >= len(tokens):
                raise ValueError('Missing settings value')
            token = tokens[index]
            index += 1
            if token.group() == '{':
                block(path + (key,), True)
            elif token.group() in ('}', '='):
                raise ValueError('Malformed settings value')
            else:
                spans[path + (key,)] = (token.start(), token.end())
        if nested:
            raise ValueError('Unclosed settings block')
    block()
    if ('game', 'autosave', 'value') not in spans:
        raise ValueError('Missing game.autosave.value')
    return text, spans[('game', 'autosave', 'value')]


def mods_span(raw):
    text = raw.decode('utf-8-sig')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate launcher key')
            result[key] = value
        return result
    data = json.loads(text, object_pairs_hook=unique)
    if not isinstance(data, dict) or not isinstance(data.get('enabled_mods'), list):
        raise ValueError('Missing enabled_mods array')
    # Match top-level JSON properties, rather than a string in another value.
    decoder = json.JSONDecoder()
    index = text.index('{') + 1
    while True:
        while text[index].isspace() or text[index] == ',':
            index += 1
        if text[index] == '}':
            break
        key, length = decoder.raw_decode(text[index:])
        index += length
        while text[index].isspace():
            index += 1
        if text[index] != ':':
            raise ValueError('Malformed launcher JSON')
        index += 1
        while text[index].isspace():
            index += 1
        start = index
        _, length = decoder.raw_decode(text[index:])
        index += length
        if key == 'enabled_mods':
            return text, (start, index)
    raise ValueError('Missing launcher selection')


def replace_target(path, parser, expected, replacement):
    path = safe_path(path)
    raw = path.read_bytes()
    text, (start, end) = parser(raw)
    if text[start:end] != expected:
        raise ValueError('Owned target changed: ' + path.name)
    updated = text[:start] + replacement + text[end:]
    encoded = updated.encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8')
    if path.read_bytes() != raw:
        raise ValueError('Concurrent file mutation: ' + path.name)
    path.write_bytes(encoded)


class ManagedProfile:
    def __init__(self, user_data, mod_root, evidence):
        self.user_data = safe_path(user_data)
        self.mod_root = safe_path(mod_root)
        self.evidence = safe_path(evidence)
        self.changes = []
        self.descriptor = None
        self.descriptor_bytes = None

    def prepare(self):
        self.evidence.mkdir(parents=True, exist_ok=True)
        paths = [(self.user_data / 'pdx_settings.txt', autosave_span, '"NO_AUTOSAVE"'),
                 (self.user_data / 'dlc_load.json', mods_span, None)]
        parsed = []
        for path, parser, replacement in paths:
            raw = safe_path(path).read_bytes()
            text, (start, end) = parser(raw)
            (self.evidence / (path.name + '.before')).write_bytes(raw)
            parsed.append((path, parser, text[start:end], replacement))
        mod_directory = safe_path(self.user_data / 'mod')
        if not mod_directory.is_dir():
            raise ValueError('Existing CK3 mod directory required')
        candidate = mod_directory / ('asp_managed_' + secrets.token_hex(8) + '.mod')
        self.descriptor_bytes = ('name="Aspirations (Managed Test)"\npath="' + self.mod_root.as_posix() + '"\n').encode('utf-8')
        with candidate.open('xb') as stream:
            self.descriptor = candidate
            stream.write(self.descriptor_bytes)
        for path, parser, original, replacement in parsed:
            replacement = replacement or json.dumps(['mod/' + self.descriptor.name])
            # Record intent before mutation so partial preparation remains reversible.
            self.changes.append((path, parser, original, replacement))
            replace_target(path, parser, original, replacement)

    def restore(self):
        conflicts, restored = [], []
        for path, parser, original, prepared in reversed(self.changes):
            try:
                text, (start, end) = parser(safe_path(path).read_bytes())
                if text[start:end] == original:
                    restored.append(path.name)
                    continue
                replace_target(path, parser, prepared, original)
                restored.append(path.name)
            except (OSError, ValueError) as error:
                conflicts.append(str(error))
        if self.descriptor is not None:
            try:
                if self.descriptor.exists():
                    if safe_path(self.descriptor).read_bytes() != self.descriptor_bytes:
                        raise ValueError('Owned descriptor changed; retained')
                    self.descriptor.unlink()
                restored.append('temporary_descriptor')
            except (OSError, ValueError) as error:
                conflicts.append(str(error))
        return {'restored': not conflicts, 'targets': restored, 'conflicts': conflicts}

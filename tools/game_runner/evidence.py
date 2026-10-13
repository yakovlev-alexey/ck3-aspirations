"""Build provenance and required fresh native evidence for managed sessions."""
import hashlib
import json
import subprocess
import time
from pathlib import Path
from .protocol import safe_path
from .ui import UIError, WindowGeometry, validate_frame, _png_dimensions


def sha(path):
    return hashlib.sha256(safe_path(path).read_bytes()).hexdigest()


def validate_manifest(repository):
    repository = safe_path(repository)
    root = safe_path(repository / '.build/dev/mod')
    manifest = safe_path(repository / '.build/dev/manifest.json')
    entries = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if not isinstance(entries, list) or not entries:
        raise ValueError('Existing nonempty dev build manifest required')
    mapped, sources, source_hashes = set(), set(), {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'Source', 'Destination', 'Hash'}:
            raise ValueError('Invalid build manifest entry')
        source = safe_path(repository / entry['Source'])
        output = safe_path(root / entry['Destination'])
        generated_descriptor = entry['Source'] == 'packaging/descriptor.mod' and entry['Destination'] == 'descriptor.mod'
        allowed_source = (source.is_relative_to(repository / 'src') and 'game' in source.parts) or source.is_relative_to(repository / 'packaging')
        if not allowed_source or not output.is_relative_to(root):
            raise ValueError('Manifest path escapes owned source/output')
        if output in mapped or source in sources:
            raise ValueError('Duplicate manifest path')
        mapped.add(output)
        sources.add(source)
        source_hashes[entry['Source']] = sha(source)
        if (not generated_descriptor and source_hashes[entry['Source']] != entry['Hash'].lower()) or sha(output) != entry['Hash'].lower():
            raise ValueError('Source/build drift: ' + entry['Source'])
    actual = {safe_path(path) for path in root.rglob('*') if path.is_file()}
    source_files = {safe_path(path) for path in (repository / 'src').rglob('*') if path.is_file() and 'game' in path.relative_to(repository / 'src').parts}
    source_files.update(source for source in sources if source.is_relative_to(repository / 'packaging'))
    if mapped != actual or sources != source_files:
        raise ValueError('Unmapped or missing source/build files; rebuild dev output')
    return {'manifest_sha256': sha(manifest), 'descriptor_sha256': sha(root / 'descriptor.mod'), 'files': entries, 'source_sha256': source_hashes}


def check_dev_build(repository, timeout=30):
    try:
        result = subprocess.run(['pwsh', '-NoProfile', '-File', str(Path(repository) / 'tools/check.ps1'), '-Profile', 'dev'], cwd=repository, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        raise TimeoutError('Dev build preflight deadline exceeded') from error
    if result.returncode:
        raise ValueError('Existing dev build checks failed: ' + (result.stdout + result.stderr)[-2000:])
    return {'status': 'passed', 'output': result.stdout.strip()}


def revision(repository, timeout=10):
    deadline = time.monotonic() + timeout
    def git(*args):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Revision preflight deadline exceeded")
        try:
            return subprocess.run(['git', '-C', str(repository), *args], capture_output=True, text=True, check=True, timeout=remaining).stdout.strip()
        except subprocess.TimeoutExpired as error:
            raise TimeoutError('Revision preflight deadline exceeded') from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError('Revision provenance could not be read') from error
    return {'revision': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain')), 'changes': git('status', '--porcelain').splitlines()}


def validate_evidence(native, started, output_root):
    root = safe_path(output_root)
    evidence = safe_path(native.get('evidence', root / 'missing'))
    if not evidence.is_relative_to(root):
        raise ValueError('Native evidence escapes session directory')
    runs = native.get('runs', [])
    if len(runs) != native.get('repeat') or not runs:
        raise ValueError('Missing completed repetitions')
    paths = []
    screenshot = safe_path(evidence / 'final.png')
    if not screenshot.is_file() or not 0 < screenshot.stat().st_size <= 64 * 1024 * 1024:
        raise ValueError('Missing or oversized actual PNG screenshot')
    try:
        _png_dimensions(screenshot.read_bytes())
    except UIError as error:
        raise ValueError('Invalid required PNG screenshot: ' + str(error)) from error
    paths.append(screenshot)
    for run in runs:
        assertions = run.get('assertions', [])
        if not assertions or any(item.get('passed') is not True for item in assertions):
            raise ValueError('Missing or failed native assertions')
        measurements = {key: value for key, value in run.items() if isinstance(value, dict) and 'session' in value and 'request' in value}
        if not measurements:
            raise ValueError('Missing native request measurements')
        logic_keys = {'initial', 'lifecycle', 'duplicate'}
        if 'ui_declaration_logs' in run:
            declaration_session = run['initial']['session']
            reload_session = run['ui_reloaded']['session']
            if declaration_session == reload_session:
                raise ValueError('UI reload must use a fresh session')
            declaration_keys = {'initial', 'ui_setup', 'ui_open', 'ui_declared', 'ui_duplicate'}
            intervals = [(run['ui_declaration_logs'], declaration_session, {key: value for key, value in measurements.items() if key in declaration_keys}),
                         (run['logs'], reload_session, {key: value for key, value in measurements.items() if key not in declaration_keys})]
            required_frames = ['open-aspirations', 'select-story', 'declare-confirmation', 'declare-result', 'save-menu', 'save-dialog', 'save-name', 'save-result', 'reload-selector', 'reload-story']
            frames = run.get('ui_frames', [])
            if [frame.get('operation') for frame in frames] != required_frames:
                raise ValueError('Missing complete ordered native UI frame evidence')
            for frame in frames:
                geometry = WindowGeometry(**frame['geometry'])
                observed = validate_frame(frame['path'], evidence, geometry, started, frame['operation'])
                if observed != frame:
                    raise ValueError('UI screenshot metadata or bytes changed')
                paths.append(safe_path(frame['path']))
            frame_record = evidence / f"ui-frames-{run['index']}.json"
            if not frame_record.exists() or json.loads(frame_record.read_text()) != frames:
                raise ValueError('Missing matching UI frame record')
            paths.append(frame_record)
            saved = run['ui_save']
            retained = safe_path(saved['evidence_path'])
            if not retained.is_relative_to(evidence) or not retained.is_file() or sha(retained) != saved['sha256'] or retained.stat().st_size != saved['bytes'] or saved['sha256'] == native.get('baseline_sha256'):
                raise ValueError('Missing actual nonbaseline UI campaign evidence')
            paths.append(retained)
        elif 'logic_logs' in run:
            logic_session = run['initial']['session']
            calendar_session = run['calendar_setup']['session']
            if logic_session == calendar_session:
                raise ValueError('Lifecycle calendar must use a fresh session')
            intervals = [(run['logic_logs'], logic_session, {key: value for key, value in measurements.items() if key in logic_keys}),
                         (run['logs'], calendar_session, {key: value for key, value in measurements.items() if key not in logic_keys})]
        else:
            intervals = [(run['logs'], run['initial']['session'], measurements)]
        for directory, interval_session, interval_measurements in intervals:
            logs = safe_path(directory)
            if not logs.is_relative_to(evidence):
                raise ValueError('Log evidence escapes native directory')
            debug = logs / 'debug.log'
            if not debug.exists():
                raise ValueError('Missing fresh identity-bound native log')
            debug_text = debug.read_text(encoding='utf-8-sig', errors='replace')
            if not interval_measurements:
                raise ValueError('Missing measurements for retained log interval')
            for measurement in interval_measurements.values():
                session, request = measurement['session'], measurement['request']
                if session != interval_session:
                    raise ValueError('Measurement does not belong to its recorded log interval')
                terminal = f"ASP_AUTOMATION|1|{session}|{request}|DONE|"
                records = list(evidence.glob(f'{session}-{request}*.json'))
                if terminal not in debug_text or not records or not any(json.loads(record.read_text()) == measurement for record in records):
                    raise ValueError('Missing identity-bound terminal/request evidence')
                paths.extend(records)
            paths.append(debug)
            error_log = logs / 'error.log'
            if not error_log.exists():
                raise ValueError('Missing runtime diagnostic evidence')
            paths.append(error_log)
    persisted = evidence / 'report.json'
    if not persisted.exists() or json.loads(persisted.read_text()) != native:
        raise ValueError('Missing or inconsistent native report')
    paths.append(persisted)
    paths = sorted(set(paths))
    for path in paths:
        if path.stat().st_mtime < started:
            raise ValueError('Stale evidence: ' + path.name)
    return [{'path': str(path.relative_to(root)), 'sha256': sha(path), 'bytes': path.stat().st_size} for path in paths]


def persist_report(directory, report):
    directory = Path(directory)
    report['report_json'] = str(directory / 'report.json')
    report['report_markdown'] = str(directory / 'report.md')
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    native = report.get('native', {})
    assertions = [item for run in native.get('runs', []) for item in run.get('assertions', [])]
    lines = ['# Managed CK3 session', '', f"Status: {report['status']}. Scenario: {report['scenario']}; repeat: {report['repeat']}.", '',
             f"Revision: {report.get('source', {}).get('revision', 'unavailable')}; dirty: {report.get('source', {}).get('dirty', 'unavailable')}.",
             f"Duration: {report.get('duration_seconds', 0):.2f}s; deadline: {report['deadline_seconds']}s.",
             f"Assertions: {sum(item.get('passed') is True for item in assertions)}/{len(assertions)} passed.",
             f"Owned processes stopped: {report.get('cleanup', {}).get('processes_stopped', False)}; profile restored: {report.get('cleanup', {}).get('profile', {}).get('restored', False)}; baseline unchanged: {report.get('baseline_unchanged', False)}.", '']
    if report.get('error'):
        lines.extend(['Failure: ' + report['error'], ''])
    lines.extend(['Evidence:', ''])
    lines.extend('- `' + item['path'] + '` (' + item['sha256'] + ')' for item in report.get('evidence_files', []))
    lines.extend(['', 'Native measured state, assertion names, complete build file map, hashes and cleanup conflicts are in `report.json`.'])
    (directory / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

"""One-command prepare/run/evidence/restore lifecycle; raw artifacts stay ignored."""
import dataclasses
import hashlib
import json
import secrets
import shutil
import sys
import time
from pathlib import Path
from .evidence import check_dev_build, persist_report, revision, sha, validate_evidence, validate_manifest
from .processes import supervise_worker, WorkerCleanupError
from .profile import ManagedProfile
from .protocol import safe_path
from .registry import SCENARIOS
from .runner import Config, SessionGuard
from .windows import resolve_documents, require_idle_profile


class ManagedFiles:
    def __init__(self, config, directory):
        self.config, self.directory = config, directory
        self.save = None
        self.request = safe_path(config.user_data / 'run/asp_automation_request.txt')
        self.original = None
        self.captured = False
        self.created_root = False
        self.journal = directory / 'request-ownership.json'

    def prepare(self):
        if not self.request.parent.exists():
            self.request.parent.mkdir()
            self.created_root = True
        self.original = self.request.read_bytes() if self.request.exists() else None
        self.captured = True
        if self.original is not None:
            (self.directory / 'request.before').write_bytes(self.original)
        candidate = safe_path(self.config.user_data / 'save games' / ('asp_automation_' + secrets.token_hex(8) + '.ck3'))
        try:
            with candidate.open('xb') as target:
                self.save = candidate
                with self.config.baseline_save.open('rb') as source:
                    shutil.copyfileobj(source, target)
        finally:
            if self.save is not None:
                self.save_hash = sha(self.save)
        if self.save_hash != sha(self.config.baseline_save):
            raise ValueError('Baseline changed while staging')

    def restore(self):
        conflicts = []
        if self.captured:
            try:
                current = self.request.read_bytes() if self.request.exists() else None
                expected = json.loads(self.journal.read_text()).get('hashes', []) if self.journal.exists() else []
                if current != self.original:
                    if current is None or hashlib.sha256(current).hexdigest() not in expected:
                        raise ValueError('Request changed externally; retained')
                    if self.original is None:
                        self.request.unlink()
                    else:
                        self.request.write_bytes(self.original)
            except (OSError, ValueError) as error:
                conflicts.append(str(error))
        if self.save is not None:
            try:
                if self.save.exists():
                    if sha(self.save) != getattr(self, 'save_hash', sha(self.config.baseline_save)):
                        raise ValueError('Staged save changed externally; retained')
                    self.save.unlink()
            except (OSError, ValueError) as error:
                conflicts.append(str(error))
        if self.created_root:
            try:
                if self.request.parent.exists() and not any(self.request.parent.iterdir()):
                    self.request.parent.rmdir()
            except OSError as error:
                conflicts.append(str(error))
        return {'restored': not conflicts, 'conflicts': conflicts}


def run_managed_session(config, scenario, repeat=1, deadline=240):
    if scenario not in SCENARIOS or type(repeat) is not int or not 1 <= repeat <= 10:
        raise ValueError('Only registered scenarios with repeat 1 through 10 are supported')
    if type(deadline) is not int or not 1 <= deadline <= 900:
        raise ValueError('Session deadline must be an integer from 1 through 900 seconds')
    config = Config.load(config) if isinstance(config, (str, Path)) else config
    config.validate()
    repository = Path(__file__).resolve().parents[2]
    directory = config.output_root / ('managed-' + time.strftime('%Y%m%d-%H%M%S') + '-' + secrets.token_hex(4))
    directory.mkdir(parents=True)
    start, started = time.monotonic(), time.time()
    report = {'version': 1, 'status': 'transport_error', 'scenario': scenario, 'repeat': repeat, 'deadline_seconds': deadline, 'started_unix': started, 'cleanup': {'processes_stopped': True}}
    guard = SessionGuard(config.user_data)
    profile = ManagedProfile(config.user_data, repository / '.build/dev/mod', directory / 'backups')
    files = ManagedFiles(config, directory)
    baseline = sha(config.baseline_save)
    report['baseline_sha256'] = baseline
    def remaining(limit=900):
        value = deadline - (time.monotonic() - start)
        if value <= 0:
            raise TimeoutError('Managed session deadline exceeded')
        return min(limit, value)
    try:
        expected_user = safe_path(Path(resolve_documents()) / 'Paradox Interactive/Crusader Kings III')
        if config.user_data != expected_user:
            raise ValueError('Configured user_data must match actual Windows Documents')
        guard.acquire()
        require_idle_profile(timeout=remaining(10))
        report['source'] = revision(repository, timeout=remaining(10))
        report['build_check'] = check_dev_build(repository, timeout=remaining(30))
        report['build'] = validate_manifest(repository)
        remaining()
        profile.prepare()
        remaining()
        files.prepare()
        worker_config = dataclasses.replace(config, output_root=directory / 'native')
        payload = {'config': {key: str(value) if isinstance(value, Path) else value for key, value in dataclasses.asdict(worker_config).items()}, 'save': str(files.save), 'journal': str(files.journal), 'scenario': scenario, 'repeat': repeat}
        worker_input = directory / 'worker.json'
        worker_input.write_text(json.dumps(payload), encoding='utf-8')
        output = supervise_worker([sys.executable, '-m', 'tools.game_runner.session_worker', str(worker_input)], repository, remaining(), audit_path=directory / "process-ownership.json")
        native = json.loads(output)
        report['native'] = native
        report['status'] = native['status']
        if native['status'] == 'passed':
            report['evidence_files'] = validate_evidence(native, started, directory)
            if validate_manifest(repository) != report['build']:
                raise ValueError('Source/build changed during session')
            report['source_end'] = revision(repository, timeout=remaining(10))
            if report['source_end']['revision'] != report['source']['revision']:
                raise ValueError('Repository revision changed during session')
    except (RuntimeError, ValueError, OSError, TimeoutError) as error:
        report['status'] = 'timeout' if isinstance(error, TimeoutError) else 'transport_error'
        report['error'] = str(error)
        if isinstance(error, WorkerCleanupError):
            report['cleanup']['processes_stopped'] = False
    finally:
        # Supervisor returns/raises only after its exact Job has been stopped.
        if report['cleanup']['processes_stopped']:
            report['cleanup']['files'] = files.restore()
            report['cleanup']['profile'] = profile.restore()
            try:
                guard.close()
            except (OSError, RuntimeError) as error:
                report['cleanup']['lock_error'] = str(error)
        else:
            report['cleanup']['files'] = {'restored': False, 'conflicts': ['Owned process cleanup unconfirmed; files retained']}
            report['cleanup']['profile'] = {'restored': False, 'conflicts': ['Owned process cleanup unconfirmed; profile and lock retained for recovery']}
        process_audit = directory / 'process-ownership.json'
        if process_audit.exists():
            report['cleanup']['process_ownership'] = json.loads(process_audit.read_text())
        game_processes = directory / 'game-processes.json'
        if game_processes.exists():
            report['owned_pids'] = json.loads(game_processes.read_text()).get('owned_pids', [])
        elif files.journal.exists():
            report['owned_pids'] = json.loads(files.journal.read_text()).get('owned_pids', [])
        try:
            report['baseline_unchanged'] = sha(config.baseline_save) == baseline
        except (OSError, ValueError) as error:
            report['baseline_unchanged'] = False
            report['cleanup']['baseline_error'] = str(error)
        if not report['baseline_unchanged'] or not report['cleanup']['files']['restored'] or not report['cleanup']['profile']['restored'] or report['cleanup'].get('lock_error'):
            report['status'] = 'transport_error'
            report.setdefault('error', 'Cleanup conflict or baseline mutation; inspect retained backups')
        report['duration_seconds'] = time.monotonic() - start
        persist_report(directory, report)
    return report

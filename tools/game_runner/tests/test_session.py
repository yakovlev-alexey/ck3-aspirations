"""Managed workflow safety tests use real files and bounded subprocesses."""
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
try:
    from tools.game_runner import session
except ImportError:
    session = None


class ManagedTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(session, 'Managed workflow is absent')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.user = self.root / 'Documents/Paradox Interactive/Crusader Kings III'
        (self.user / 'mod').mkdir(parents=True)
        (self.user / 'save games').mkdir()
        self.settings = self.user / 'pdx_settings.txt'
        self.settings.write_bytes(b'"game"={"autosave"={version=0 value="YEARLY"}}\n"renderer"={"scale"=1}\n')
        self.dlc = self.user / 'dlc_load.json'
        self.dlc.write_bytes(b'{"enabled_mods": ["mod/user.mod"], "disabled_dlcs": []}\n')

    def profile(self):
        return session.ManagedProfile(self.user, self.root / 'build/mod', self.root / 'evidence')

    def test_normal_targeted_restoration_preserves_unrelated_settings(self):
        before = self.dlc.read_bytes()
        profile = self.profile()
        profile.prepare()
        self.assertIn(b'NO_AUTOSAVE', self.settings.read_bytes())
        self.settings.write_bytes(self.settings.read_bytes().replace(b'"scale"=1', b'"scale"=2'))
        audit = profile.restore()
        self.assertTrue(audit['restored'])
        self.assertIn(b'YEARLY', self.settings.read_bytes())
        self.assertIn(b'"scale"=2', self.settings.read_bytes())
        self.assertEqual(self.dlc.read_bytes(), before)
        self.assertEqual(list((self.user / 'mod').iterdir()), [])

    def test_external_target_change_is_not_overwritten(self):
        profile = self.profile()
        profile.prepare()
        self.settings.write_bytes(self.settings.read_bytes().replace(b'NO_AUTOSAVE', b'MONTHLY'))
        self.dlc.write_bytes(b'{"enabled_mods": ["mod/concurrent.mod"], "disabled_dlcs": []}')
        audit = profile.restore()
        self.assertFalse(audit['restored'])
        self.assertEqual(len(audit['conflicts']), 2)
        self.assertIn(b'MONTHLY', self.settings.read_bytes())
        self.assertIn(b'concurrent.mod', self.dlc.read_bytes())
        self.assertEqual(list((self.user / 'mod').iterdir()), [])

    def test_partial_setup_failure_can_restore_already_written_settings(self):
        profile = self.profile()
        original = self.settings.read_bytes()
        self.dlc.write_bytes(b'{bad json')
        with self.assertRaises(ValueError):
            profile.prepare()
        self.assertTrue(profile.restore()['restored'])
        self.assertEqual(self.settings.read_bytes(), original)

    def test_comments_and_duplicate_settings_cannot_enable_preparation(self):
        self.settings.write_bytes(b'# "autosave"={value="YEARLY"}\n"game"={"autosave"={value="YEARLY"} "autosave"={value="YEARLY"}}')
        original = self.settings.read_bytes()
        profile = self.profile()
        with self.assertRaises(ValueError):
            profile.prepare()
        profile.restore()
        self.assertEqual(self.settings.read_bytes(), original)

    def manifest(self):
        (self.root / 'src/core/game/events').mkdir(parents=True)
        source = self.root / 'src/core/game/events/asp.txt'
        source.write_bytes(b'fixture')
        output = self.root / '.build/dev/mod/events'
        output.mkdir(parents=True)
        (output / 'asp.txt').write_bytes(b'fixture')
        (output.parent / 'descriptor.mod').write_bytes(b'name="dev"')
        (self.root / 'packaging').mkdir()
        (self.root / 'packaging/descriptor.mod').write_bytes(b'name="release"')
        (self.root / '.build/dev/manifest.json').write_text(json.dumps([{'Source': 'src/core/game/events/asp.txt', 'Destination': 'events/asp.txt', 'Hash': hashlib.sha256(b'fixture').hexdigest()}, {'Source': 'packaging/descriptor.mod', 'Destination': 'descriptor.mod', 'Hash': hashlib.sha256(b'name="dev"').hexdigest()}]))
        return source

    def test_manifest_detects_source_drift_and_unmapped_built_files(self):
        source = self.manifest()
        self.assertEqual(len(session.validate_manifest(self.root)['files']), 2)
        source.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            session.validate_manifest(self.root)
        source.write_bytes(b'fixture')
        (self.root / '.build/dev/mod/events/stale.txt').write_bytes(b'old')
        with self.assertRaises(ValueError):
            session.validate_manifest(self.root)

    def test_owned_job_stops_descendants_and_preserves_unrelated_process(self):
        import ctypes
        from ctypes import wintypes
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            code = "import sys,subprocess;sys.stdin.readline();p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);print(p.pid)"
            pid = int(session.supervise_worker([sys.executable, '-c', code], self.root, 3))
            api = ctypes.WinDLL('kernel32', use_last_error=True)
            api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            api.OpenProcess.restype = wintypes.HANDLE
            api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            api.CloseHandle.argtypes = [wintypes.HANDLE]
            handle = api.OpenProcess(0x100000, False, pid)
            if handle:
                try:
                    self.assertEqual(api.WaitForSingleObject(handle, 0), 0)
                finally:
                    api.CloseHandle(handle)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)

    def test_missing_stale_or_unrelated_evidence_cannot_pass(self):
        evidence = self.root / 'native'
        logs = evidence / 'logs-1'
        logs.mkdir(parents=True)
        (logs / 'debug.log').write_text('ASP_AUTOMATION|1|123|1|ACK\n')
        native = {'status': 'passed', 'repeat': 1, 'evidence': str(evidence), 'runs': [{'index': 1, 'initial': {'session': 123}, 'assertions': [{'name': 'native', 'passed': True}], 'logs': str(logs)}]}
        started = time.time() - 1
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)
        (evidence / 'final.png').write_bytes(b'not a screenshot')
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)
        initial = {'session': 123, 'request': 2, 'counter': 0, 'date': 43000}
        native['runs'][0]['initial'] = initial
        (logs / 'debug.log').write_text('ASP_AUTOMATION|1|123|2|DONE|counter=0|date=43000\n')
        (logs / 'error.log').write_text('')
        (evidence / '123-2.json').write_text(json.dumps(initial))
        (evidence / 'final.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGMQcYsCAAEmALW1sxutAAAAAElFTkSuQmCC'))
        (evidence / 'report.json').write_text(json.dumps(native))
        self.assertEqual(len(session.validate_evidence(native, started, self.root)), 5)
        os.utime(evidence / 'final.png', (started - 10, started - 10))
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)
        os.utime(evidence / 'final.png', None)
        (evidence / '123-2.json').write_text(json.dumps({**initial, 'counter': 100}))
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)
        (evidence / '123-2.json').write_text(json.dumps(initial))
        (logs / 'error.log').unlink()
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)

    def test_partial_staging_failure_removes_only_exclusively_created_save(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        baseline = self.root / 'baseline.ck3'
        baseline.write_bytes(b'immutable')
        directory = self.root / 'evidence'
        directory.mkdir()
        files = session.ManagedFiles(SimpleNamespace(user_data=self.user, baseline_save=baseline), directory)
        def partial(source, target):
            target.write(b'partial')
            raise OSError('injected copy failure')
        with patch.object(session.shutil, 'copyfileobj', side_effect=partial):
            with self.assertRaises(OSError):
                files.prepare()
        self.assertTrue(files.restore()['restored'])
        self.assertEqual(list((self.user / 'save games').iterdir()), [])

    def test_managed_files_preserve_external_request_and_save_changes(self):
        from types import SimpleNamespace
        baseline = self.root / 'baseline.ck3'
        baseline.write_bytes(b'immutable')
        directory = self.root / 'evidence'
        directory.mkdir()
        files = session.ManagedFiles(SimpleNamespace(user_data=self.user, baseline_save=baseline), directory)
        files.prepare()
        files.request.write_bytes(b'concurrent user request')
        files.save.write_bytes(b'concurrent save')
        result = files.restore()
        self.assertFalse(result['restored'])
        self.assertEqual(len(result['conflicts']), 2)
        self.assertEqual(files.request.read_bytes(), b'concurrent user request')
        self.assertEqual(files.save.read_bytes(), b'concurrent save')
        self.assertEqual(baseline.read_bytes(), b'immutable')

    def test_partial_write_failure_restores_completed_profile_edits(self):
        from unittest.mock import patch
        from tools.game_runner import profile as profile_module
        original = self.settings.read_bytes()
        original_replace = profile_module.replace_target
        def fail_dlc(path, *args):
            if path.name == 'dlc_load.json':
                raise OSError('injected write failure')
            return original_replace(path, *args)
        profile = self.profile()
        with patch.object(profile_module, 'replace_target', side_effect=fail_dlc):
            with self.assertRaises(OSError):
                profile.prepare()
        self.assertTrue(profile.restore()['restored'])
        self.assertEqual(self.settings.read_bytes(), original)
        self.assertEqual(list((self.user / 'mod').iterdir()), [])

    def test_managed_normal_assertion_startup_and_deadline_paths_restore_profile(self):
        from unittest.mock import patch
        from tools.game_runner.runner import Config
        repo = Path(session.__file__).resolve().parents[2]
        output_temp = tempfile.TemporaryDirectory(dir=repo / '.local')
        self.addCleanup(output_temp.cleanup)
        baseline = self.root / 'baseline.ck3'
        baseline.write_bytes(b'immutable')
        executable = self.root / 'ck3.exe'
        executable.write_bytes(b'fake executable is never launched')
        config = Config(executable, self.user, baseline, Path(output_temp.name))
        settings_before, dlc_before = self.settings.read_bytes(), self.dlc.read_bytes()
        self.manifest()
        def worker(command, cwd, timeout, audit_path=None):
            payload = json.loads(Path(command[-1]).read_text())
            native = Path(payload['config']['output_root']) / 'measured'
            logs = native / 'logs-1'
            logs.mkdir(parents=True)
            (logs / 'debug.log').write_text('ASP_AUTOMATION|1|123|2|DONE|counter=0|date=43000\n')
            (logs / 'error.log').write_text('')
            (native / 'final.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGMQcYsCAAEmALW1sxutAAAAAElFTkSuQmCC'))
            initial = {'session': 123, 'request': 2, 'counter': 0, 'date': 43000}
            (native / '123-2.json').write_text(json.dumps(initial))
            result = {'status': 'passed', 'repeat': 1, 'evidence': str(native), 'runs': [{'index': 1, 'initial': initial, 'assertions': [{'name': 'native', 'passed': True}], 'logs': str(logs)}]}
            (native / 'report.json').write_text(json.dumps(result))
            return json.dumps(result)
        manifest = session.validate_manifest(self.root)
        for outcome, expected in [(worker, 'passed'), (lambda *args, **kwargs: json.dumps({'status': 'assertion_failed', 'repeat': 1, 'runs': []}), 'assertion_failed'), (RuntimeError('injected startup failure'), 'transport_error'), (TimeoutError('injected deadline'), 'timeout'), (session.WorkerCleanupError('injected unconfirmed process exit'), 'transport_error')]:
            with self.subTest(expected=expected), patch.object(session, 'resolve_documents', return_value=self.root / 'Documents'), patch.object(session, 'require_idle_profile'), patch.object(session, 'check_dev_build', return_value={'status': 'passed'}), patch.object(session, 'validate_manifest', return_value=manifest), patch.object(session, 'revision', return_value={'revision': 'fixture', 'dirty': False, 'changes': []}), patch.object(session, 'supervise_worker', side_effect=outcome):
                result = session.run_managed_session(config, 'core-regression')
            self.assertEqual(result['status'], expected, result)
            self.assertTrue(result['baseline_unchanged'])
            if isinstance(outcome, session.WorkerCleanupError):
                self.assertFalse(result['cleanup']['processes_stopped'])
                self.assertFalse(result['cleanup']['profile']['restored'])
                self.assertIn(b'NO_AUTOSAVE', self.settings.read_bytes())
                self.assertTrue((self.user / '.asp-automation.lock').exists())
                # There is no actual child in this injected case; temporary test root cleanup owns it.
                continue
            self.assertTrue(result['cleanup']['profile']['restored'])
            self.assertTrue(result['cleanup']['files']['restored'])
            self.assertEqual(self.settings.read_bytes(), settings_before)
            self.assertEqual(self.dlc.read_bytes(), dlc_before)
            self.assertFalse((self.user / '.asp-automation.lock').exists())
            self.assertEqual(list((self.user / 'save games').iterdir()), [])
            self.assertEqual(json.loads(Path(result['report_json']).read_text())['status'], expected)
            self.assertIn('Status: ' + expected, Path(result['report_markdown']).read_text())

    def test_startup_failure_retains_exact_launched_pid_evidence(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from tools.game_runner.windows import WindowsBackend
        backend = WindowsBackend.__new__(WindowsBackend)
        backend.config = SimpleNamespace(game_executable=self.root / 'ck3.exe', startup_timeout=1)
        backend.process = None
        backend.started_pids = []
        backend.preflight = lambda: None
        backend.process_journal = self.root / 'game-processes.json'
        with patch('tools.game_runner.windows.subprocess.run', return_value=SimpleNamespace(stdout='')), patch('tools.game_runner.windows.subprocess.Popen', return_value=SimpleNamespace(pid=4242, poll=lambda: 1)):
            with self.assertRaises(RuntimeError):
                backend.start('owned.ck3')
        self.assertEqual(json.loads(backend.process_journal.read_text())['owned_pids'], [4242])

    def test_supervised_child_deadline_terminates_owned_child(self):
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            session.supervise_worker([sys.executable, '-c', 'import sys,time;sys.stdin.readline();time.sleep(30)'], self.root, 0.2)
        self.assertLess(time.monotonic() - started, 8)

    def test_supervised_child_normal_and_failure_exit(self):
        self.assertEqual(session.supervise_worker([sys.executable, '-c', 'import sys;sys.stdin.readline();print("done")'], self.root, 3), 'done\n')
        with self.assertRaises(RuntimeError):
            session.supervise_worker([sys.executable, '-c', 'import sys;sys.stdin.readline();sys.exit(3)'], self.root, 3)


if __name__ == '__main__':
    unittest.main()

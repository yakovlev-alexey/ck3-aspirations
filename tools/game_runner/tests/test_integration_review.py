"""Integration review failure boundaries; no native input or child processes."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools.game_runner import processes, session
from tools.game_runner.runner import Config
from tools.game_runner.tests import test_ui as ui_tests


class IntegrationReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def evidence(self):
        native = self.root / 'native'
        logs = native / 'logs-1'
        logs.mkdir(parents=True)
        measurement = {'session': 123, 'request': 2, 'counter': 0, 'date': 43000}
        (logs / 'debug.log').write_text('ASP_AUTOMATION|1|123|2|DONE|counter=0|date=43000\n')
        (logs / 'error.log').write_text('')
        (native / '123-2.json').write_text(json.dumps(measurement))
        result = {'status': 'passed', 'repeat': 1, 'evidence': str(native),
                  'runs': [{'index': 1, 'initial': measurement,
                            'assertions': [{'name': 'native', 'passed': True}], 'logs': str(logs)}]}
        (native / 'report.json').write_text(json.dumps(result))
        fixture = ui_tests.EvidenceTests.__new__(ui_tests.EvidenceTests)
        fixture.root = native
        screenshot = fixture.png('final.png', 1, 1)
        return result, screenshot

    def test_generic_required_png_rejects_fresh_header_only_with_other_evidence_matching(self):
        native, screenshot = self.evidence()
        started = time.time() - 1
        self.assertEqual(len(session.validate_evidence(native, started, self.root)), 5)
        screenshot.write_bytes(screenshot.read_bytes()[:24])
        self.assertEqual(screenshot.stat().st_size, 24)
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.root)

    def boundary(self):
        class Job:
            def assign(self, process):
                pass
            def close(self):
                raise RuntimeError('injected unconfirmed Job exit')
        process = SimpleNamespace(pid=4242, returncode=0,
                                  communicate=lambda *args, **kwargs: ('{}', ''), poll=lambda: 0)
        return Job, process

    def failing_audit(self):
        original = Path.write_text
        writes = []
        def write(path, text, *args, **kwargs):
            if path.name == 'process-ownership.json':
                writes.append(text)
                if len(writes) == 2:
                    raise OSError('injected final audit persistence failure')
            return original(path, text, *args, **kwargs)
        return write, writes

    def test_final_audit_failure_preserves_cleanup_safety_exception_and_both_causes(self):
        job, process = self.boundary()
        write, writes = self.failing_audit()
        with patch.object(processes, 'ProcessJob', job), patch.object(processes.subprocess, 'Popen', return_value=process), patch.object(Path, 'write_text', new=write):
            with self.assertRaises(processes.WorkerCleanupError) as caught:
                processes.supervise_worker(['fake'], self.root, 1, self.root / 'process-ownership.json')
        self.assertEqual(len(writes), 2)
        self.assertIn('unconfirmed Job exit', str(caught.exception))
        self.assertIn('audit persistence failure', str(caught.exception))
        self.assertFalse(json.loads(writes[-1])['processes_stopped'])

    def test_combined_cleanup_audit_failure_keeps_parent_profile_files_and_lock(self):
        repository = Path(session.__file__).resolve().parents[2]
        output = tempfile.TemporaryDirectory(dir=repository / '.local')
        self.addCleanup(output.cleanup)
        user = self.root / 'Documents/Paradox Interactive/Crusader Kings III'
        (user / 'save games').mkdir(parents=True)
        (user / 'mod').mkdir()
        settings = user / 'pdx_settings.txt'
        settings.write_bytes(b'"game"={"autosave"={value="YEARLY"}}\n')
        (user / 'dlc_load.json').write_bytes(b'{"enabled_mods":[],"disabled_dlcs":[]}\n')
        baseline = self.root / 'baseline.ck3'
        baseline.write_bytes(b'immutable')
        executable = self.root / 'ck3.exe'
        executable.write_bytes(b'never launched')
        config = Config(executable, user, baseline, Path(output.name))
        job, process = self.boundary()
        write, writes = self.failing_audit()
        with patch.object(session, 'resolve_documents', return_value=self.root / 'Documents'), patch.object(session, 'require_idle_profile'), patch.object(session, 'check_dev_build', return_value={'status': 'passed'}), patch.object(session, 'validate_manifest', return_value={}), patch.object(session, 'revision', return_value={'revision': 'fixture', 'dirty': False}), patch.object(processes, 'ProcessJob', job), patch.object(processes.subprocess, 'Popen', return_value=process), patch.object(Path, 'write_text', new=write), patch.object(session.ManagedProfile, 'restore', return_value={'restored': True}) as profile_restore, patch.object(session.ManagedFiles, 'restore', return_value={'restored': True}) as files_restore:
            result = session.run_managed_session(config, 'core-regression')
        self.assertEqual(len(writes), 2)
        self.assertEqual(result['status'], 'transport_error')
        self.assertFalse(result['cleanup']['processes_stopped'])
        self.assertFalse(result['cleanup']['profile']['restored'])
        self.assertFalse(result['cleanup']['files']['restored'])
        self.assertIn('audit persistence failure', result['error'])
        profile_restore.assert_not_called()
        files_restore.assert_not_called()
        self.assertIn(b'NO_AUTOSAVE', settings.read_bytes())
        self.assertTrue((user / '.asp-automation.lock').exists())
        self.assertEqual(len(list((user / 'save games').glob('asp_automation_*.ck3'))), 1)
        self.assertEqual(len(list((user / 'mod').iterdir())), 1)
        self.assertTrue((Path(result['report_json']).parent / 'backups').is_dir())
        self.assertEqual(baseline.read_bytes(), b'immutable')

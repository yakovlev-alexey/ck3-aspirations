"""Deterministic regressions for managed request/profile ownership and lifecycle evidence."""
import base64
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools.game_runner import profile, protocol, session
from tools.game_runner.runner import GameRunner


class ReviewBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.user = self.root / 'user'
        for name in ('save games', 'logs', 'mod'):
            (self.user / name).mkdir(parents=True)
        self.evidence = self.root / 'evidence'
        self.evidence.mkdir()
        self.baseline = self.root / 'baseline.ck3'
        self.baseline.write_bytes(b'pristine')
        self.settings = self.user / 'pdx_settings.txt'
        self.settings.write_bytes(b'"game"={"autosave"={value="YEARLY"}}\n')
        self.dlc = self.user / 'dlc_load.json'
        self.dlc.write_bytes(b'{"enabled_mods":[],"disabled_dlcs":[]}\n')

    def request_runner(self):
        config = SimpleNamespace(user_data=self.user, baseline_save=self.baseline, output_root=self.evidence, request_timeout=1)
        files = session.ManagedFiles(config, self.evidence)
        files.prepare()
        runner = GameRunner.__new__(GameRunner)
        runner.config = config
        runner.session, runner.request, runner.run_directory = 123, 0, None
        runner.request_root, runner.request_path, runner.request_journal = files.request.parent, files.request, files.journal
        calls = []
        runner.backend = SimpleNamespace(command=calls.append, started_pids=[])
        runner._wait = lambda *args, **kwargs: {'version': 1, 'session': runner.session, 'request': runner.request, 'kind': 'DONE', 'counter': 0, 'date': 43000}
        return files, runner, calls

    def assert_request_conflict(self, files, runner, calls, expected_calls):
        with self.assertRaises((RuntimeError, ValueError)):
            runner._send('observe')
        self.assertEqual(files.request.read_bytes(), b'external request')
        self.assertEqual(len(calls), expected_calls)
        audit = files.restore()
        self.assertFalse(audit['restored'])
        self.assertEqual(len(audit['conflicts']), 1)
        self.assertEqual(files.request.read_bytes(), b'external request')
        self.assertEqual(list((self.user / 'save games').iterdir()), [])

    def test_external_request_before_first_send_is_not_adopted(self):
        files, runner, calls = self.request_runner()
        files.request.write_bytes(b'external request')
        self.assert_request_conflict(files, runner, calls, 0)

    def test_external_request_between_sends_is_not_overwritten(self):
        files, runner, calls = self.request_runner()
        runner._send('observe')
        files.request.write_bytes(b'external request')
        self.assert_request_conflict(files, runner, calls, 1)

    def test_external_request_during_staging_is_preserved(self):
        files, runner, calls = self.request_runner()
        def external_write(fd):
            files.request.write_bytes(b'external request')
        with patch.object(protocol.os, 'fsync', side_effect=external_write):
            self.assert_request_conflict(files, runner, calls, 0)
        self.assertEqual(list(files.request.parent.glob('.asp-request-*')), [])

    def test_partial_write_for_each_profile_target_keeps_live_bytes_and_cleans_owned_stage(self):
        original_write = Path.write_bytes
        original_temporary = tempfile.NamedTemporaryFile
        expected = {self.settings: self.settings.read_bytes(), self.dlc: self.dlc.read_bytes()}
        sentinel = self.user / '.asp-profile-user-owned'
        sentinel.write_bytes(b'keep')
        for target in (self.settings, self.dlc):
            with self.subTest(target=target.name):
                for path, raw in expected.items():
                    path.write_bytes(raw)
                transaction = profile.ManagedProfile(self.user, self.root / 'build/mod', self.evidence / target.name)
                def partial_live(path, data):
                    if path.resolve() == target.resolve():
                        original_write(path, data[:8])
                        raise OSError('injected partial write')
                    return original_write(path, data)
                class PartialStream:
                    def __init__(self, stream):
                        self.stream = stream
                    def __enter__(self):
                        self.stream.__enter__()
                        return self
                    def __exit__(self, *args):
                        return self.stream.__exit__(*args)
                    def __getattr__(self, key):
                        return getattr(self.stream, key)
                    def write(self, data):
                        self.stream.write(data[:8])
                        self.stream.flush()
                        raise OSError('injected partial staging write')
                def partial_stage(*args, **kwargs):
                    stream = original_temporary(*args, **kwargs)
                    return PartialStream(stream) if target.name in kwargs.get('prefix', '') else stream
                with patch.object(Path, 'write_bytes', new=partial_live), patch.object(tempfile, 'NamedTemporaryFile', side_effect=partial_stage):
                    with self.assertRaises(OSError):
                        transaction.prepare()
                self.assertTrue(transaction.restore()['restored'])
                for path, raw in expected.items():
                    self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(sentinel.read_bytes(), b'keep')
                self.assertEqual({path.name for path in self.user.iterdir()}, {'save games', 'logs', 'mod', 'pdx_settings.txt', 'dlc_load.json', sentinel.name})
                self.assertEqual(list((self.user / 'mod').iterdir()), [])

    def lifecycle_evidence(self):
        native = self.evidence / 'native'
        logic, calendar = native / 'logs-1-logic', native / 'logs-1'
        logic.mkdir(parents=True)
        calendar.mkdir()
        run = {'index': 1, 'initial': {'session': 123, 'request': 2, 'date': 43000}, 'lifecycle': {'session': 123, 'request': 3, 'date': 43000, 'p01': 1}, 'reload_precondition': {'session': 456, 'request': 3, 'date': 43000, 'reload_identity': 1}, 'calendar_setup': {'session': 456, 'request': 2, 'date': 43000}, 'calendar_day': {'session': 456, 'request': 4, 'date': 43001}, 'calendar': {'session': 456, 'request': 5, 'date': 43001, 'calendar_reviews': 2}, 'logic_logs': str(logic), 'logs': str(calendar), 'assertions': [{'name': 'native_lifecycle_and_calendar', 'passed': True}]}
        run['duplicate'] = dict(run['lifecycle'])
        run['calendar_duplicate'] = dict(run['calendar'])
        for directory, identity in ((logic, 123), (calendar, 456)):
            measurements = [value for value in run.values() if isinstance(value, dict) and value.get('session') == identity]
            (directory / 'debug.log').write_text(''.join(f"ASP_AUTOMATION|1|{identity}|{value['request']}|DONE|date={value['date']}\n" for value in measurements))
            (directory / 'error.log').write_text('')
            for value in measurements:
                (native / f"{identity}-{value['request']}.json").write_text(json.dumps(value))
        (native / 'final.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGMQcYsCAAEmALW1sxutAAAAAElFTkSuQmCC'))
        result = {'status': 'passed', 'scenario': 'lifecycle-regression', 'repeat': 1, 'evidence': str(native), 'runs': [run]}
        (native / 'report.json').write_text(json.dumps(result))
        return result, logic, calendar

    def test_lifecycle_evidence_retains_both_exact_sessions_and_intervals(self):
        native, logic, calendar = self.lifecycle_evidence()
        files = session.validate_evidence(native, time.time() - 1, self.evidence)
        names = {value['path'] for value in files}
        for directory in (logic, calendar):
            for name in ('debug.log', 'error.log'):
                self.assertIn(str((directory / name).relative_to(self.evidence)), names)
        self.assertIn(str((logic.parent / '123-3.json').relative_to(self.evidence)), names)
        self.assertIn(str((logic.parent / '456-5.json').relative_to(self.evidence)), names)

    def test_missing_or_stale_logic_interval_cannot_pass_lifecycle(self):
        native, logic, calendar = self.lifecycle_evidence()
        started = time.time() - 1
        original = (logic / 'debug.log').read_bytes()
        (logic / 'debug.log').unlink()
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.evidence)
        (logic / 'debug.log').write_bytes(original)
        os.utime(logic / 'error.log', (started - 5, started - 5))
        with self.assertRaises(ValueError):
            session.validate_evidence(native, started, self.evidence)

    def test_calendar_measurement_cannot_borrow_another_request_identity(self):
        native, logic, calendar = self.lifecycle_evidence()
        native['runs'][0]['calendar']['session'] = 789
        (logic.parent / 'report.json').write_text(json.dumps(native))
        with self.assertRaises(ValueError):
            session.validate_evidence(native, time.time() - 1, self.evidence)


if __name__ == '__main__':
    unittest.main()

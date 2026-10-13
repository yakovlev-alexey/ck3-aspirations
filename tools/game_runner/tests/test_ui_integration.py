"""UI transport rejects incomplete telemetry and protects owned save recovery."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from tools.game_runner.protocol import Telemetry, ProtocolError
from tools.game_runner.ui import UI_FIELDS
from tools.game_runner.session import ManagedFiles


class UIIntegrationTests(unittest.TestCase):
    def record(self, values):
        return ('ASP_AUTOMATION|1|123|2|DONE|counter=0|date=43000|' + '|'.join(key + '=' + str(value) for key, value in values.items()) + '\n').encode()

    def test_ui_telemetry_keeps_every_native_measurement(self):
        values = {key: 0 for key in UI_FIELDS}
        parsed = Telemetry(123, 2, operation='ui_assert').feed(self.record(values))[0]
        self.assertEqual({key: parsed[key] for key in UI_FIELDS}, values)
        incomplete = dict(values)
        del incomplete['second_identity']
        with self.assertRaises(ProtocolError):
            Telemetry(123, 2, operation='ui_assert').feed(self.record(incomplete))

    def test_owned_ui_save_is_restored_after_worker_exit_but_external_bytes_survive(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            user = root / 'user'
            (user / 'save games').mkdir(parents=True)
            evidence = root / 'evidence'
            evidence.mkdir()
            baseline = root / 'baseline.ck3'
            baseline.write_bytes(b'pristine')
            config = SimpleNamespace(user_data=user, baseline_save=baseline)
            owned = user / 'save games/asp_ui_0123456789abcdef.ck3'
            owned.write_bytes(b'actual UI save')
            journal = evidence / 'ui-save-ownership.json'
            record = {'path': str(owned), 'sha256': hashlib.sha256(owned.read_bytes()).hexdigest()}
            journal.write_text(json.dumps({'saves': [record]}))
            files = ManagedFiles(config, evidence)
            self.assertTrue(files.restore()['restored'])
            self.assertFalse(owned.exists())
            owned.write_bytes(b'external change')
            files = ManagedFiles(config, evidence)
            self.assertFalse(files.restore()['restored'])
            self.assertEqual(owned.read_bytes(), b'external change')

    def test_ui_save_journal_cannot_delete_outside_or_unowned_save(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            user = root / 'user'
            (user / 'save games').mkdir(parents=True)
            evidence = root / 'evidence'
            evidence.mkdir()
            sentinel = root / 'user/save games/user-campaign.ck3'
            sentinel.write_bytes(b'keep')
            (evidence / 'ui-save-ownership.json').write_text(json.dumps({'saves': [{'path': str(sentinel), 'sha256': '0' * 64}]}))
            files = ManagedFiles(SimpleNamespace(user_data=user), evidence)
            self.assertFalse(files.restore()['restored'])
            self.assertEqual(sentinel.read_bytes(), b'keep')

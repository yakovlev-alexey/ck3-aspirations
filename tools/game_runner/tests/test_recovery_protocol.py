"""Recovery results require every native measurement and exact request identity."""
import unittest
from tools.game_runner.protocol import Telemetry, ProtocolError, RECOVERY_FIELDS

FIELDS = RECOVERY_FIELDS

class RecoveryProtocolTests(unittest.TestCase):
    def message(self, drop=None):
        fields = '|'.join(f'{name}=0' for name in FIELDS if name != drop)
        return f'ASP_AUTOMATION|1|73102000|3|DONE|counter=0|date=430243|{fields}\n'.encode()

    def test_complete_recovery_native_result_is_accepted(self):
        parser = Telemetry(73102000, 3, operation='recovery_regression')
        parser.feed(self.message())
        self.assertEqual(parser.terminal['origin_control'], 0)

    def test_missing_attribution_measurement_cannot_pass(self):
        with self.assertRaises(ProtocolError):
            Telemetry(73102000, 3, operation='recovery_regression').feed(self.message('foreign'))

    def test_wrong_request_is_ignored(self):
        parser = Telemetry(73102000, 4, operation='recovery_regression')
        parser.feed(self.message())
        self.assertIsNone(parser.terminal)

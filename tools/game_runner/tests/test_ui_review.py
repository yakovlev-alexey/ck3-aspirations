"""Review regressions with real save files and simulated native input boundaries."""
import dataclasses
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools.game_runner.session import ManagedFiles
from tools.game_runner.tests.test_ui import measured
from tools.game_runner.ui import UIError, WindowGeometry
from tools.game_runner.ui_scenario import NativeUIOperations
from tools.game_runner.windows import WindowsBackend


class SaveReloadReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.user = self.root / 'user'
        (self.user / 'save games').mkdir(parents=True)
        self.evidence = self.root / 'evidence'
        self.evidence.mkdir()
        self.before = measured() | {'session': 123, 'date': 43000}
        self.reloaded = measured() | {'session': 456, 'date': 43000}
        self.opened = dict(self.reloaded)
        self.events = []
        self.now = 0
        self.candidate = self.user / 'save games/asp_ui_0123456789abcdef.ck3'
        self.backend = SimpleNamespace(
            geometry=lambda: WindowGeometry(42, 100, 120, 2560, 1440, 2560, 1440, 0, 0),
            preflight=lambda: {'GUI': {'scale': {'value': '1.3'}}, 'game': {'cloud_save': {'enabled': 'no'}}},
            open_console=lambda: self.events.append('console'),
            key=lambda vk: None, replace_text=lambda name: None,
            stop=lambda: self.events.append('stop'))
        self.runner = SimpleNamespace(
            backend=self.backend, config=SimpleNamespace(user_data=self.user, request_timeout=1),
            request_journal=self.evidence / 'request-ownership.json',
            baseline_hash=hashlib.sha256(b'baseline').hexdigest(),
            _directory=lambda: self.evidence, clock=lambda: self.now, sleep=self.advance,
            launch_save=self.root / 'original.ck3', session=123,
            _start=lambda: self.events.append('start'), _send=self.send)
        self.operations = NativeUIOperations(self.runner, 1)
        self.operations.capture = lambda stage: self.events.append(stage)
        self.operations.click = self.click
        token = patch('tools.game_runner.ui_scenario.secrets.token_hex', return_value='0123456789abcdef')
        token.start()
        self.addCleanup(token.stop)

    def advance(self, delay):
        self.now += delay

    def send(self, operation):
        return dict(self.reloaded if operation == 'ui_reload_assert' else self.opened)

    def click(self, x, y):
        self.events.append((x, y))
        if (x, y) == (1395, 1154):
            self.candidate.write_bytes(b'actual native save')

    def entry(self):
        return json.loads((self.evidence / 'ui-save-ownership.json').read_text())['saves'][0]

    def restore(self):
        return ManagedFiles(self.runner.config, self.evidence).restore()

    def test_foreign_save_created_while_typing_survives_cleanup_without_save_click(self):
        self.backend.replace_text = lambda name: self.candidate.write_bytes(b'foreign campaign')
        self.operations.click = lambda x, y: self.events.append((x, y))
        with self.assertRaises(UIError):
            self.operations.save_campaign()
        self.assertNotIn((1395, 1154), self.events)
        self.assertIsNone(self.entry()['sha256'])
        audit = self.restore()
        self.assertFalse(audit['restored'])
        self.assertTrue(audit['conflicts'])
        self.assertEqual(self.candidate.read_bytes(), b'foreign campaign')

    def test_stable_save_has_no_delete_authority_until_validated_reload(self):
        candidate, saved = self.operations.save_campaign()
        self.assertEqual(saved['sha256'], hashlib.sha256(candidate.read_bytes()).hexdigest())
        self.assertIsNone(self.entry()['sha256'])
        self.assertFalse(self.restore()['restored'])
        self.assertEqual(candidate.read_bytes(), b'actual native save')

    def test_foreign_bytes_at_noop_save_and_rejected_reload_are_retained(self):
        def noop_save(x, y):
            if (x, y) == (1395, 1154):
                self.candidate.write_bytes(b'foreign campaign')
        self.operations.click = noop_save
        candidate, saved = self.operations.save_campaign()
        self.reloaded['second_identity'] = 0
        with self.assertRaises(UIError):
            self.operations.reload_campaign(candidate, self.before)
        self.assertIsNone(self.entry()['sha256'])
        self.assertFalse(self.restore()['restored'])
        self.assertEqual(candidate.read_bytes(), b'foreign campaign')

    def test_reopened_selector_must_keep_binding_ids_and_immutable_state_before_input(self):
        candidate, saved = self.operations.save_campaign()
        for change in ({'choice_second': 0}, {'second_id': 99}, {'first_identity': 0},
                       {'deadline_days': 1824}, {'review_delta': 1}, {'stress_delta': 10}):
            with self.subTest(change=change):
                self.events.clear()
                self.opened = self.reloaded | change
                with self.assertRaises(UIError):
                    self.operations.reload_campaign(candidate, self.before)
                self.assertNotIn('console', self.events)
                self.assertNotIn('reload-selector', self.events)
                self.assertNotIn((1750, 1077), self.events)
                self.assertIsNone(self.entry()['sha256'])
        self.assertFalse(self.restore()['restored'])
        self.assertEqual(candidate.read_bytes(), b'actual native save')

    def test_changed_save_before_reload_is_retained_without_starting_game(self):
        candidate, saved = self.operations.save_campaign()
        candidate.write_bytes(b'external replacement')
        self.events.clear()
        with self.assertRaises(UIError):
            self.operations.reload_campaign(candidate, self.before)
        self.assertNotIn('start', self.events)
        self.assertFalse(self.restore()['restored'])
        self.assertEqual(candidate.read_bytes(), b'external replacement')

    def test_changed_save_during_reload_never_acquires_delete_authority(self):
        candidate, saved = self.operations.save_campaign()
        self.runner._start = lambda: candidate.write_bytes(b'external replacement')
        with self.assertRaises(UIError):
            self.operations.reload_campaign(candidate, self.before)
        self.assertIsNone(self.entry()['sha256'])
        self.assertFalse(self.restore()['restored'])
        self.assertEqual(candidate.read_bytes(), b'external replacement')

    def test_validated_reload_grants_cleanup_only_for_the_original_saved_bytes(self):
        candidate, saved = self.operations.save_campaign()
        reloaded, opened = self.operations.reload_campaign(candidate, self.before)
        self.assertEqual(reloaded, self.reloaded)
        self.assertEqual(opened, self.opened)
        self.assertEqual(self.entry()['sha256'], saved['sha256'])
        self.assertTrue(self.restore()['restored'])
        self.assertFalse(candidate.exists())


class SettledGeometryReviewTests(unittest.TestCase):
    def test_geometry_change_during_settle_never_dispatches_button_down(self):
        original = WindowGeometry(42, 100, 120, 2560, 1440, 2560, 1440, 0, 0)
        for change in ({'screen_x': 10}, {'client_width': 2048, 'client_height': 1152}, {'dpi': 144}):
            with self.subTest(change=change):
                state = {'geometry': original}
                buttons = []
                backend = WindowsBackend.__new__(WindowsBackend)
                backend.user32 = SimpleNamespace(SetCursorPos=lambda *point: True)
                backend.validate = lambda: None
                backend.geometry = lambda: state['geometry']
                backend._mouse_input = lambda flags, release=False: buttons.append(flags)
                with patch('tools.game_runner.windows.time.sleep', side_effect=lambda seconds: state.update(geometry=dataclasses.replace(original, **change))):
                    with self.assertRaises(UIError):
                        backend.click_image(original, 100, 100)
                self.assertEqual(buttons, [])

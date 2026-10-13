"""Real runner/transport/evidence with only slow Windows/CK3 boundary simulated."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools.game_runner.tests import test_runner as base
from tools.game_runner.tests import test_ui as ui_tests
from tools.game_runner.ui import UI_FIELDS, WindowGeometry
from tools.game_runner.evidence import validate_evidence
from tools.game_runner.session import ManagedFiles
from tools.game_runner.windows import WindowsBackend, FocusError


class UIBoundary(base.NativeIOBoundary):
    def __init__(self, config):
        super().__init__(config)
        self.actual = None
        self.selected = 0
        self.wrong = False
        self.omit = None
        self.generation = 0
    def preflight(self):
        return {'GUI': {'scale': {'value': '1.3'}}, 'game': {'cloud_save': {'enabled': 'no'}}}
    def geometry(self):
        self.validate()
        return WindowGeometry(42 + self.generation, 100 + self.generation, 120, 2560, 1440, 2560, 1440, 0, 0)
    def start(self, save_name):
        super().start(save_name)
        self.generation += 1
        (self.config.user_data / 'logs/error.log').write_text('')
        if save_name.startswith('asp_ui_'):
            self.actual = json.loads((self.config.user_data / 'save games' / save_name).read_text())
    def command(self, command):
        raw = (self.config.user_data / 'run/asp_automation_request.txt').read_text(encoding='utf-8-sig')
        op = re.search(r'OP = (\w+)', raw)
        if not op or not op[1].startswith('ui_'):
            return super().command(command)
        session = int(re.search(r'SESSION = (\d+)', raw)[1]); request = int(re.search(r'REQUEST = (\d+)', raw)[1])
        log = self.config.user_data / 'logs/debug.log'
        if self.cached and self.cached[:2] == (session, request):
            with log.open('ab') as stream: stream.write(self.cached[2])
            return
        if op[1] == 'ui_setup':
            self.actual = ui_tests.measured() | dict(selected_id=0, declared_count=0, second_declared=0, deadline_days=0, choice_second=0, eligible_count=2)
        if op[1] == 'ui_open': self.actual['choice_second'] = 1
        values = dict(self.actual)
        values.pop(self.omit, None)
        data = (f'ASP_AUTOMATION|1|{session}|{request}|DONE|counter=0|date=43000|' + '|'.join(f'{key}={value}' for key, value in values.items()) + '\n').encode()
        with log.open('ab') as stream: stream.write(data)
        self.cached = session, request, data
    def click_image(self, geometry, x, y):
        geometry.require_unchanged(self.geometry())
        geometry.image_to_screen(x, y)
        if (x,y) == (1750,1077): self.selected = 11 if self.wrong else 12
        if (x,y) == (920,990):
            self.actual.update(selected_id=self.selected, declared_count=1, first_declared=int(self.selected == 11), second_declared=int(self.selected == 12), deadline_days=1825, eligible_count=1)
        if (x,y) == (1395,1154):
            path = self.config.user_data / 'save games' / (self.name + '.ck3')
            with path.open('x') as stream: json.dump(self.actual, stream)
    def key(self, vk): pass
    def replace_text(self, name): self.name = name
    def screenshot(self, path):
        if 'save-dialog' in path.name and getattr(self, 'missing_frame', False): return
        fixture = ui_tests.EvidenceTests.__new__(ui_tests.EvidenceTests)
        fixture.root = Path(path).parent
        fixture.png(Path(path).name,2560,1440)


class UISequenceTests(unittest.TestCase):
    def setUp(self):
        base.RunnerIOTests.setUp(self)
        self.backend = UIBoundary(self.config)
        self.runner.backend = self.backend
        self.config.request_timeout = 1
        self.files = ManagedFiles(self.config, self.root / 'managed')
        self.files.directory.mkdir()
        self.files.prepare()
        self.runner.request_journal = self.files.journal
        self.started = __import__('time').time() - 1
    def tearDown(self):
        self.runner.close()
        self.files.restore()
        self.temporary.cleanup()
    def test_unmanaged_ui_rejected_before_game_or_input_resources(self):
        del self.runner.request_journal
        report = self.runner.run_scenario('ui-regression')
        self.assertEqual(report['status'], 'assertion_failed')
        self.assertIn('managed', report['error'])
        self.assertIsNone(self.runner.launch_save)
        self.assertFalse(self.runner.guard.owned)
        self.assertFalse(self.runner.request_path.exists())

    def test_real_runner_sequence_retains_exact_reload_state_and_all_evidence(self):
        report = self.runner.run_scenario('ui-regression')
        self.assertEqual(report['status'], 'passed', report.get('error'))
        run = report['runs'][0]
        self.assertNotEqual(run['ui_declared']['session'], run['ui_reloaded']['session'])
        self.assertEqual(run['ui_declared']['selected_id'],12)
        self.assertEqual(run['ui_reloaded']['selected_id'],12)
        files = validate_evidence(report,self.started,self.config.output_root)
        self.assertEqual(len([entry for entry in files if entry['path'].endswith('.png')]),11)
        self.assertTrue(self.files.restore()['restored'])
        self.assertFalse(Path(run['ui_save']['path']).exists())
    def test_wrong_story_declaration_is_assertion_failure_before_save(self):
        self.backend.wrong = True
        result = self.runner.run_scenario('ui-regression')
        self.assertEqual(result['status'],'assertion_failed')
        self.assertIn('selected_id',result['error'])
        self.assertEqual(list((self.root / 'save games').glob('asp_ui_*')),[])
    def test_missing_frame_cannot_be_counted_as_ui_success(self):
        self.backend.missing_frame = True
        result = self.runner.run_scenario('ui-regression')
        self.assertEqual(result['status'],'assertion_failed')
        self.assertIn('screenshot',result['error'])
    def test_parent_evidence_rejects_missing_second_session_logs_or_saved_bytes(self):
        result = self.runner.run_scenario('ui-regression')
        self.assertEqual(result['status'],'passed',result.get('error'))
        run = result['runs'][0]
        (Path(run['logs']) / 'debug.log').unlink()
        with self.assertRaises(ValueError): validate_evidence(result,self.started,self.config.output_root)
    def test_parent_evidence_rejects_missing_stage_or_changed_save(self):
        result = self.runner.run_scenario('ui-regression')
        self.assertEqual(result['status'],'passed',result.get('error'))
        run = result['runs'][0]
        Path(run['ui_save']['evidence_path']).write_bytes(b'changed')
        with self.assertRaises(ValueError): validate_evidence(result,self.started,self.config.output_root)


class MouseSafetyTests(unittest.TestCase):
    def test_pointer_move_settles_and_rechecks_ownership_before_button_down(self):
        events = []
        class Backend(WindowsBackend):
            def __init__(self):
                self.user32 = SimpleNamespace(SetCursorPos=lambda *point: self.move(*point))
            def move(self, *point):
                events.append(('move', point))
                return True
            def geometry(self):
                return WindowGeometry(42,100,96,1920,1080,1920,1080,10,25)
            def validate(self): events.append('validate')
            def _mouse_input(self, flags, release=False):
                events.append(('button', flags))
        backend = Backend()
        with patch('tools.game_runner.windows.time.sleep', side_effect=lambda seconds: events.append('settle')):
            backend.click_image(backend.geometry(),100,100)
        press = events.index(('button',2))
        self.assertEqual(events[press-3:press], [('move',(110,125)), 'settle', 'validate'])

    def test_foreground_loss_during_pointer_settle_cannot_press_mouse(self):
        class Backend(WindowsBackend):
            def __init__(self):
                self.lost = False
                self.buttons = []
                self.user32 = SimpleNamespace(SetCursorPos=lambda *point: True)
            def geometry(self): return WindowGeometry(42,100,96,1920,1080,1920,1080,0,0)
            def validate(self):
                if self.lost: raise FocusError('Lost foreground during pointer settle')
            def _mouse_input(self, flags, release=False): self.buttons.append(flags)
        backend = Backend()
        with patch('tools.game_runner.windows.time.sleep', side_effect=lambda seconds: setattr(backend,'lost',True)):
            with self.assertRaises(FocusError): backend.click_image(backend.geometry(),100,100)
        self.assertEqual(backend.buttons, [])

    def test_lost_foreground_after_down_releases_owned_mouse_button(self):
        class Backend(WindowsBackend):
            def __init__(self):
                self.held = False
                self.user32 = SimpleNamespace(SetCursorPos=lambda *args: True)
            def geometry(self): return WindowGeometry(42,100,96,1920,1080,1920,1080,0,0)
            def validate(self):
                if self.held: raise FocusError('Lost foreground after owned down')
            def _mouse_input(self, flags, release=False):
                if flags == 2: self.held = True
                if flags == 4 and release: self.held = False
        backend=Backend()
        with self.assertRaises(FocusError): backend.click_image(backend.geometry(),100,100)
        self.assertFalse(backend.held)

class FocusActivationTests(unittest.TestCase):
    def test_owned_window_activation_waits_for_foreground_without_sending_input(self):
        class API:
            def SetForegroundWindow(self, hwnd): self.requested = hwnd; return True
            def GetForegroundWindow(self): return self.requested
        backend = WindowsBackend.__new__(WindowsBackend)
        backend.user32 = API()
        backend.hwnd = 42
        calls = []
        backend.validate = lambda: calls.append('validate')
        backend._focus_owned_window()
        self.assertEqual(calls, ['validate'])

class ReadyWindowTests(unittest.TestCase):
    def test_ready_reselects_the_loaded_owned_window_before_activation(self):
        backend = WindowsBackend.__new__(WindowsBackend)
        backend.hwnd = 42
        backend._owned_window = lambda: 77
        activated = []
        backend._focus_owned_window = lambda: activated.append(backend.hwnd)
        backend.ready()
        self.assertEqual(activated, [77])
        self.assertEqual(backend.hwnd, 77)

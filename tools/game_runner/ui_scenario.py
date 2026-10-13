"""Registered deterministic native UI sequence; no arbitrary click/script API."""
import hashlib
import json
import secrets
import shutil
import time
from pathlib import Path
from .protocol import safe_path
from .ui import UIError, UI_FIELDS, validate_setup, validate_declaration, validate_reload, validate_frame, wait_for_saved_campaign


class NativeUIOperations:
    """Named operations measured on CK3 1.20.1, 2560x1440, GUI scale1.3.

    Intermediate captures document input; only exact native postconditions certify
    selection/declaration. Unsupported layout/profile fails before mouse input.
    """
    def __init__(self, runner, index):
        self.runner, self.backend, self.index = runner, runner.backend, index
        self.frames = []
        self.directory = runner._directory()
        self.refresh_geometry()

    def refresh_geometry(self):
        geometry = self.backend.geometry()
        settings = self.backend.preflight()
        try:
            scale = settings['GUI']['scale']['value']
            cloud = settings['game']['cloud_save']['enabled']
        except (KeyError, TypeError) as error:
            raise UIError('Missing supported GUI/local-save profile') from error
        if (geometry.image_width, geometry.image_height) != (2560, 1440) or scale != '1.3' or cloud != 'no':
            raise UIError('UI scenario requires 2560x1440 client, GUI scale1.3 and local cloud_save=no')
        self.geometry = geometry

    def capture(self, operation):
        self.runner.sleep(0.8)  # Native event-window show animation is0.7s.
        started = time.time()
        path = self.directory / f'ui-{self.index}-{operation}.png'
        self.geometry.require_unchanged(self.backend.geometry())
        self.backend.screenshot(path)
        frame = validate_frame(path, self.directory, self.geometry, started, operation)
        self.frames.append(frame)
        (self.directory / f'ui-frames-{self.index}.json').write_text(json.dumps(self.frames, indent=2) + '\n', encoding='utf-8')
        return frame

    def click(self, x, y):
        self.backend.click_image(self.geometry, x, y)
        self.runner.sleep(0.8)

    def open_aspirations(self, setup):
        opened = self.runner._send('ui_open')
        values = {key: opened[key] for key in UI_FIELDS}
        validate_setup(values, opened=True)
        if (opened['first_id'], opened['second_id']) != (setup['first_id'], setup['second_id']):
            raise UIError('Selector substituted the prepared Story identities')
        self.backend.open_console()  # Toggle the known open console closed.
        self.capture('open-aspirations')
        return opened

    def select_story(self, expected_story_id, opened):
        if expected_story_id != opened['second_id'] or opened['choice_second'] != 1:
            raise UIError('Requested Story is not the exact captured second selector entry')
        self.click(1750, 1077)
        self.capture('select-story')

    def declare_goal(self, first_id, second_id):
        self.click(1750, 1023)
        self.capture('declare-confirmation')
        # Native default character-event confirmation, first of two options.
        self.click(920, 990)
        self.capture('declare-result')
        self.backend.open_console()
        declared = self.runner._send('ui_assert')
        validate_declaration(first_id, second_id, {key: declared[key] for key in UI_FIELDS})
        return declared

    def save_campaign(self):
        save_root = safe_path(self.runner.config.user_data / 'save games')
        candidate = safe_path(save_root / ('asp_ui_' + secrets.token_hex(8) + '.ck3'))
        if candidate.exists():
            raise UIError('Disposable UI save name collided; no overwrite authorized')
        journal = self.runner.request_journal.parent / 'ui-save-ownership.json'
        entries = json.loads(journal.read_text(encoding='utf-8'))['saves'] if journal.exists() else []
        entry = {'path': str(candidate), 'sha256': None}
        entries.append(entry)
        journal.write_text(json.dumps({'saves': entries}), encoding='utf-8')
        self.backend.open_console()
        self.backend.key(0x1B)
        self.capture('save-menu')
        self.click(500, 612)
        self.capture('save-dialog')
        self.backend.replace_text(candidate.stem)
        self.capture('save-name')
        self.click(1395, 1154)
        saved = wait_for_saved_campaign(candidate, self.runner.baseline_hash, self.runner.config.request_timeout, clock=self.runner.clock, sleep=self.runner.sleep)
        entry['sha256'] = saved['sha256']
        journal.write_text(json.dumps({'saves': entries}), encoding='utf-8')
        retained = self.directory / f'ui-campaign-{self.index}.ck3'
        shutil.copyfile(candidate, retained)
        if hashlib.sha256(retained.read_bytes()).hexdigest() != saved['sha256']:
            raise UIError('Retained UI save bytes disagree with actual native save')
        self.capture('save-result')
        return candidate, saved | {'evidence_path': str(retained)}

    def reload_campaign(self, candidate, before):
        original = self.runner.launch_save
        self.backend.stop()
        self.runner.session = None
        self.runner.launch_save = candidate
        try:
            self.runner._start()  # New identity, actual saved filename, no setup.
        finally:
            self.runner.launch_save = original
        self.refresh_geometry()
        reloaded = self.runner._send('ui_reload_assert')
        validate_reload({key: before[key] for key in UI_FIELDS}, {key: reloaded[key] for key in UI_FIELDS})
        if reloaded['session'] == before['session'] or reloaded['date'] != before['date']:
            raise UIError('Reload did not use a fresh session at the saved native date')
        opened = self.runner._send('ui_open')
        self.backend.open_console()
        self.capture('reload-selector')
        self.click(1750, 1077)
        self.capture('reload-story')
        return reloaded, opened


def run_ui_sequence(runner, initial, index):
    if not hasattr(runner, 'request_journal'):
        raise UIError('ui-regression requires the managed session ownership workflow')
    operations = NativeUIOperations(runner, index)
    setup = runner._send('ui_setup')
    validate_setup({key: setup[key] for key in UI_FIELDS})
    opened = operations.open_aspirations(setup)
    operations.select_story(setup['second_id'], opened)
    declared = operations.declare_goal(setup['first_id'], setup['second_id'])
    duplicate = runner._send('ui_assert', replay=True)
    if duplicate != declared:
        raise UIError('UI declaration measurement replay changed')
    candidate, saved = operations.save_campaign()
    declaration_logs = runner._snapshot_logs(f'{index}-ui-declaration')
    reloaded, reopened = operations.reload_campaign(candidate, declared)
    logs = runner._snapshot_logs(index)
    final = runner._directory() / 'final.png'
    shutil.copyfile(operations.directory / f'ui-{index}-reload-story.png', final)
    return {'index': index, 'initial': initial, 'ui_setup': setup, 'ui_open': opened,
            'ui_declared': declared, 'ui_duplicate': duplicate, 'ui_reloaded': reloaded,
            'ui_reopened': reopened, 'ui_declaration_logs': declaration_logs, 'logs': logs,
            'ui_frames': operations.frames, 'ui_save': saved,
            'assertions': [{'name': name, 'passed': True} for name in (
                'native_two_eligible_distinct_story_setup', 'native_selector_exact_second_reference',
                'actual_second_story_declaration_other_unchanged', 'native_declaration_replay',
                'actual_new_native_save', 'actual_reload_exact_identity_and_pledge',
                'fresh_reload_session_same_native_date', 'fresh_required_ui_frames',
                'baseline_unchanged')]}

from pathlib import Path
import unittest
class BondLocalizationTests(unittest.TestCase):
    def test_all_bond_strings_are_single_native_lines(self):
        root=Path(__file__).resolve().parents[3]
        path=root/'src/stories/personal_bond/game/localization/english/asp_personal_bond_l_english.yml'
        data=path.read_bytes();self.assertTrue(data.startswith(b'\xef\xbb\xbf'));self.assertNotIn(b'\xef\xbb\xbf',data[3:])
        lines=data.decode('utf-8-sig').splitlines()
        self.assertEqual(lines[0],'l_english:')
        for line in lines[1:]:
            self.assertRegex(line,r'^ asp_(bond_[a-z_]+|personal_bond_story(_desc)?):0 ".*"$')
        values={line.split(':0 ',1)[0].strip():line.split(':0 ',1)[1] for line in lines[1:]}
        for connection in ('court','relation'):
            self.assertIn(r'\n\nOnly a new Friend or Best Friend',values[f'asp_bond_origin_{connection}_friendship'])
            self.assertIn(r'\n\nOnly a new Lover or Soulmate',values[f'asp_bond_origin_{connection}_romance'])
        for mode in ('friendship','romance'):
            self.assertIn(r'\n\nPrivate desire.',values[f'asp_bond_management_{mode}'])

    def test_origin_and_rival_cost_do_not_depend_on_management_scope(self):
        root=Path(__file__).resolve().parents[3]
        events=(root/'src/stories/personal_bond/game/events/asp_personal_bond_events.txt').read_text(encoding='utf-8-sig')
        loc=(root/'src/stories/personal_bond/game/localization/english/asp_personal_bond_l_english.yml').read_text(encoding='utf-8-sig')
        self.assertNotIn('custom_tooltip = asp_abandon_cost',events)
        self.assertEqual(events.count('custom_tooltip = asp_bond_release_cost'),2)
        value=next(line for line in loc.splitlines() if line.startswith(' asp_bond_release_cost:'))
        self.assertNotIn('asp_selected_story',value)
        self.assertNotIn('asp_bond_event_story',value)
        self.assertIn('asp_desire_abandonment_stress',value)
        self.assertIn('modifiers apply',value)
        self.assertIn('From 24 months',value)

    def test_origin_and_rival_have_native_unconditional_fallback(self):
        root=Path(__file__).resolve().parents[3]
        events=(root/'src/stories/personal_bond/game/events/asp_personal_bond_events.txt').read_text(encoding='utf-8-sig')
        self.assertEqual(events.count('option = { name = asp_close fallback = yes }'),2)

    def test_touched_native_scripts_preserve_exactly_one_bom(self):
        root = Path(__file__).resolve().parents[3]
        paths = list((root / 'src/stories/personal_bond').rglob('*.txt'))
        paths.extend(root / name for name in (
            'src/core/game/common/on_action/asp_core.txt',
            'src/core/game/common/script_values/asp_core.txt',
            'src/core/game/common/scripted_effects/asp_dispatch.txt',
            'src/core/game/common/scripted_triggers/asp_core.txt',
            'src/core/game/events/asp_management_events.txt',
            'src/core/tests/game/common/scripted_effects/asp_automation_debug.txt',
        ))
        for path in paths:
            with self.subTest(path=path.relative_to(root)):
                data = path.read_bytes()
                self.assertTrue(data.startswith(b'\xef\xbb\xbf'))
                self.assertNotIn(b'\xef\xbb\xbf', data[3:])

    def test_visible_native_story_has_implicit_name_and_description(self):
        root = Path(__file__).resolve().parents[3]
        text = (root / 'src/stories/personal_bond/game/localization/english/asp_personal_bond_l_english.yml').read_text(encoding='utf-8-sig')
        keys = {line.split(':0 ', 1)[0].strip() for line in text.splitlines()[1:]}
        self.assertIn('asp_personal_bond_story', keys)
        self.assertIn('asp_personal_bond_story_desc', keys)

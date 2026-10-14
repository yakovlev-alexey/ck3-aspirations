import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]


def native_block(text, marker):
    """Return one native block, including nested conditional display branches."""
    start = text.index("{", text.index(marker))
    depth = 1
    end = start + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start + 1:end - 1]


class IntegratedLocalizationTests(unittest.TestCase):
    def test_card_uses_selected_native_mode(self):
        text=(ROOT/'src/stories/personal_bond/game/localization/english/asp_personal_bond_l_english.yml').read_text(encoding='utf-8-sig')
        self.assertIn("[Story.Custom('asp_bond_story_mode')]",text)
        self.assertIn('asp_bond_story_friendship:',text)
        self.assertIn('asp_bond_story_romance:',text)
        branch=(ROOT/'src/stories/personal_bond/game/common/customizable_localization/asp_personal_bond.txt').read_text(encoding='utf-8-sig')
        self.assertIn('var:asp_interpretation = flag:romance',branch)

    def test_terminal_summaries_cannot_replay_settled_effects(self):
        cases = (
            ('src/stories/vengeance/game/events/asp_vengeance_events.txt', 'asp_vengeance.2', 'asp_vengeance_event_outcome'),
            ('src/stories/holding_recovery/game/events/asp_recovery_events.txt', 'asp_holding_recovery.2', 'asp_recovery_event_outcome'),
            ('src/stories/personal_bond/game/events/asp_personal_bond_events.txt', 'asp_personal_bond.2', 'asp_bond_terminal_outcome'),
            ('src/core/game/events/asp_pledge_events.txt', 'asp_pledge.2', 'asp_pledge_event_result'),
        )
        allowed = {'if', 'else_if', 'else', 'limit', 'custom_tooltip'}
        for path, event, captured in cases:
            with self.subTest(event=event):
                text = (ROOT/path).read_text(encoding='utf-8-sig')
                immediate = native_block(native_block(text, event+' ='), 'immediate =')
                # A strict allow-list rejects rewards, state writes, event dispatch,
                # or traversal of ended Stories even if nested in a branch.
                keys = re.findall(r'([\w:]+)\s*=\s*', immediate)
                self.assertTrue(keys)
                self.assertTrue(set(keys) <= allowed | {
                    'scope:'+captured,
                    'scope:asp_vengeance_event_accountability',
                    'scope:asp_bond_terminal_mode',
                }, keys)
                self.assertIn('scope:'+captured+' = 1', immediate)
                self.assertIn('custom_tooltip =', immediate)

    def test_absent_public_success_has_no_reward_summary(self):
        text = (ROOT/'src/core/game/events/asp_pledge_events.txt').read_text(encoding='utf-8-sig')
        immediate = native_block(native_block(text, 'asp_pledge.2 ='), 'immediate =')
        absent = native_block(immediate, 'if =')
        self.assertIn('scope:asp_pledge_event_result = 5', absent)
        self.assertIn('custom_tooltip = asp_pledge_absent_happened', absent)
        self.assertNotIn('asp_pledge_reward_happened', absent)

    def test_release_localization_preserves_native_encoding(self):
        files = list((ROOT/'src').glob('*/game/localization/english/*_l_english.yml'))
        files += list((ROOT/'src/stories').glob('*/game/localization/english/*_l_english.yml'))
        self.assertEqual(4, len(files))
        for path in files:
            with self.subTest(path=path.name):
                self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'))
                self.assertTrue(path.read_text(encoding='utf-8-sig').startswith('l_english:\n'))

    def test_keep_disclosure_guards_weak_story_before_mode_read(self):
        text = (ROOT/'src/stories/personal_bond/game/events/asp_personal_bond_events.txt').read_text(encoding='utf-8-sig')
        for event in ('asp_personal_bond.1', 'asp_personal_bond.3'):
            with self.subTest(event=event):
                event_body = native_block(text, event+' =')
                keep = native_block(event_body, 'option =')
                self.assertIn('name = asp_bond_keep', keep)
                guard = native_block(keep, 'if =')
                outer_limit = native_block(guard, 'limit =')
                # Passing a reference into the character-context guard is safe;
                # entering the weak Story to read its mode requires that guard
                # to succeed first, not just an adjacent visibility predicate.
                self.assertRegex(outer_limit, r'^\s*asp_bond_event_can_manage_trigger\s*=\s*\{\s*STORY\s*=\s*scope:asp_bond_event_story\s*\}\s*$')
                self.assertNotIn('var:asp_interpretation', outer_limit)
                mode = native_block(guard, 'if =')
                self.assertIn('scope:asp_bond_event_story ?=', mode)
                self.assertIn('custom_tooltip = asp_bond_friendship_condition', mode)
                self.assertIn('custom_tooltip = asp_bond_romance_condition', guard)
                self.assertNotIn('custom_tooltip', keep.replace(guard, ''))

    def test_future_stress_relief_discloses_base_and_loss_modifiers(self):
        cases = (
            ('vengeance', 'asp_vengeance_l_english.yml', ('asp_vengeance_personal_condition', 'asp_vengeance_accountability_condition', 'asp_vengeance_condition_personal', 'asp_vengeance_condition_accountability')),
            ('holding_recovery', 'asp_recovery_l_english.yml', ('asp_recovery_condition', 'asp_recovery_story_information_private', 'asp_recovery_story_information_declared')),
            ('personal_bond', 'asp_personal_bond_l_english.yml', ('asp_bond_friendship_condition', 'asp_bond_romance_condition', 'asp_bond_story_friendship', 'asp_bond_story_romance')),
        )
        for family, filename, keys in cases:
            text = (ROOT/'src/stories'/family/'game/localization/english'/filename).read_text(encoding='utf-8-sig')
            values = dict(re.findall(r'^\s*(asp_\w+):0 "(.*)"$', text, re.M))
            for key in keys:
                with self.subTest(key=key):
                    self.assertRegex(values[key], r'base (10|20) Stress relief')
                    self.assertIn('Stress Loss modifiers apply', values[key])

    def test_shared_vengeance_memory_does_not_publish_owner_culpability(self):
        text = (ROOT/'src/stories/vengeance/game/localization/english/asp_vengeance_l_english.yml').read_text(encoding='utf-8-sig')
        value = next(line for line in text.splitlines() if line.startswith(' asp_vengeance_personal_memory_desc_third_perspective:'))
        # This same memory type serves secret and public fulfillment. Its third
        # perspective must not turn private owner-responsibility into disclosure.
        self.assertNotRegex(value, r'\b(caused|killed|slew|executed|murdered)\b')

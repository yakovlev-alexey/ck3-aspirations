"""Visible recovery Stories must render their own county and frozen context."""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class RecoveryLocalizationTests(unittest.TestCase):
    def test_native_card_keys_and_both_context_branches(self):
        game = ROOT / "src/stories/holding_recovery/game"
        story = (game / "common/story_cycles/asp_recovery.txt").read_text(encoding="utf-8-sig")
        localization = (game / "localization/english/asp_recovery_l_english.yml").read_text(encoding="utf-8-sig")
        custom = (game / "common/customizable_localization/asp_recovery.txt").read_text(encoding="utf-8-sig")
        self.assertIn('visualization = { custom_string_key = "asp_recovery_story_information" }', story)
        for key in ("asp_holding_recovery_story", "asp_holding_recovery_story_desc"):
            self.assertEqual(len(re.findall(rf"^ {key}:0 ", localization, re.M)), 1)
        self.assertIn("[Story.Custom('asp_recovery_story_information')]", localization)
        self.assertIn("has_variable = asp_declared", custom)
        for key in ("asp_recovery_story_information_private", "asp_recovery_story_information_declared"):
            line = next(line for line in localization.splitlines() if line.startswith(f" {key}:0 "))
            for token in ("Var('asp_target').Title.GetName", "Var('asp_recovery_origin_control').GetValue", "ScriptValue('asp_story_age_days')", "ScriptValue('asp_time_until_review_days')", "Story.Custom('asp_recovery_story_cause')", "Story.Custom('asp_recovery_story_interpretation')"):
                self.assertIn(token, line)
            self.assertIn("Control to at least 80 AND", line)
            self.assertIn("begun after this ambition and funded by me", line)
            for condition in ('Tribal Markets', 'Palisades', 'Pastures', 'Cereal Fields', 'Hill Farms', 'cancelled', 'foreign-funded', 'ownership-interrupted'):
                self.assertIn(condition, line)
        declared = next(line for line in localization.splitlines() if line.startswith(" asp_recovery_story_information_declared:0 "))
        self.assertIn("ScriptValue('asp_time_until_pledge_days')", declared)
        for cause in ("raid", "siege"):
            self.assertIn(f"flag:{cause}", custom)
        for interpretation in ("protection", "family_prestige", "income"):
            self.assertIn(f"flag:{interpretation}", custom)


if __name__ == "__main__":
    unittest.main()

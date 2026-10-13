import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class IntegratedLocalizationTests(unittest.TestCase):
    def test_card_uses_selected_native_mode(self):
        text=(ROOT/'src/stories/personal_bond/game/localization/english/asp_personal_bond_l_english.yml').read_text(encoding='utf-8-sig')
        self.assertIn("[Story.Custom('asp_bond_story_mode')]",text)
        self.assertIn('asp_bond_story_friendship:',text)
        self.assertIn('asp_bond_story_romance:',text)
        branch=(ROOT/'src/stories/personal_bond/game/common/customizable_localization/asp_personal_bond.txt').read_text(encoding='utf-8-sig')
        self.assertIn('var:asp_interpretation = flag:romance',branch)

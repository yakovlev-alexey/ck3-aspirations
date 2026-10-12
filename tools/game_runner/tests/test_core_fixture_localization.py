import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class CoreFixtureLocalizationTests(unittest.TestCase):
    def test_native_debug_story_has_name_and_implicit_description(self):
        story = (ROOT / "src/core/tests/game/common/story_cycles/asp_core_debug.txt").read_text(encoding="utf-8-sig")
        localization = (ROOT / "src/core/tests/game/localization/english/asp_core_debug_l_english.yml").read_text(encoding="utf-8-sig")
        self.assertIn("asp_core_debug = {", story)
        for key in ("asp_core_debug", "asp_core_debug_desc"):
            with self.subTest(key=key):
                self.assertRegex(localization, rf'(?m)^ {re.escape(key)}:0 "[^"\n]+"$')


if __name__ == "__main__":
    unittest.main()
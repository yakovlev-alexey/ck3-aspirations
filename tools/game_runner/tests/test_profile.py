import tempfile
import unittest
from pathlib import Path
from tools.game_runner import windows


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.check = getattr(windows, "require_safe_profile", None)
        self.assertIsNotNone(self.check, "autosave/profile launch preflight is absent")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.documents = Path(self.temp.name) / "Documents"
        self.user = self.documents / "Paradox Interactive" / "Crusader Kings III"
        self.user.mkdir(parents=True)

    def profile(self, text):
        (self.user / "pdx_settings.txt").write_text(text, encoding="utf-8")

    def test_never_in_actual_profile_allows_launch_preflight(self):
        self.profile('"game"={"autosave"={version=0 value="NEVER"}}')
        self.check(self.user, self.documents)

    def test_other_sections_comments_and_yearly_cannot_enable_preflight(self):
        for text in [
            '"renderer"={"autosave"={value="NEVER"}} "game"={"autosave"={value="YEARLY"}}',
            '# "game"={"autosave"={value="NEVER"}}\n"game"={"autosave"={value="YEARLY"}}',
            '"game"={"autosave"={value="MONTHLY"}}',
        ]:
            with self.subTest(text=text):
                self.profile(text)
                with self.assertRaises(ValueError):
                    self.check(self.user, self.documents)

    def test_missing_duplicate_or_malformed_preference_is_rejected(self):
        for text in [
            '"game"={}',
            '"game"={"autosave"={value="NEVER"} "autosave"={value="YEARLY"}}',
            '"game"={"autosave"={value="NEVER"}} "game"={"autosave"={value="NEVER"}}',
            '"game"={"autosave"={value="NEVER"}',
        ]:
            with self.subTest(text=text):
                self.profile(text)
                with self.assertRaises(ValueError):
                    self.check(self.user, self.documents)

    def test_configured_alternate_profile_is_rejected(self):
        self.profile('"game"={"autosave"={value="NEVER"}}')
        alternate = self.documents / "alternate"
        alternate.mkdir()
        (alternate / "pdx_settings.txt").write_text('"game"={"autosave"={value="NEVER"}}',encoding="utf-8")
        with self.assertRaises(ValueError):
            self.check(alternate, self.documents)


if __name__ == "__main__":
    unittest.main()

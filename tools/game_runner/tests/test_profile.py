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

    def test_no_autosave_in_actual_profile_allows_launch_preflight(self):
        self.profile('"game"={"autosave"={version=0 value="NO_AUTOSAVE"}}')
        self.check(self.user, self.documents)

    def test_other_sections_comments_and_yearly_cannot_enable_preflight(self):
        for text in [
            '"renderer"={"autosave"={value="NO_AUTOSAVE"}} "game"={"autosave"={value="YEARLY"}}',
            '# "game"={"autosave"={value="NO_AUTOSAVE"}}\n"game"={"autosave"={value="YEARLY"}}',
            '"game"={"autosave"={value="MONTHLY"}}',
        ]:
            with self.subTest(text=text):
                self.profile(text)
                with self.assertRaises(ValueError):
                    self.check(self.user, self.documents)

    def test_invalid_never_enum_is_rejected(self):
        self.profile('"game"={"autosave"={value="NEVER"}}')
        with self.assertRaises(ValueError):
            self.check(self.user, self.documents)

    def backend(self):
        from types import SimpleNamespace
        backend = windows.WindowsBackend.__new__(windows.WindowsBackend)
        backend.process = SimpleNamespace(poll=lambda: None, pid=100)
        backend.hwnd = 42
        def pid(hwnd, pointer):
            pointer._obj.value = 100
        backend.user32 = SimpleNamespace(GetForegroundWindow=lambda: 42, GetWindowThreadProcessId=pid)
        backend.preflight = lambda: self.check(self.user, self.documents)
        return backend

    def test_profile_rewrite_after_load_is_rejected_by_validation(self):
        self.profile('"game"={"autosave"={value="NO_AUTOSAVE"}}')
        backend = self.backend()
        backend.validate()
        self.profile('"game"={"autosave"={value="YEARLY"}}')
        with self.assertRaises(ValueError):
            backend.validate()

    def test_profile_rewrite_before_tick_sends_no_input(self):
        self.profile('"game"={"autosave"={value="NO_AUTOSAVE"}}')
        backend = self.backend()
        backend.validate()
        self.profile('"game"={"autosave"={value="YEARLY"}}')
        inputs = []
        backend.key = lambda vk: inputs.append(vk)
        backend._input = lambda *args, **kwargs: inputs.append((args, kwargs))
        with self.assertRaises(ValueError):
            backend.command("tick_day 1")
        self.assertEqual(inputs, [])

    def test_missing_duplicate_or_malformed_preference_is_rejected(self):
        for text in [
            '"game"={}',
            '"game"={"autosave"={value="NO_AUTOSAVE"} "autosave"={value="YEARLY"}}',
            '"game"={"autosave"={value="NO_AUTOSAVE"}} "game"={"autosave"={value="NO_AUTOSAVE"}}',
            '"game"={"autosave"={value="NO_AUTOSAVE"}',
        ]:
            with self.subTest(text=text):
                self.profile(text)
                with self.assertRaises(ValueError):
                    self.check(self.user, self.documents)

    def test_configured_alternate_profile_is_rejected(self):
        self.profile('"game"={"autosave"={value="NO_AUTOSAVE"}}')
        alternate = self.documents / "alternate"
        alternate.mkdir()
        (alternate / "pdx_settings.txt").write_text('"game"={"autosave"={value="NO_AUTOSAVE"}}',encoding="utf-8")
        with self.assertRaises(ValueError):
            self.check(alternate, self.documents)


if __name__ == "__main__":
    unittest.main()

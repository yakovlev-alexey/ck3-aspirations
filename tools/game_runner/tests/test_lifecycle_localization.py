"""Native scope localization must use supported presence checks."""
from pathlib import Path
import unittest
class LocalizationTests(unittest.TestCase):
    def test_private_and_declared_presence_use_native_var_is_set(self):
        root=Path(__file__).resolve().parents[3]
        for relative in ("src/core/game/localization/english/asp_core_l_english.yml","src/stories/vengeance/game/localization/english/asp_vengeance_l_english.yml"):
            text=(root/relative).read_text(encoding="utf-8-sig")
            self.assertNotIn("MakeScope.HasVariable",text)

    def test_event_visibility_preserves_native_predicates(self):
        root=Path(__file__).resolve().parents[3]
        for name in ("asp_management_events.txt","asp_core_events.txt","asp_pledge_events.txt"):
            text=(root/"src/core/game/events"/name).read_text(encoding="utf-8-sig")
            self.assertNotIn("hidden_trigger",text)
            predicate = "asp_event_can_declare_trigger" if name == "asp_pledge_events.txt" else "asp_story_owned_by_event_root_trigger"
            self.assertIn(predicate,text)
        core=(root/"src/core/game/common/scripted_triggers/asp_core.txt").read_text(encoding="utf-8-sig")
        self.assertIn("asp_can_declare_story_trigger = yes asp_story_owned_by_event_root_trigger = yes",core)
    def test_all_aspiration_script_value_getters_are_defined(self):
        import re
        root=Path(__file__).resolve().parents[3]
        values=set()
        for path in (root/"src").glob("**/game/common/script_values/*.txt"):
            values.update(re.findall(r"^(asp_\w+)\s*=",path.read_text(encoding="utf-8-sig"),re.M))
        for path in (root/"src").glob("**/game/localization/english/*.yml"):
            for key in re.findall(r"ScriptValue\('([^']+)'\)",path.read_text(encoding="utf-8-sig")):
                if key.startswith("asp_"): self.assertIn(key,values,str(path))
    def test_dynamic_deadline_keeps_its_native_context(self):
        root=Path(__file__).resolve().parents[3]
        core=(root/"src/core/game/events/asp_management_events.txt").read_text(encoding="utf-8-sig")
        self.assertIn("desc = asp_management_selected_declared_character_desc",core)
        family=(root/"src/stories/vengeance/game/common/customizable_localization/asp_vengeance.txt").read_text(encoding="utf-8-sig")
        self.assertIn("asp_vengeance_story_information_declared",family)

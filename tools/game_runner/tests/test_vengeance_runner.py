"""Vengeance reports must reject missing or incorrect native case measurements."""
import re
import unittest
from tools.game_runner.tests import test_runner as runner_tests

FIELDS = {
    "v01": 1, "v01_created": 1, "v01_replayed": 0,
    "v02": 1, "v02_hidden": 0, "v02_known": 1, "v02_exposed": 0,
    "v03": 1, "v03_personal_delta": -20, "v03_impossible_delta": 0, "v03_memories": 2,
    "v04": 1, "v04_stress_delta": -20, "v04_prestige_delta": 100, "v04_preexisting": 0,
    "v05": 1, "v05_content": 1, "v05_exclusions": 3, "v05_costs": 1,
    "v06": 1, "v06_action_delta": 52, "v06_closure_delta": -20, "v06_total_delta": 32,
}

class VengeanceBoundary(runner_tests.NativeIOBoundary):
    def command(self, command):
        text = (self.config.user_data / "run" / "asp_automation_request.txt").read_text(encoding="utf-8-sig")
        if "OP = vengeance_regression" not in text:
            return super().command(command)
        session = int(re.search(r"SESSION = (\d+)", text)[1])
        request = int(re.search(r"REQUEST = (\d+)", text)[1])
        log = self.config.user_data / "logs" / "debug.log"
        if self.cached and self.cached[:2] == (session, request):
            with log.open("ab") as stream:
                stream.write(self.cached[2])
            return
        fields = dict(FIELDS)
        fields.update(getattr(self, "override", {}))
        fields.pop(getattr(self, "drop", ""), None)
        line = f"ASP_AUTOMATION|1|{session}|{request}|DONE|counter=0|date=43000|"
        data = (line + "|".join(f"{key}={value}" for key, value in fields.items()) + "\n").encode()
        with log.open("ab") as stream:
            stream.write(data)
        self.cached = (session, request, data)

class VengeanceRunnerTests(unittest.TestCase):
    def setUp(self):
        runner_tests.RunnerIOTests.setUp(self)
        self.backend = VengeanceBoundary(self.config)
        self.runner.backend = self.backend

    def tearDown(self):
        runner_tests.RunnerIOTests.tearDown(self)

    def test_measured_vengeance_report_and_cached_duplicate(self):
        report = self.runner.run_scenario("vengeance-regression")
        self.assertEqual(report["status"], "passed")
        result = report["runs"][0]
        self.assertEqual(result["vengeance"]["v04_prestige_delta"], 100)
        self.assertEqual(result["duplicate"], result["vengeance"])
        self.assertEqual(len(result["assertions"]), 10)

    def test_wrong_native_delta_cannot_pass_even_with_pass_flag(self):
        self.backend.override = {"v04_prestige_delta": 200}
        report = self.runner.run_scenario("vengeance-regression")
        self.assertEqual(report["status"], "assertion_failed")
        self.assertIn("V04_new_custody_only", {a["name"] for a in report["runs"][0]["assertions"] if not a["passed"]})

    def test_incomplete_native_vengeance_result_is_transport_error(self):
        self.backend.drop = "v02_hidden"
        report = self.runner.run_scenario("vengeance-regression")
        self.assertEqual(report["status"], "transport_error")
        self.assertFalse(self.backend.running)

    def test_hidden_origin_is_rejected_despite_pass_flag(self):
        self.backend.override = {"v02_hidden": 1}
        self.assertEqual(self.runner.run_scenario("vengeance-regression")["status"], "assertion_failed")

if __name__ == "__main__":
    unittest.main()

"""Lifecycle telemetry validates native deltas independently of PASS markers."""
import re
import unittest
from tools.game_runner.tests import test_runner as base
FIELDS = {"p01":1,"p02":1,"p03":1,"p04":1,"p05":1,"p06":1,"release_delta":0,"penalty_prestige":-100,"penalty_stress":19,"penalty_control":19,"return_prestige":-100,"return_stress":19,"absent_stress":0,"replacement_count":3,"replacement_delta":13,"replacement_control":13,"ui_replay":1}
class Boundary(base.NativeIOBoundary):
    def command(self, command):
        text = (self.config.user_data / "run" / "asp_automation_request.txt").read_text(encoding="utf-8-sig")
        calendar = "OP = lifecycle_calendar_assert" in text
        reload_check = "OP = lifecycle_reload_assert" in text
        if "OP = lifecycle_regression" not in text and not calendar and not reload_check:
            return super().command(command)
        session=int(re.search(r"SESSION = (\d+)",text)[1]);request=int(re.search(r"REQUEST = (\d+)",text)[1])
        log=self.config.user_data/"logs"/"debug.log"
        if self.cached and self.cached[:2]==(session,request):
            with log.open("ab") as stream: stream.write(self.cached[2])
            return
        fields={"calendar_before":43000,"calendar_after":43001,"calendar_reviews":2,"calendar_declare":1,"calendar_prestige":-100,"calendar_stress":19,"calendar_control":19} if calendar else dict(FIELDS)
        if reload_check: fields={"reload_identity":1}
        fields.update({key:value for key,value in getattr(self,"override",{}).items() if key in fields});fields.pop(getattr(self,"drop",""),None)
        data=(f"ASP_AUTOMATION|1|{session}|{request}|DONE|counter=0|date=43000|"+"|".join(f"{key}={value}" for key,value in fields.items())+"\n").encode()
        with log.open("ab") as stream: stream.write(data)
        self.cached=(session,request,data)
        if getattr(self,"runtime_error",False):
            (self.config.user_data/"logs"/"error.log").write_text(getattr(self,"diagnostic","[00:00:00][E][test.cpp:1]: Script system error!\n Error: invalid scope\n Script location: file: common/scripted_effects/asp_core.txt line: 1\n"),encoding="utf-8")
class LifecycleTests(unittest.TestCase):
    def setUp(self):
        base.RunnerIOTests.setUp(self);self.backend=Boundary(self.config);self.runner.backend=self.backend
    def tearDown(self): base.RunnerIOTests.tearDown(self)
    def test_measured_replay(self):
        report=self.runner.run_scenario("lifecycle-regression")
        self.assertEqual(report["status"],"passed")
        self.assertEqual(report["runs"][0]["lifecycle"],report["runs"][0]["duplicate"])
    def test_wrong_once_cost_rejected_despite_pass(self):
        self.backend.override={"penalty_prestige":-200}
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"assertion_failed")
    def test_absent_reward_rejected(self):
        self.backend.override={"absent_stress":-20}
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"assertion_failed")
    def test_incomplete_result_rejected(self):
        self.backend.drop="replacement_count"
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"transport_error")
    def test_native_runtime_error_rejected_despite_pass(self):
        self.backend.runtime_error=True
        report=self.runner.run_scenario("lifecycle-regression")
        self.assertEqual(report["status"],"assertion_failed")
        self.assertGreaterEqual(report["runs"][0]["aspiration_runtime_error_count"],1)
    def test_compile_link_and_factory_diagnostics_rejected(self):
        for source in ("jomini_script_argument.cpp", "jomini_eventtarget.cpp", "pdx_data_factory.cpp"):
            with self.subTest(source=source):
                self.backend.runtime_error=True
                self.backend.diagnostic=f"[00:00:00][E][{source}:1]: Native invalid script/data scope\n Script location: common/scripted_effects/asp_core.txt\n"
                report=self.runner.run_scenario("lifecycle-regression")
                self.assertEqual(report["status"],"assertion_failed")
                self.assertEqual(report["runs"][0]["aspiration_runtime_error_count"],2)
    def test_no_valid_options_rejected_despite_native_pass(self):
        self.backend.runtime_error=True
        self.backend.diagnostic="[05:13:22][E][event_window_data.cpp:286]: Event 'asp_vengeance.1' triggered but has no valid options for Test Aspirant\n"
        report=self.runner.run_scenario("lifecycle-regression")
        self.assertTrue(all(report["runs"][0]["lifecycle"]["p0"+str(n)]==1 for n in range(1,7)))
        self.assertEqual(report["status"],"assertion_failed")
        self.assertGreater(report["runs"][0]["aspiration_runtime_error_count"],0)
    def test_wrong_actual_calendar_boundary_rejected(self):
        self.backend.override={"calendar_reviews":1}
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"assertion_failed")
    def test_parser_diagnostic_cannot_pass(self):
        self.backend.runtime_error=True
        self.backend.diagnostic='[00:00:00][E][pdx_persistent_reader.cpp:216]: Error: "Invalid date string" in file: "common/scripted_effects/asp_lifecycle_test.txt"\n'
        report=self.runner.run_scenario("lifecycle-regression")
        self.assertEqual(report["status"],"assertion_failed")
    def test_wrong_saved_state_precondition_rejected(self):
        self.backend.override={"reload_identity":0}
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"assertion_failed")
    def test_ui_replay_memory_assertion_rejected_despite_pass(self):
        self.backend.override={"ui_replay":0}
        self.assertEqual(self.runner.run_scenario("lifecycle-regression")["status"],"assertion_failed")

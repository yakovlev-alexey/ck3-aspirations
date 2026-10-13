"""Recovery transport checks reject plausible PASS records with wrong measurements."""
import re
import unittest
from tools.game_runner.tests import test_runner as base
FIELDS = {"h01":1,"h02":1,"h03":1,"h04":1,"h05":1,"reward_stress":-20,"reward_xp":100,"modifier_count":1,"loss_stress":13,"loss_control":13,"pledge_stress":19,"pledge_control":19,"pledge_prestige":-100,"unproven":0,"foreign":0,"cancelled":0,"replayed":0,"origin_control":69}
class Boundary(base.NativeIOBoundary):
    def command(self, command):
        text=(self.config.user_data/"run"/"asp_automation_request.txt").read_text(encoding="utf-8-sig")
        if "OP = recovery_regression" not in text: return super().command(command)
        session=int(re.search(r"SESSION = (\d+)",text)[1]);request=int(re.search(r"REQUEST = (\d+)",text)[1])
        log=self.config.user_data/"logs"/"debug.log"
        if self.cached and self.cached[:2]==(session,request):
            with log.open("ab") as stream: stream.write(self.cached[2])
            return
        fields=dict(FIELDS);fields.update(getattr(self,"override",{}));fields.pop(getattr(self,"drop",""),None)
        data=(f"ASP_AUTOMATION|1|{session}|{request}|DONE|counter=0|date=43000|"+"|".join(f"{key}={value}" for key,value in fields.items())+"\n").encode()
        with log.open("ab") as stream: stream.write(data)
        self.cached=(session,request,data)
        if getattr(self,"runtime_error",False):
            (self.config.user_data/"logs"/"error.log").write_text('[00:00:00][E][test.cpp:1]: Script system error!\n Error: invalid scope\n Script location: file: common/scripted_effects/asp_recovery.txt line: 1\n',encoding="utf-8")
class RecoveryRunnerTests(unittest.TestCase):
    def setUp(self):
        base.RunnerIOTests.setUp(self);self.backend=Boundary(self.config);self.runner.backend=self.backend
    def tearDown(self): base.RunnerIOTests.tearDown(self)
    def test_complete_measured_replay(self):
        report=self.runner.run_scenario("recovery-regression")
        self.assertEqual(report["status"],"passed")
        self.assertEqual(report["runs"][0]["recovery"],report["runs"][0]["duplicate"])
    def test_foreign_payment_cannot_pass(self):
        self.backend.override={"foreign":1}
        self.assertEqual(self.runner.run_scenario("recovery-regression")["status"],"assertion_failed")
    def test_unmodified_nominal_stress_cannot_replace_native_control(self):
        self.backend.override={"loss_stress":10,"pledge_stress":15}
        self.assertEqual(self.runner.run_scenario("recovery-regression")["status"],"assertion_failed")
    def test_repeat_reward_rejected(self):
        self.backend.override={"replayed":-20}
        self.assertEqual(self.runner.run_scenario("recovery-regression")["status"],"assertion_failed")
    def test_missing_measurement_rejected(self):
        self.backend.drop="cancelled"
        self.assertEqual(self.runner.run_scenario("recovery-regression")["status"],"transport_error")
    def test_native_error_rejected_despite_pass_fields(self):
        self.backend.runtime_error=True
        report=self.runner.run_scenario("recovery-regression")
        self.assertEqual(report["status"],"assertion_failed")
        self.assertGreater(report["runs"][0]["aspiration_runtime_error_count"],0)

"""Integrated transport checks reject plausible PASS records with wrong measurements."""
import re
import unittest
from tools.game_runner.tests import test_runner as base
FIELDS = {'ambitions': 3, 'desires': 5, 'caps_rejected': 1, 'other_stories': 7, 'identity_preserved': 1, 'selected_stress': -10, 'selected_xp': 50, 'selected_prestige': 0, 'selected_stewardship': 0, 'after_ambitions': 3, 'after_desires': 4, 'replay_xp': 0, 'pledge_stress': 0, 'pledge_prestige': 0, 'pledge_result': 5, 'county_result': 5, 'normal_result': 1, 'normal_prestige': 100, 'persistence_identity': 1, 'replacement_valid': 1, 'replacement_duplicate': 1}
class Boundary(base.NativeIOBoundary):
    diagnostic = None
    def command(self, command):
        text=(self.config.user_data/"run"/"asp_automation_request.txt").read_text(encoding="utf-8-sig")
        if "OP = integrated_regression" not in text: return super().command(command)
        session=int(re.search(r"SESSION = (\d+)",text)[1]);request=int(re.search(r"REQUEST = (\d+)",text)[1])
        log=self.config.user_data/"logs"/"debug.log"
        if self.cached and self.cached[:2]==(session,request):
            with log.open("ab") as stream: stream.write(self.cached[2])
            return
        fields=dict(FIELDS);fields.update(getattr(self,"override",{}));fields.pop(getattr(self,"drop",""),None)
        data=(f"ASP_AUTOMATION|1|{session}|{request}|DONE|counter=0|date=43000|"+"|".join(f"{key}={value}" for key,value in fields.items())+"\n").encode()
        with log.open("ab") as stream: stream.write(data)
        self.cached=(session,request,data)
        if self.diagnostic:
            (self.config.user_data/"logs"/"error.log").write_text(self.diagnostic,encoding="utf-8")
        if getattr(self,"runtime_error",False):
            (self.config.user_data/"logs"/"error.log").write_text('[00:00:00][E][test.cpp:1]: Script system error!\n Error: invalid scope\n Script location: file: common/scripted_effects/asp_bond.txt line: 1\n',encoding="utf-8")
class IntegratedRunnerTests(unittest.TestCase):
    def setUp(self):
        base.RunnerIOTests.setUp(self); self.backend=Boundary(self.config); self.runner.backend=self.backend
    def tearDown(self): base.RunnerIOTests.tearDown(self)
    def test_complete_measured_replay(self):
        report=self.runner.run_scenario("integrated-regression")
        self.assertEqual(report["status"],"passed")
        self.assertEqual(report["runs"][0]["integrated"], report["runs"][0]["duplicate"])
    def test_each_wrong_measurement_cannot_pass(self):
        for field,value in FIELDS.items():
            with self.subTest(field=field):
                self.backend.override={field:value+1}
                self.assertEqual(self.runner.run_scenario("integrated-regression")["status"],"assertion_failed")
    def test_missing_measurement_cannot_pass(self):
        self.backend.drop="identity_preserved"
        self.assertEqual(self.runner.run_scenario("integrated-regression")["status"],"transport_error")
    def test_native_error_cannot_pass(self):
        self.backend.diagnostic="[00:00:00][E][pdx_data_factory.cpp:1]: Invalid native data\n Script location: asp_pledge.2\n"
        self.assertEqual(self.runner.run_scenario("integrated-regression")["status"],"assertion_failed")

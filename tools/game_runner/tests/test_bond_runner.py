"""Bond transport checks reject plausible PASS records with wrong measurements."""
import re
import unittest
from tools.game_runner.tests import test_runner as base
FIELDS = {'b01': 1, 'b02': 1, 'b03': 1, 'b04': 1, 'b05': 1, 'native_locked': 1, 'native_unlocked': 1, 'native_romance': 1, 'friend_stress': -10, 'friend_xp': 50, 'romance_stress': -10, 'romance_xp': 0, 'replay_xp': 0, 'memories': 2, 'death_stress': 0, 'temporary_retained': 1, 'incompatible_stress': 0, 'rival_fixed': 1, 'chance0': 20, 'chance1': 12, 'chance2': 6, 'chance3': 2, 'chance4': 2, 'chance5': 0, 'cooldown': 360, 'consumed': 1, 'fresh': 1, 'content': 1, 'lustful_weight': 15}
FIELDS.update({'b06': 1, 'b07': 1, 'bestfriend_stress': -10, 'bestfriend_xp': 50, 'soulmate_stress': -10, 'soulmate_xp': 0, 'blocked_cooldown': 1, 'blocked_cap': 1, 'absence_stress': 0, 'absence_xp': 0, 'early_stress': 7, 'early_control': 7, 'review_release': 0, 'retained_days': 360, 'origin_preserved': 1, 'no_pledge': 1, 'already_mode': 1, 'routine_created': 1, 'context_stable': 1})
FIELDS.update({'f2r_eligible': 1, 'f2r_mode': 2, 'f2r_same_story': 1, 'f2r_same_target': 1, 'f2r_instance_delta': 0, 'f2r_allocation_delta': 0, 'f2r_origin_delta': 0, 'f2r_incident_delta': 0, 'f2r_signature_delta': 0, 'f2r_serial_delta': 0, 'f2r_consumed_delta': 0, 'f2r_cooldown_delta': 0, 'f2r_desires': 1, 'f2r_stress': 0, 'f2r_xp': 0, 'f2r_memories': 0, 'f2r_review_days': 720, 'f2r_review_notified': 0, 'r2f_eligible': 1, 'r2f_mode': 1, 'r2f_same_story': 1, 'r2f_same_target': 1, 'r2f_instance_delta': 0, 'r2f_allocation_delta': 0, 'r2f_origin_delta': 0, 'r2f_incident_delta': 0, 'r2f_signature_delta': 0, 'r2f_serial_delta': 0, 'r2f_consumed_delta': 0, 'r2f_cooldown_delta': 0, 'r2f_desires': 1, 'r2f_stress': 0, 'r2f_xp': 0, 'r2f_memories': 0, 'r2f_review_days': 360, 'r2f_review_notified': 0})
FIELDS.update({'f2r_before_mode': 1, 'r2f_before_mode': 2})
class Boundary(base.NativeIOBoundary):
    diagnostic = None
    def command(self, command):
        text=(self.config.user_data/"run"/"asp_automation_request.txt").read_text(encoding="utf-8-sig")
        if "OP = bond_regression" not in text: return super().command(command)
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
class BondRunnerTests(unittest.TestCase):
    def setUp(self):
        base.RunnerIOTests.setUp(self);self.backend=Boundary(self.config);self.runner.backend=self.backend
    def tearDown(self): base.RunnerIOTests.tearDown(self)
    def test_complete_measured_replay(self):
        report=self.runner.run_scenario("bond-regression")
        self.assertEqual(report["status"],"passed")
        self.assertEqual(report["runs"][0]["bond"],report["runs"][0]["duplicate"])
    def test_wrong_chance_cannot_pass(self):
        self.backend.override={"chance4":20}
        self.assertEqual(self.runner.run_scenario("bond-regression")["status"],"assertion_failed")
    def test_romance_cannot_grant_friendship_xp(self):
        self.backend.override={"romance_xp":50}
        self.assertEqual(self.runner.run_scenario("bond-regression")["status"],"assertion_failed")
    def test_repeat_reward_rejected(self):
        self.backend.override={"replay_xp":50}
        self.assertEqual(self.runner.run_scenario("bond-regression")["status"],"assertion_failed")
    def test_missing_measurement_rejected(self):
        self.backend.drop="cooldown"
        self.assertEqual(self.runner.run_scenario("bond-regression")["status"],"transport_error")
    def test_native_error_rejected_despite_pass_fields(self):
        self.backend.runtime_error=True
        report=self.runner.run_scenario("bond-regression")
        self.assertEqual(report["status"],"assertion_failed")
        self.assertGreater(report["runs"][0]["aspiration_runtime_error_count"],0)

    def test_incomplete_case_cannot_pass(self):
        for field in ("native_locked", "temporary_retained", "rival_fixed", "consumed", "fresh", "content"):
            with self.subTest(field=field):
                self.backend.override = {field: 0}
                self.assertEqual(self.runner.run_scenario("bond-regression")["status"], "assertion_failed")

    def test_native_compile_link_and_factory_diagnostics_cannot_pass(self):
        for source in ("jomini_script_argument.cpp", "jomini_eventtarget.cpp", "pdx_data_factory.cpp"):
            with self.subTest(source=source):
                self.backend.diagnostic = f"[00:00:00][E][{source}:1]: Native invalid script/data scope\n Script location: common/scripted_effects/asp_personal_bond.txt\n"
                self.assertEqual(self.runner.run_scenario("bond-regression")["status"], "assertion_failed")

    def test_no_valid_options_cannot_pass_despite_complete_measurements(self):
        self.backend.diagnostic = "[00:00:00][E][event_window_data.cpp:286]: Event 'asp_personal_bond.1' triggered but has no valid options\n"
        self.assertEqual(self.runner.run_scenario("bond-regression")["status"], "assertion_failed")

    def test_successful_reinterpretation_cannot_noop_reset_or_reward(self):
        fields = [key for key in FIELDS if key.startswith(('f2r_', 'r2f_'))]
        self.assertEqual(len(fields), 38)
        for field in fields:
            with self.subTest(field=field):
                self.backend.override = {field: (3 - FIELDS[field]) if field.endswith("_mode") else FIELDS[field] + 1}
                self.assertEqual(self.runner.run_scenario('bond-regression')['status'], 'assertion_failed')

    def test_missing_successful_reinterpretation_measurement_rejected(self):
        self.backend.drop = 'r2f_consumed_delta'
        self.assertEqual(self.runner.run_scenario('bond-regression')['status'], 'transport_error')

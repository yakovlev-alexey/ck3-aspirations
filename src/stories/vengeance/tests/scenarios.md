# Vengeance acceptance scenarios

[Contract](../SPEC.md) · [Shared lifecycle and pledge scenarios](../../../core/tests/scenarios.md). V01-V06 use the shared native effects in `game/common/scripted_effects/asp_vengeance_test.txt`; `event asp_test_vengeance.1` and registered `vengeance-regression` call exactly those effects. The registered suite is the reproducible automatable gate. Real UI/action acceptance is a separate required gate.

Run from a disposable adult landed male player baseline with the dev profile active and autosave disabled:

```powershell
python -m tools.game_runner --config .local/automation/config.json run vengeance-regression --repeat 1
```

| ID | Controlled setup and native assertion | Expected extra result |
| --- | --- | --- |
| V01 | Actual scripted death invokes the additive native child; force randomness only after captured eligibility. Compare exact victim/culprit, one reservation, duplicate new death with same culprit, then abandon and replay both origins. | One ambition, both deaths consumed, no further instance ID for the active duplicate, zero replay after release. |
| V02 | Raw concealed killer, no matching known secret; then native `reveal_to` on the exact murder secret and process retained candidates. Forgive and repeat. Separately expose another secret before its first observation. | Hidden 0, verified known 1, exposure-only 0, no repeated proposal. Pending lists contain only observed victims, never a hidden culprit. |
| V03 | Record actual native owner-attributed death; separately natural unrelated death; repeat each callback and inspect exact victim-bound memory types. | Personal -20 Stress and one personal memory; unrelated 0 Stress and one impossible memory; no heir target. |
| V04 | Select accountability with a live culprit outside custody, then native `imprison` and refresh twice; compare origin with preexisting custody. | New custody +100 Prestige/-20 Stress once; preexisting custody cannot choose accountability. |
| V05 | Owner-caused death; child victims who are rival/nemesis; Content friend bereavement; plain/Compassionate/Vengeful/both-trait costs; occupancy 0/1/2. | Three exclusions, Content eligible, base costs 10/5/15/15, probabilities 50/35/20 and Vengeful 75/52.5/30. |
| V06 | Run installed `execute_prisoner_effect` for a Compassionate owner, capture stress before and immediately after action, then refresh fixed personal goal. | Positive vanilla action stress remains; aspiration separately -20; total equals action delta minus 20. This scripted action is logic evidence, not a real GUI click. |
| V07 | Declared personal vengeance and shown public-attribution rule. | Reserved for Task 4 pledge tests: secret private closure plus withdrawal, public fulfillment plus pledge bonus. |
| V08 | Scheduled reflection, reinterpretation, switching away and return. | Reserved for Task 4 lifecycle tests; age/pledge policy preserved, no retrospective reward. |

Knowledge capability probe: `event asp_test_vengeance.10` compares explicit public `death_duel`, a concealed `death_murder`, native secret discovery and exposure. CK3 1.20.0.4 exposes no generic read-side killer-knowledge predicate. Public death reason plus exact killer and a matching `any_known_secret` (`secret_type`, `secret_owner`, `secret_target`, `is_known_by`) are verified positive evidence. Exposure removes the secret from the known-secret iterator while the same-event secret scope survives. Direct exposure before observation remains unsupported; never infer public knowledge from the raw killer, murderer trait or generic opinion. V02 registers the corresponding positive and negative gameplay paths.

## Mandatory actual execution and rendering

1. Load the same disposable baseline with the dev profile. Pause. Run `event asp_test_vengeance.20`; demand fresh `ASP_TEST V06 GUI READY`. Setup creates one known ambition and a live prisoner, sets Compassionate, and stores exact target/story plus stress/memory baselines. It never executes the target.
2. Capture the readable origin naming victim and culprit; inspect all conditions/costs. Choose personal vengeance in the actual event UI. Open the target through the story or prison UI, choose vanilla Execute, capture the confirmation tooltip (normal trait stress/legal effects), and click the real confirmation. Keep the date paused.
3. Run `event asp_test_vengeance.21`; require fresh `ASP_TEST V06 GUI PASS` and measured `action`, `closure`, `memories`. This checks the target is dead with this owner as killer, positive native action stress, separate -20 closure, exactly one memory and zero active ambitions; repeat refresh cannot pay twice. Capture the personal terminal event and fresh logs.
4. Inspect the native story card before execution: title, cause, exact condition, fixed target, age and reflection information must resolve in English. `event asp_test_vengeance.30` prepares a separate visual origin; choose personal, then `.31` produces unrelated death and a distinct unresolved-closure event. Capture that event separately. These visual steps are not certified by the bounded runner.

Do not repurpose core `.2` (C04 reload) or `.3` (C03 stale action). Test fixture and debug localization are dev-only. Record fresh report paths and actual screenshots in the ignored task report; never commit saves or logs.

Observed Task 3 results on CK3 1.20.0.4: registered V01-V06 passed, including literal deltas/counts and cached duplicate identity; actual paused vanilla Execute separately passed +100 action Stress/-20 closure/one memory. Corrected native cards and all four distinct terminal meanings render in English. The earlier uppercase getter failure is retained in the ignored report/evidence. V07-V08 are covered by the Task 4 P01-P06 procedures below; independent stage review is pending.

## Task 4 pledge and lifecycle entry

`event asp_test_vengeance.2` executes shared P01-P06 assertions from core’s `lifecycle-regression`; the `.1` V01-V06 entry remains unchanged. Required actual calendar, save/load, review/declaration/replacement UI, switch/return, owner death and succession procedures are documented in [core scenarios](../../../core/tests/scenarios.md). Secret fulfillment withdraws an unexpired public pledge, public fulfillment adds one core +100, and owner-caused impossibility cannot excuse a pledge. No direct-exposure knowledge gap is silently broadened.

Task 7 registered [combined core scenarios](../../../core/tests/scenarios.md#task-7-combined-registered-and-actual-acceptance) exercise replacement duplicate filters with unlike Character/Title targets and invisible bond contexts. Explicit schema/family branches must preserve real same-family duplicate rejection and produce no native tooltip diagnostics. Existing family reward/eligibility contracts are unchanged.

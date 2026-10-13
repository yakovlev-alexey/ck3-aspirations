# Construction reservation, original payer and exact Story tokens

Status: measured-native callbacks/UI; scripted native token-isolation regressions.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

Installed construction on_actions expose the original payer in `scope:character`; native fallback may substitute the holding owner afterward. An additive child retains the original scope: actual player and AI purchases supplied the payer, while script-created construction supplied none despite the fallback. Capture and verify original identity; never infer payment from holder. The dedicated AI probe omitted `-disable_ai`, prepared a legal vacancy/funds and required both a real engine start callback and resource decrease. The deterministic runner retains `-disable_ai`.

Start/cancel/complete callbacks do not supply a stable construction transaction identifier. Allocate a monotonic Province start serial, snapshot supported category levels and legal prerequisites, and clear old tokens on every start/cancellation/title loss. Completion requires the same Province/serial/payer plus an eligible level increase. An actual GUI cancel/restart confirmed fresh callbacks; no reimbursement is needed.

Native generated trigger documentation states that `free_building_slots` counts ongoing construction. Actual GUI start reported slots0/ongoing1/payer-owner1 after reservation; strict origin legality was false and originally prevented tracking. Origin still requires a slot for new categories. Native start tracking skips that already-consumed slot check while retaining holding/government/terrain/innovation/category predicates. Registered native child-on_action slot0 RED/GREEN and an actual paid GUI retest verify this distinction.

Native title-loss `scope:transfer_type = flag:granted` was observed during actual GUI Grant. Only that exact cause is voluntary; conquest, other and missing causes conservatively close impossible/free. Typed registered transfers exercise enum policy and reacquisition invalidation; they are not a real lost-war playthrough. Siege/raid child hooks use `on_siege_completion` and `on_raid_action_completion` without replacing vanilla hooks.

The prototype mirrors only Tribal Markets/Palisades1–2 and Pastures/Cereal Fields/Hill Farms1 prerequisites from installed native building definitions. Legal availability excludes treasury sufficiency: this long-term ambition can precede saving funds. Native costs/discounts remain authoritative. Actual paid start/finish used bounded `instabuild` acceleration; ordinary construction duration was not certified. Later-frame management retains Task4's bounded ten Trigger Localization(database/dynamic) notices with harmless dismissal and no other aspiration runtime/parser/data errors.

### Exact Story token ownership

A Story's historical started-Province list does not own a newer Story's pending token. Title-loss and terminal cleanup may clear the current Province Story/payer references only when they still point to that exact old Story. Registered H04 covers matching normal cleanup, old-owner title-loss isolation, no-reward terminal isolation and the newer Story's subsequent one-time reward. H03 independently initializes AI payer snapshots and clears cached GUI/Province state before invoking the native start observer.

## Evidence and reproduction

[Recovery contract](../../src/stories/holding_recovery/SPEC.md#verified-native-reservation-boundary), [H01-H06 and actual payment/cancel/finish procedures](../../src/stories/holding_recovery/tests/scenarios.md), [native child hooks](../../src/stories/holding_recovery/game/common/on_action/asp_recovery.txt), [payer/token implementation](../../src/stories/holding_recovery/game/common/scripted_effects/asp_recovery.txt), [availability predicates](../../src/stories/holding_recovery/game/common/scripted_triggers/asp_recovery.txt), [H03/H04 native fixture](../../src/stories/holding_recovery/tests/game/common/scripted_effects/asp_recovery_test.txt) and [transport controls](../../tools/game_runner/tests/test_recovery_runner.py). Installed sources: `game/common/on_action/province_on_actions.txt` and native building definitions. Run registered `recovery-regression`; real GUI payment/start/cancel/restart/finish/grant remain separate mandatory procedures.

## Implication

Keep the free-slot test at origin; the authoritative start occurs after reservation and must not require a second slot. Capture ORIGINAL scope:character before native holder fallback, never substitute the holder as payer. Compare exact Province/serial/payer/Story and supported level increase. Invalidate on start/cancel/loss; historical Province membership never permits clearing another Story token.

## Limits

Only the listed prototype construction pool is supported. Script-created work can have no original payer. H03 slot0 scripting reports ongoing0; actual GUI ongoing1/payment is separate. H04 models a suspended AI owner and new player token in native script; it is not an actual player switch or payment. Typed conquest/reacquisition is not a lost-war playthrough. Paid completion used instabuild acceleration; ordinary build duration was not certified.

[Knowledge index](README.md)

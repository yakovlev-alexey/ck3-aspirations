# Holding recovery acceptance scenarios

[Contract](../SPEC.md) · [Shared lifecycle and pledge scenarios](../../../core/tests/scenarios.md). Status: **H01–H05 registered native and mandatory GUI acceptance observed on CK3 1.20.0.4**. Stable native fixture IDs are allocated in SPEC. Reserved H01–H05 retain the reviewed plan mapping; extra coverage uses new IDs.

Procedure: disposable adult landed player save; observe enemy siege/raid, county owner, starting control, payer evidence and construction start/completion token. Snapshot stress, stewardship XP, local modifier and prestige. Force randomness only; replay natural callbacks and inspect fresh logs/screens. Never infer payer from county-holder substitution.

| ID | Given | When / manual procedure | Then / exact extra result |
| --- | --- | --- | --- |
| H01 | Observed new enemy siege/raid, personally held county, control 69 and suitable available construction | Force selection; separately test control 70, another owner's county and no buildable option | Exactly one eligible ambition at 69; zero for other-owner/control-70/no-option cases. Incident/control/category recorded, no reward or unavailable-building promise. Content remains eligible. |
| H02 | Active recovery with recorded origin and construction state | Restore control 80 alone, complete already-started work; separately new owner-funded completion plus control 80 | Control alone/old work fails. New qualifying work plus 80 succeeds once: +100 stewardship XP, -20 stress and one three-year +5% county tax modifier. Existing completed work never qualifies; no reimbursement. |
| H03 | Tracked post-origin construction with payment evidence | Cancel/restart, complete foreign-funded work or omit reliable payer; then complete genuinely fresh eligible owner-funded work | Cancelled/wrong/restarted-old/foreign/unproven-payer work never falsely qualifies. A fresh verified owner-funded start/completion may qualify; holder substitution is not payment proof. |
| H04 | Tracked construction, held county and optional pledge | Involuntary loss, voluntary grant, then transfer/reacquire and finish old work in separate cases | Involuntary loss closes free with memory; voluntary grant uses +10 private abandonment or one -100 prestige/+15 stress pledge penalty without extra private cost. Transfer/reacquisition cannot launder old construction; no silent reconquest. |
| H05 | Active recovery with milestone/repeat-incident fixtures | Try declaration after control 80 or qualifying completion; repeat raid while active and repeat fulfillment | Either achieved milestone blocks declaration. Repeat incident never stacks goals or modifiers; one active same-target track and payout only; later recovery requires fresh incident. |
| H06 | Eligible 12-month-old recovery without achieved milestones | Declare, retain/reinterpret at 8-year review, save/load and switch away through completion | Five-year pledge once; review private release free, retaining schedules 3 years without origin reset; core absence policy grants zero retrospective reward. |

The ignored Task 5 report retains exact sessions, manifests, fresh logs and screenshots; source review is separate. H06 remains a shared lifecycle procedure: Task 5 does not claim an actual recovery save/load or player-switch playthrough.

Task 5 clarification: H01's “available construction” tests legal/technology/terrain/slot/upgrade prerequisites in the explicit SPEC pool. Insufficient current treasury alone does not block a long-term ambition; a county with no legally supported next option does. Actual GUI payment remains a distinct native acceptance gate, including discounts; no fixture may infer it from current county ownership.

## Registered executable acceptance

`python -m tools.game_runner --config .local/automation/config.json run recovery-regression --repeat 1` and manual `event asp_test_holding_recovery.1` execute the same dev-only H01–H05 fixture effects. The runner requires complete numeric telemetry, exact session/request identity, unchanged disposable baseline, identical cached replay, measured native stress controls, and absent aspiration runtime diagnostics. Transport unit boundaries validate the reporter; they are not gameplay evidence.

Fixture setup changes county control, supported building tiers, and invokes the shared incident/construction/title-loss callback effects directly. Such scripted starts/finishes/transfers prove policy handling, not actual payment or a played war. Separate native GUI-funded start/finish and original payer capability evidence remains mandatory.


## Mandatory GUI and later-frame procedures

Use a disposable adult landed player baseline and `event asp_test_holding_recovery.20` to prepare an active Control 69 recovery and legal Palisades vacancy. This is scripted incident/resource setup. Choose the protection origin interpretation, open the named county's capital holding, choose its empty building slot and purchase Palisades I through **Construct**. Record actual cost, resources before/after, original native payer, start serial and callback state. Actual accepted callback reported free slots0/ongoing1/payer-owner1 and a fresh category baseline; origin's free-slot requirement must not be reapplied after reservation.

Use `.21` only to set Control 80. In the disposable session, bounded native `instabuild` and day advancement accelerate the already purchased work. Inspect actual completion and then allow the next native Story-cycle day. `.22` reuses H02's independent reward/payment assertions: Stress−20, Stewardship XP+100, modifier1, Control 80, active count0 and resources below the pre-purchase snapshot. Inspect the county modifier tooltip: +5% Holding Taxes, exactly three years from settlement. Native discounts remain authoritative. The accepted UI settlement was 4 October 1178, expiry 4 October 1181; this is not an ordinary construction-duration or three-year waiting test.

For origin safety, prepare `.20`, keep its origin open, end the exact saved Story through core impossible/no-reward, render and hover its old choices in a later frame, then click harmless Close. Require disabled stale choices, dismissal, no reward and no weak-Story/parser/data/no-valid-options errors in the fresh byte interval.

For management safety, prepare `.20`, choose an interpretation, open the native management selector and select that recovery. End the exact Story while its management window remains open; render and hover the old release option, inspect No Immediate Effects, then click to dismiss. The accepted later-frame interval contains ten Trigger Localization(database/dynamic) notices, matching Task 4's bounded diagnostic policy, and zero other aspiration runtime/parser/data errors. This does not claim a pristine log or justify a new shared guard change.

Registered H03 additionally dispatches the native construction-start child at slot0, verifies token/completion, and reports ongoing0 for its scripted occupancy model. Actual GUI ongoing1/payment is the distinct procedure above. Registered typed conquest/reacquisition and unknown-cause fixtures verify conservative closure; actual GUI Grant confirms `granted`. No real lost-war playthrough is claimed.

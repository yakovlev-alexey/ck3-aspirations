# Numeric calendar, lifecycle and terminal ordering

Status: measured-native with scripted fixture and actual-input boundaries.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

Generated script docs in the disposable test record show `is_landed` requires a county or barony; `is_ruler` alone also accepts landless title holders. The core reservation guard uses both predicates. Engine acceptance of the complete eligibility path still requires a negative in-game case.

A direct `create_story` saved reference survived an event option and actual native save/load. In the loaded campaign, a one-day tick changed the numeric `current_date` delta by exactly one while retaining the captured target, origin, next review and timed-variable state. Native serialized durations for `months = 24` and `years = 8` were 720 and 2920 days. The core stores origin and next review as numeric date values using these measured initial durations. This historical primitive probe did not exercise scheduled-review or pledge boundaries; those were measured separately by the later lifecycle fixtures and native procedures below.

The scope/calendar probe emitted `ASP_PROBE CORE EVENT_SCOPE PASS`, `CALENDAR_DAY PASS`, and `SAVE_LOAD_STATE PASS` in the recorded fresh intervals. These markers prove the primitive capabilities, not C01–C04 core gameplay. Subsequent core acceptance verified UI presentation, terminal callbacks, class caps, stale-action protection and real core-instance reload. Current registered lifecycle coverage measures P01-P06 review, declaration, settlement, suspension and replacement policy, with a separate actual-native-day calendar interval. Actual review choices, Save Game/reload, player switches and succession remain distinct acceptance procedures in the [core scenarios](../../src/core/tests/scenarios.md#mandatory-native-lifecycle-procedures); scripted dates or flags do not replace those inputs.

The actual native Save Game boundary fixture serializes `months=12` as tick360, `years=3` as tick1095 and `years=5` as tick1825 in CK3 1.20.0.4. Together with Task 2’s720/2920 probes, these establish the numeric declaration/repeat/pledge defaults without assumptions about date-unit conversion. The shared boundary runner advances an actual native day and observes current_date+1, two due review latches, declaration eligibility and exact expiry at equality.

Core progress may destroy the current story. A later `if` or even a scope switch still requires a valid current object and produced invalid-story errors after `end_story`. Query the family’s terminal predicate first and make terminal dispatch the final effect; retain suspension through that branch so returning completed goals cannot receive rewards. Native friendship is removed by death: replacement preserves the qualifying bond captured by the original death hook and revalidates the remaining consumed cause, rather than re-querying that dead relation.

Suspended public fulfillment retains persisted fulfilled state and zero Prestige economics, but transports numeric event result5 for the withheld-reward narrative. Character and county settlements both explicitly state no retrospective rewards; ordinary result1 still grants100 Prestige. Actual mixed-family return screenshots and measured zero-resource/memory checks establish the presentation separately from scripted transport.

## Evidence and reproduction

[Core contract](../../src/core/SPEC.md#task-4-lifecycle-ordering-and-state), [P01-P09 and mandatory procedures](../../src/core/tests/scenarios.md), [calendar/scope probes](../../src/core/tests/game/events/asp_core_debug_events.txt), [lifecycle fixture](../../src/core/tests/game/common/scripted_effects/asp_lifecycle_test.txt), [terminal implementation](../../src/core/game/common/scripted_effects/asp_core.txt) and [registered lifecycle tests](../../tools/game_runner/tests/test_lifecycle_runner.py). Registered `lifecycle-regression` separates logic and actual-day intervals; native Save Game/reload/switch procedures remain explicitly required.

## Implication

Use measured numeric date defaults, preserve origin/review/deadline fields, settle expiry at equality before terminal progress, and make destructive terminal dispatch the last effect. Preserve effective no-reward policy during suspended fulfillment and show the withheld-reward narrative.

## Limits

The exact duration values were measured for CK3 1.20.0.4 and specific parameters; do not extrapolate arbitrary calendar units or future versions. Artificial timestamps/suspension flags prove policy, not actual elapsed years or a player switch. Primitive scope/timer PASS markers are not family gameplay acceptance. Combined persistence has separate mandatory procedures.

[Knowledge index](README.md)

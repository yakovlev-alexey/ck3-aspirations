# Story authoring and acceptance guide

This guide turns the [repository contract](repository.md#living-specifications-and-ownership) into a review checklist. [Core](../src/core/SPEC.md) and each family's `SPEC.md` remain the behavioral authority. This is neither another product specification nor a script schema. Read the [knowledge index](knowledge/README.md) and relevant topic notes before relying on an engine capability.

## Shared acceptance checklist

- **Origin and exact target:** describe a truthful observed incident or current context, eligibility and knowledge gates, consumed cause and duplicate suppression. Record the original owner, stable target scope, Story instance ID and dates before the origin choice. Include a positive case and an excluded/previously fulfilled/duplicate case; selection forcing bypasses probability only.
- **Lifecycle:** link core's reservation, class capacity, review, declaration, suspension/return and owner-death rules. Reinterpretation preserves cause, target and age. Show actual save/reload and player-switch requirements separately from fixtures that alter dates or flags. State family exceptions explicitly rather than requiring every family to declare.
- **Completion and cancellation:** specify conjunctive milestones, terminal precedence, exact modified resource/memory deltas, no-reward cases and one-time core resolution. Repeat the callback and check zero additional payout. Test voluntary release, impossible closure, cancellation/restart where applicable and stale evidence. Distinguish vanilla action costs from added aspiration effects.
- **Stale actions:** select one exact Story while another same-family Story remains live; retire the selected Story, render/hover its saved event in a later frame, then attempt the old action. Require harmless dismissal, no wrong-target mutation or resource change and no fresh weak-link, DataFactory or no-valid-options diagnostic. Event visibility and effect guards both matter.
- **Visible state:** define the native visible Story's title key, implicit `<story_type>_desc` key and explicit visualization key. Render the exact target, cause, selected condition, age, review and private/declared state; declared families show deadline and settlement consequences. Inspect origin, active card, management, outcome and stale hover with fresh screenshots/logs. Missing keys may have no error-log line. Invisible context records have no card requirement.
- **Registered evidence:** link stable Given/When/Then scenario IDs, owning dev-only native fixtures and a name in the [runner registry](../tools/game_runner/scenarios.json). Require independent native measurements, session/request identity, replay, unchanged disposable baseline and fresh diagnostics. Add new assertions to a registered scenario or register a bounded new one; a manual event or static PASS alone is insufficient.

## Current family evidence

These references locate the required coverage; they are not blanket pass claims. Each linked procedure retains its actual-input requirements and disclosed setup/acceleration. Lifecycle/stale/presentation references may use shared core scenarios because core owns those interfaces.

| Family | Origin and target | Lifecycle | Completion and cancellation | Stale actions | Presentation | Registered regression |
| --- | --- | --- | --- | --- | --- | --- |
| `vengeance` | [`V01`](../src/stories/vengeance/tests/scenarios.md), [`V02`](../src/stories/vengeance/tests/scenarios.md) | [`P01`](../src/core/tests/scenarios.md), [`P04`](../src/core/tests/scenarios.md), [`P05`](../src/core/tests/scenarios.md) | [`V03`](../src/stories/vengeance/tests/scenarios.md), [`V04`](../src/stories/vengeance/tests/scenarios.md), [`P03`](../src/core/tests/scenarios.md) | [`C03`](../src/core/tests/scenarios.md), [`I06`](../src/core/tests/scenarios.md) | [`I05`](../src/core/tests/scenarios.md) | `vengeance-regression` [Fixture](../src/stories/vengeance/tests/game/common/scripted_effects/asp_vengeance_test.txt) |
| `holding_recovery` | [`H01`](../src/stories/holding_recovery/tests/scenarios.md) | [`H06`](../src/stories/holding_recovery/tests/scenarios.md), [`P04`](../src/core/tests/scenarios.md), [`P05`](../src/core/tests/scenarios.md) | [`H02`](../src/stories/holding_recovery/tests/scenarios.md), [`H03`](../src/stories/holding_recovery/tests/scenarios.md), [`H04`](../src/stories/holding_recovery/tests/scenarios.md) | [`C03`](../src/core/tests/scenarios.md), [`I06`](../src/core/tests/scenarios.md) | [`I05`](../src/core/tests/scenarios.md) | `recovery-regression` [Fixture](../src/stories/holding_recovery/tests/game/common/scripted_effects/asp_recovery_test.txt) |
| `personal_bond` | [`B01`](../src/stories/personal_bond/tests/scenarios.md), [`B04`](../src/stories/personal_bond/tests/scenarios.md) | [`B06`](../src/stories/personal_bond/tests/scenarios.md), [`B07`](../src/stories/personal_bond/tests/scenarios.md) | [`B02`](../src/stories/personal_bond/tests/scenarios.md), [`B03`](../src/stories/personal_bond/tests/scenarios.md) | [`C03`](../src/core/tests/scenarios.md), [`I06`](../src/core/tests/scenarios.md) | [`I05`](../src/core/tests/scenarios.md) | `bond-regression` [Fixture](../src/stories/personal_bond/tests/game/common/scripted_effects/asp_personal_bond_test.txt) |

Vengeance retains the supported-public/known-secret gate and the direct-exposure-before-observation gap. Recovery requires control plus fresh original-owner-funded construction, reservation-aware tracking and exact Story token cleanup; a typed transfer fixture is not a played war. Bonds remain private, have no declaration, and require an available native pursuit at origin; scripted relations do not satisfy actual Befriend acceptance. Shared `core-regression`, `lifecycle-regression` and `integrated-regression` references and required UI/reload/switch procedures are in [core scenarios](../src/core/tests/scenarios.md).

## New family template

Copy this outline into the new family's `SPEC.md` and write concrete prose. Remove examples/placeholders before acceptance. Reserve stable event IDs before implementation; add categories only when used. Native code remains under the family's `game/`, fixtures under `tests/game/`, and Given/When/Then cases under `tests/scenarios.md`.

```markdown
# <Family> specification
Status: <implemented/proposed>; schema and tested CK3 version.
[Core lifecycle](../../core/SPEC.md) · [Acceptance](tests/scenarios.md)

## Intent and scope
Stable family/type/namespace/category; supported owners and exclusions.

## Origin, knowledge and exact target
Observed cause/current context; eligibility and pursuit; consumption/duplicates;
fixed owner/target/instance/date; existing satisfaction and negative controls.

## State and ownership
Saved fields and stable IDs; owning scopes; documented core interfaces;
family private state; migration policy before changing saved identifiers.

## Transitions and consequences
Interpretation, progress, review/reinterpretation, completion and precedence;
release/impossibility/cancellation; declaration support or explicit exclusion;
owner death, suspension/return; one-time deltas, memories, no-reward cases.

## Presentation and compatibility
Title, implicit description and state body keys; exact condition/target/age/review;
origin/action/outcome/stale render; private/declared consequences where supported;
native sources, CK3/DLC bounds and unresolved capabilities.

## Registered and mandatory acceptance
Stable F01... Given/When/Then cases for all shared categories; registered scenario
and owning fixture links; measured positive/negative/replay controls;
actual UI/save/reload/switch procedures, screenshot/log evidence and honest limits.
```

Add a row to the current family evidence table with linked scenario IDs for each category and a registered scenario/native fixture. A shared case can cover a core rule only when the new family's applicability or exception is documented. Do not rename an existing case or saved identifier to make a new family fit.

## Static checks and native acceptance

Run `pwsh -NoProfile -File tools/check-contracts.ps1` for source-only evidence/key checks, or the normal dev/release `tools/check.ps1` after assembly. `tools/tests/run.ps1` includes the checker boundary tests using disposable fixtures. The checker discovers story directories, validates the evidence table's category references and registered names, checks linked scenario IDs/native fixture paths and visible Story keys (including nested native folders), and rejects broken/nonportable knowledge links. Origin/target and terminal/cancel coverage must include owning-family scenarios; other categories may reuse core. Another family's scenarios or fixtures cannot satisfy that row. It accepts invisible context Stories without player-facing keys.

The table's column structure is an evidence index used by this check; narrative SPEC headings and rules remain ordinary prose. A row can link an unverified required procedure, so a static pass proves discoverability and key presence only. It does not establish correct scopes, payment, knowledge, date arithmetic, native rendering, exact UI selection or gameplay success. The [runner contract](../tools/game_runner/SPEC.md) owns supported operations and live evidence requirements. Raw evidence stays ignored; knowledge preserves portable reproduction and qualified observations.

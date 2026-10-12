# Holding recovery specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Runtime implementation is pending.

[Core lifecycle and balancing](../../core/SPEC.md) · [Product intent](../../../docs/design.md) · [Acceptance scenarios](tests/scenarios.md)

### Recovery of a damaged holding

**Cause:** a personally held county loses control after an enemy siege or raid observed while the mod is active. The event records the county, the incident, and the control value. Require control below 70 and at least one available, appropriate construction or upgrade that the player can undertake there.

**Class:** ambition.

**Objective:** restore control to at least 80 and complete one eligible construction or upgrade begun after the aspiration starts and paid for by the owner. Both conditions must be true while the county remains personally held. The origin event names the eligible building categories, rather than promising a specific unavailable building. Buildings already complete or already under construction do not satisfy the construction condition.

The narrative distinguishes a desire to protect inhabitants from a desire to restore family prestige or income. These interpretations influence wording and emotional consequences without requiring separate construction systems.

**Invalidation:** loss of the county prompts reconsideration. An involuntary loss closes the aspiration without an uncontrollable-loss penalty and leaves a memory. A voluntary grant instead uses the ordinary abandonment policy, including any applicable pledge penalty. The prototype does not silently replace the aspiration with an unimplemented reconquest family. A later recovery requires a fresh qualifying incident.

**Reward:** modest stewardship experience and a temporary local recovery modifier. The modifier cannot stack with another instance of itself. A repeat incident while the same aspiration is active adds context rather than another reward track.

## State and ownership

Stable family flag: `holding_recovery`; class: ambition. Store county, origin incident/control, chosen interpretation, owner at origin, eligible building categories, and a construction-start token proving new owner-funded work after origin. Record uninterrupted ownership and qualifying completion; neither a substituted county-holder scope nor completion alone proves payment.

Character entry: `asp_start_holding_recovery_effect = { COUNTY = <county title> }`; validate incident, county ownership/control and eligible construction, consume origin, reserve capacity and retain the created story reference. Story interfaces are `asp_holding_recovery_check_progress_effect` and `asp_holding_recovery_resolve_effect = { OUTCOME = <flag> REWARDS = <flag> }` through core dispatch.

Namespace: `asp_holding_recovery`; dev namespace: `asp_test_holding_recovery`. Task 1 allocates no event IDs. Planned files use `game/common/.../asp_holding_recovery.txt`, including the non-stacking county modifier, `game/events/asp_holding_recovery_events.txt` and `game/localization/english/asp_holding_recovery_l_english.yml`. Shared fields and operations are owned by core.

## Parameters, transitions and consequences

Origin requires personally held county control below 70 after an observed enemy siege/raid and an available appropriate construction/upgrade. Apply core's 50% major-event chance and ambition occupancy multipliers. Content remains eligible. Repeat damage while active adds context without another reward track; consumed incidents and family/target guards prevent farming.

Fulfillment requires control at least 80 and one eligible owner-funded construction begun after origin and completed while the county remains personally held. Existing, in-progress-at-origin, cancelled, foreign-funded and ownership-interrupted work never qualifies. A fresh construction token is needed after cancellation or ownership interruption; restoring ownership cannot revive invalid evidence.

Protection of inhabitants, family prestige and income are narrative interpretations of the same conjunctive objective. Loss of county prompts reconsideration: involuntary loss closes free with memory and excuses an uncontrollable pledge; voluntary grant uses abandonment/pledge policy. No target substitution or reconquest family. Later recovery requires a new qualifying incident. Owner death and switching follow core; absent-period completion grants no retrospective rewards.

Fulfillment removes 20 stress, adds 100 stewardship lifestyle experience and a local +5% tax modifier for 3 years once. Modifier never stacks; no construction reimbursement. Early private abandonment costs core's 10 stress; review release and uncontrollable impossibility are free unless an active pledge's rules apply.

Declaration uses core's age/deadline policy and requires both control below 80 and no qualifying completed construction. A nearly completed objective cannot declare for an immediate bonus. Public success adds 100 prestige once; failure/withdrawal applies -100 prestige and +15 stress once, taking precedence over simultaneous private abandonment costs.

## Presentation and compatibility

Explain incident, recorded control, exact two-part condition and eligible building categories without naming an unavailable building. Show ownership loss and voluntary grant consequences. Use English localization and game-provided art references; no original or extracted art in Task 1.

Required surfaces: siege/raid, construction start/completion, title ownership callbacks, county control and modifiers, stories/memories. Verify payment, calendar and uninterrupted-ownership evidence before implementation; never infer payment from holder substitution. CK3 1.20.0.4 source inspected; runtime acceptance pending. No DLC-dependent branch promised; schema 1 and core migration policy apply.

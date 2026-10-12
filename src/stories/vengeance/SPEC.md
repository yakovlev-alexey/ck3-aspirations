# Vengeance specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Runtime implementation is pending.

[Core lifecycle and balancing](../../core/SPEC.md) · [Product intent](../../../docs/design.md) · [Acceptance scenarios](tests/scenarios.md)

### Vengeance for a loved one

**Cause:** a close relative, spouse, friend, or best friend is killed by a culprit whose responsibility is known to the player character. A close relative means a parent, child, or sibling for the prototype. The narrative names both the victim and the responsible character.

The culprit must be someone other than the owner. Exclude a victim who was the owner's rival or nemesis; kinship alone must not force grief for a hated relative. Do not generate the aspiration from a killing deliberately caused by the owner.

The existence of an engine-level killer reference is not evidence that the character knows a secret. Public battlefield responsibility or established character knowledge can qualify. If responsibility is concealed, do not offer a named revenge target. The prototype does not add a murder investigation system. Later disclosure can create the aspiration only when a verified knowledge event supplies the connection.

**Class:** ambition.

**Interpretations:** personal vengeance, requiring the owner's recorded responsibility for the culprit's death; or public accountability, requiring the owner to acquire custody of the culprit after the aspiration begins. Imprisonment does not become lawful merely because an aspiration exists, and the mod grants no free imprisonment reason or casus belli. Accountability is unavailable if the culprit is already the owner's prisoner.

Forgiveness is a distinct reconsideration outcome rather than a disguised execution reward. Compassionate characters can find it emotionally easier; Vengeful characters find it harder. Acceptance testing must demonstrate a conflicting-trait case in which killing grants closure but does not erase vanilla personality stress.

**Invalidation:** unrelated death of the culprit ends the pursuit through an unresolved-closure event. The culprit is not replaced with an heir. Death caused by the owner is evaluated for fulfillment before generic target-death invalidation. The victim's death cannot be replayed as another aspiration.

**Reward:** emotional closure; public accountability may also grant modest prestige. A secret killing grants no public recognition simply because the aspiration was fulfilled. A public vengeance pledge rewards known fulfillment only.

For a personal-vengeance pledge, the declaration explicitly requires publicly attributable fulfillment, such as an execution or a recorded battlefield killing. Secret fulfillment still ends the private aspiration and grants its ordinary closure, but closes the unverifiable pledge under the withdrawal policy. Show this consequence at declaration, so the player can choose secrecy with a known reputational cost.

## State and ownership

Stable family flag: `vengeance`; class: ambition. Store victim, known culprit, originating death incident, interpretation, responsibility evidence and public-attribution state on this instance. The target is never replaced with an heir. Core owns age, capacity, pledge and resolution latches.

Character entry: `asp_start_vengeance_effect = { VICTIM = <character> KILLER = <character> }`; revalidate knowledge and eligibility, consume origin, reserve capacity, retain the newly created story reference and open interpretation. Story interfaces are `asp_vengeance_check_progress_effect` and `asp_vengeance_resolve_effect = { OUTCOME = <flag> REWARDS = <flag> }` through core dispatch.

Namespace: `asp_vengeance`; dev namespace: `asp_test_vengeance`. Task 1 allocates no event IDs. Planned native files use `game/common/.../asp_vengeance.txt`, `game/events/asp_vengeance_events.txt` and `game/localization/english/asp_vengeance_l_english.yml` when implemented. Shared fields and operations come from core; no other family state may be read or mutated.

## Parameters, transitions and consequences

Use core's major-event 50% base and ambition occupancy weights, with a Vengeful multiplier of 1.5 and final chance at most 90%. Content does not suppress contextual bereavement. Retain the core incident/cap guards; one family/target active instance only.

Personal vengeance checks recorded owner responsibility before generic target-death invalidation. Accountability requires newly acquired custody after origin and is unavailable at creation when custody already exists. Forgiveness is a distinct outcome with no execution reward. Unrelated target death produces impossible unresolved closure, no fulfillment payout, and excuses the impossible pledge. Voluntary owner actions do not automatically excuse it. Owner death and switching follow core; an absent owner's fulfilled goal closes without retrospective rewards.

Ordinary fulfillment removes 20 stress once. Accountability adds 100 prestige once; personal vengeance never adds this accountability reward. Early private release costs 15 stress for Vengeful, 5 for Compassionate without Vengeful, otherwise 10; normal review and uncontrollable impossibility are free. Vanilla stress from conflicting traits remains. A still-active pledge takes precedence over private abandonment costs.

Vengeance permits declaration only under core's minimum age and milestone rules; target must not already be in custody. The personal-vengeance pledge explicitly requires publicly attributable death (for example execution or recorded battlefield responsibility). Secret fulfillment grants private closure while settling the unverifiable pledge as withdrawn: -100 prestige and +15 stress once, no public success bonus. Publicly known success grants core's pledge +100 prestige once in addition to the private result.

## Presentation and compatibility

Origin text names the victim and only a verified known culprit; no hidden-killer disclosure or investigation system. Explain personal vengeance, accountability, forgiveness, all costs and public attribution before commitment. Show unresolved closure distinctly from fulfillment. Use English localization and vanilla art references; no extracted assets.

Required surfaces: death and prisoner on-actions, knowledge predicate/disclosure event, owner-attribution evidence, stories and memories. Knowledge and responsibility probes are prerequisites, not facts inferred from an engine killer reference. CK3 1.20.0.4 source inspected; runtime acceptance pending, no DLC-dependent branch promised. Saved identifiers follow schema 1 and core migration policy.

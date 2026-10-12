# Personal bond specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Runtime implementation is pending.

[Core lifecycle and balancing](../../core/SPEC.md) · [Product intent](../../../docs/design.md) · [Acceptance scenarios](tests/scenarios.md)

### Closeness to a particular person

**Cause:** an eligible adult whom the owner has a concrete reason to know, such as a court connection, an existing positive relationship, or a recent recorded shared event. Both characters must be alive and within diplomatic reach. Do not select an arbitrary stranger solely because they are an efficient scheme target.

**Class:** desire.

**Interpretations:** friendship, satisfied by a new friend or best-friend relationship; or romantic closeness, satisfied by a new lover or soulmate relationship. Romantic candidates must satisfy the game's existing age, attraction, and relationship eligibility rules. Lustful increases the romantic interpretation's weight without forcing it for every character or every candidate.

The desired relationship must not already exist. At least one supported way to pursue it must be available at creation. Use existing interactions, activities, and events; the mod does not grant friendship, attraction, or access to a locked scheme just to make a goal achievable.

**Invalidation:** target death closes the desire through an appropriate loss event. Temporary diplomatic unavailability keeps it active until normal review; permanent incompatibility allows cost-free reconsideration. A target becoming a rival prompts a choice to relinquish the desire or retain it, rather than automatically assigning a different person.

**Reward:** emotional satisfaction and a memory. Friendship can add a small diplomacy experience reward. Romantic success is private by default and cannot be proclaimed as a public pledge in the prototype.

## State and ownership

Stable family flag: `personal_bond`; class: desire. Store selected person, truthful concrete connection, origin incident, interpretation and relationship-at-origin evidence. Preserve the person and origin on reconsideration. Core owns slot, age, cooldown and one-time resolution.

Character entry: `asp_start_personal_bond_effect = { TARGET = <character> MODE = <friendship|romance flag> }`; validate adult/alive/reachable participants, existing connection, relationship eligibility and an available supported pursuit, consume origin, reserve capacity and retain the created story. Story interfaces are `asp_personal_bond_check_progress_effect` and `asp_personal_bond_resolve_effect = { OUTCOME = <flag> REWARDS = <flag> }` through core dispatch.

Namespace: `asp_personal_bond`; dev namespace: `asp_test_personal_bond`. Task 1 allocates no event IDs. Planned files use `game/common/.../asp_personal_bond.txt`, `game/events/asp_personal_bond_events.txt`, `game/localization/english/asp_personal_bond_l_english.yml` when implemented. Shared fields and operations are owned by core.

## Parameters, transitions and consequences

Quarterly selection uses core's base 20%, desire occupancy `1.0 / 0.6 / 0.3 / 0.1 / 0.1 / 0` and twelve-month routine cooldown. Lustful multiplies romantic weight by 1.5; it never forces romance or overrides attraction, age, relationship eligibility or reach. Activation/succession may consider current circumstances without inventing a historical encounter.

Friendship requires a new friend or best-friend relationship; romance requires a new lover or soulmate relationship. An already satisfied desired relationship is ineligible. Use existing interactions, activities and events; no granted relationships or locked schemes. Reinterpretation never makes an existing relationship an instant completion reward.

Target death produces loss closure free, without fulfillment reward. Temporary diplomatic unavailability retains the desire until normal review; permanent incompatibility permits free reconsideration. A new rivalry prompts retain/relinquish rather than replacing the target. Owner death and switching follow core; completion during absence closes without retrospective reward.

Fulfillment removes 10 stress and records memory once. Friendship adds 50 diplomacy lifestyle experience; romance has no friendship XP reward. Early private abandonment costs 5 stress; review-age release and uncontrollable impossibility are free. Initial review is 24 months and retaining schedules twelve months later without resetting origin. No personal-bond public pledge is supported; romantic success stays private.

## Presentation and compatibility

Origin explains the concrete connection and chosen person, pursuit possibilities and interpretation without exposing secrets. Outcome text differentiates friendship, romance, loss and relinquishment. No dev controls or raw identifiers in release; English localization only, vanilla art references without redistribution.

Required surfaces: relationship set/remove/death callbacks, age/attraction/eligibility/reach predicates, stories, memories and bounded maintenance. Availability probes must establish a real pursuit route. CK3 1.20.0.4 source inspected; runtime acceptance pending. No DLC-dependent branch promised; schema 1 and core migration policy apply.

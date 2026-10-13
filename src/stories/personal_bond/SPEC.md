# Personal bond specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Task 6 implements this family in native CK3 script. Registered native B01–B07 and mandatory actual Befriend action/outcome acceptance are complete; exact source maps and diagnostic intervals are retained in ignored task evidence.

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

Namespace: `asp_personal_bond`; dev namespace: `asp_test_personal_bond`. Implemented files use `game/common/.../asp_personal_bond.txt`, `game/events/asp_personal_bond_events.txt`, `game/localization/english/asp_personal_bond_l_english.yml` when implemented. Shared fields and operations are owned by core.

## Parameters, transitions and consequences

Quarterly selection uses core's base 20%, desire occupancy `1.0 / 0.6 / 0.3 / 0.1 / 0.1 / 0` and twelve-month routine cooldown. Lustful multiplies romantic weight by 1.5; it never forces romance or overrides attraction, age, relationship eligibility or reach. Activation/succession may consider current circumstances without inventing a historical encounter.

Friendship requires a new friend or best-friend relationship; romance requires a new lover or soulmate relationship. An already satisfied desired relationship is ineligible. Use existing interactions, activities and events; no granted relationships or locked schemes. Reinterpretation never makes an existing relationship an instant completion reward.

Target death produces loss closure free, without fulfillment reward. Temporary diplomatic unavailability retains the desire until normal review; permanent incompatibility permits free reconsideration. A new rivalry prompts retain/relinquish rather than replacing the target. Owner death and switching follow core; completion during absence closes without retrospective reward.

Fulfillment removes 10 stress and records memory once. Friendship adds 50 diplomacy lifestyle experience; romance has no friendship XP reward. Early private abandonment costs 5 stress; review-age release and uncontrollable impossibility are free. Initial review is 24 months and retaining schedules twelve months later without resetting origin. No personal-bond public pledge is supported; romantic success stays private.

## Presentation and compatibility

Origin explains the concrete connection and chosen person, pursuit possibilities and interpretation without exposing secrets. Outcome text differentiates friendship, romance, loss and relinquishment. No dev controls or raw identifiers in release; English localization only, vanilla art references without redistribution.

Required surfaces: relationship set/remove/death callbacks, age/attraction/eligibility/reach predicates, stories, memories and bounded maintenance. Availability probes must establish a real pursuit route. CK3 1.20.0.4 native scheme eligibility and scripted family outcomes observed. No DLC-dependent branch promised; schema 1 and core migration policy apply.

## Task 6 stable allocations

Runtime asp_personal_bond.1 owns origin, .2 terminal, .3 rival/incompatibility reconsideration. Dev asp_test_personal_bond.1 runs shared B01–B05; .10 prepares real Befriend UI, .11 accelerates only an existing native scheme, .12 asserts its outcome. The invisible context Story type is asp_personal_bond_context_story; it owns no aspiration slot or reward. IDs are never repurposed.

## Implemented contextual selection and limited pursuit routes

The supported friendship route is native Befriend: `can_use_befriend_scheme_trigger` plus `can_start_scheme` for Befriend. The supported romantic route is native Seduce: mutual `is_attracted_to_gender_of` plus `can_start_scheme` for Seduce. The latter evaluates the native scheme's age, imprisonment, capacity, target, cooldown and relationship restrictions. Player-only cynical seduction without attraction does not qualify for this personal desire. No activity route, shared-event encounter, DLC-specific exception, perk grant, attraction grant or relationship grant is implemented. Native interaction/source inspection is distinct from the mandatory real UI pursuit.

A concrete connection is a current courtier/guest or a native Potential Friend, Friend, Best Friend, Lover or Soulmate relationship. Opinion alone does not qualify. Current court connections may seed a truthful acquaintance; no historical meeting is invented. Desired Friend/Best Friend or Lover/Soulmate relations reject their respective interpretation. Both participants must be living adults within native diplomatic range, and the owner must be the adult landed current player.

Each owner retains one invisible `asp_personal_bond_context_story` per observed person. It is not an aspiration: no core schema, slot, reward, management entry or inheritance. Fields are target, a signature of court/potential-friend/friend/best-friend/lover/soulmate context, monotonic context serial, and consumed serial. The first observation starts serial1. Only a changed signature or an actual native court join/leave transition renews it; observing the same court each quarter never renews it. A join/leave callback marks the old signature stale, then the next observation records current truth. Records are private to their owner, so a different ruler cannot share or overwrite consumption.

Quarterly selection works only with the owner's existing context records, current court/guests and five positive relation lists; it never iterates the world. It filters to reachable adults with at least one native supported pursuit, excludes duplicate family/target, chooses one person, then weights only the eligible interpretations10:10 (romance15 for Lustful). No trait forces romance. The selected eligible context is consumed before its20/12/6/2/2/0 percent probability roll, including a failed roll; only a created desire starts the360-day routine cooldown. Debug forcing bypasses only probability. Capacity, cooldown, target, connection, pursuit and consumption guards remain mandatory. Unchanged consumed contacts cannot propose again after abandonment or fulfillment. A genuinely observed context change can later make the same person eligible, subject to cooldown.

The desire saves fixed person, origin signature/incident, interpretation, and evidence that its desired relation was absent at creation. Reinterpretation checks a currently available native pursuit and rejects an already satisfied relationship; it preserves target, origin and slot, and uses core's due-review postponement. Daily family maintenance and additive relation callbacks dispatch terminal progress through core. Temporary distance, imprisonment or occupied scheme capacity retains the desire. Mutual-attraction loss, Celibate or the native permanent seduction blocker permits free romantic reconsideration; no temporary scheme failure is treated as permanent. Rival/Nemesis transitions latch one choice until that relation changes; retaining never silently retargets. Target death closes impossible/free. All public declaration predicates remain false for bonds, including old desires.

Core alone gives the−10 Stress fulfillment or native-modified base5 early abandonment and ends the Story. Family fulfillment adds exactly50 Diplomacy XP for friendship, zero for romance, and one appropriately private memory. Best Friend and Soulmate satisfy the respective modes. Suspended completion records memory with effective `REWARDS=none`, so no retrospective Stress/XP or visible success event. Native daily maintenance remains bounded by owned aspirations; relation hooks handle either participant without relaxing core ownership.

## Registered and mandatory acceptance

`bond-regression` invokes the shared dev effect also exposed by `event asp_test_personal_bond.1`. Complete integer telemetry, session/request/date/baseline, cached replay and absence of aspiration runtime/parser/DataFactory diagnostics are mandatory; a case flag alone cannot pass. B01–B05 covers native locked/unlocked/pursuit controls, context exclusions, exact rewards/memories, invalidation, chances/cooldown/consumption and Content/Lustful. B06 adds Best Friend/Soulmate, independent native base5 cost, cap/cooldown rejection,24-month free release,360-day retention, suspension and old-bond no-pledge. B07 adds already-achieved reinterpretation rejection and the actual bounded routine selector/unchanged observation serial. Artificial date stamps and scripted relations establish these state rules, not an actual switch, elapsed year or played relationship action.

Dev `.10` prepares an eligible court Potential Friend and reserves a friendship desire. Perk, generated contact and potential friendship are explicit controlled setup. The player must actually choose the origin, start native Befriend and confirm its interaction. `.11` rejects a missing exact native scheme and accelerates only that already-started scheme via native progress; it never sets a relationship. `.12` requires the actual Friend relation, exact target memory, released slot,−10 Stress/+50 XP and recorded exact native scheme before acceleration. Keep screenshots and fresh logs for that mandatory UI acceptance. Full ordinary scheme duration, natural emergence statistics, actual bond-specific save/load and real player-switch coverage are not claimed by the scripted fixture.

Task 6 additionally reserves dev `.13` for rival render setup, `.14` for the shared retained-rival assertion; `.16` for exact stale Story retirement, `.17` for harmless post-click assertions, `.18` for exact management render setup; `.20` for target-loss render setup and `.21` for its no-reward assertion. `.15` and `.19` are unallocated. No existing ID is repurposed.

Origin and rival windows always have a native `fallback=yes` Close with no effect. The native UI also displays this harmless Return while regular choices are valid; it closes the prompt and keeps the reserved desire. After stale weak Story links invalidate regular actions, it still guarantees a valid dismissal. Eligibility and effect guards still protect all regular actions. The shared stale setup/post-click fixture and mandatory later-frame render prove this boundary; a no-valid-options diagnostic is failure even when resources stay unchanged. Native progress acceleration in `.11` is100 units per call; the accepted11-month baseline needed four increments, not an assumed100-percent single call.

The visible native Story defines implicit `asp_personal_bond_story` and `asp_personal_bond_story_desc` keys as well as its `Story.MakeScope` body. A focused exact-key regression and actual Situations render verify title/description/target/age/review; native logs alone cannot detect raw missing-key text.

Successful reinterpretation is shared registered B07 coverage: friendship→romance before review and romance→friendship at due review. Both supported pursuits and absent desired relationships qualify on the exact adult court contact. Each direction exposes observed before/after mode, same Story/target, instance/allocation/origin/context signature/incident/serial/consumed/cooldown deltas, active desires, Stress/XP/memory deltas and next-review/notified state. Required changes are1→2 and2→1; all identity/consumption/resource deltas are0 and active desires remain1. Non-due review stays720 days; due reinterpretation clears the reminder latch and schedules360 days while preserving origin. The existing achieved-Friend rejection remains. Date/perk/contact setup is artificial; this does not claim actual UI reinterpretation or elapsed review time. Original `origin_preserved` remains the retention-only field; reinterpretation has its own independent measurements.

Task 7 card presentation uses native Story.Custom to state the exact selected Friend/Best Friend or Lover/Soulmate objective. Target, original age, review and private state remain in Story.MakeScope context. Focused branch/key checks and both actual mode renders are required; no pursuit, reward or reinterpretation behavior changes.

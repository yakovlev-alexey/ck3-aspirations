# Vengeance specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Task 3 implements the native family; acceptance evidence is recorded below. Task 4 first-story lifecycle implementation and native evidence are accepted; combined mixed-family acceptance is owned by core scenarios.

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

Use the [writing guide](../../../docs/player-facing-writing.md): grief supplies the origin tension; personal vengeance, custody and forgiveness have distinct roleplay choices and native option flavor. No scene invents a witnessed killing, funeral or public disclosure. Conditions and conditional future rewards remain in option effect descriptions and labeled cards; Stress relief is labeled as a base value subject to Stress Loss modifiers. Memories retain the original participant getters and all perspective variants. The shared personal-vengeance memory's third-person text remains neutral about owner responsibility, because the same type serves secret and public fulfillment.

The terminal event's display-only `immediate` branches use the existing numeric outcome and accountability boolean to report already settled fulfillment, forgiveness/release or unresolved loss. No effect is replayed and no ended Story is traversed. Normal family terminal events are emitted only under the existing normal-reward/current-player guard; absent completion produces no family success event. Private reward summaries cannot imply a public pledge bonus, and no-reward endings remain explicit in the effect surface. Native editorial comparison supplements V01–V06 and core I05; source checks cannot certify placement or quality.

Origin text names the victim and only a verified known culprit; no hidden-killer disclosure or investigation system. Explain personal vengeance, accountability, forgiveness, all costs and public attribution before commitment. Show unresolved closure distinctly from fulfillment. Use English localization and vanilla art references; no extracted assets.

Required surfaces: death and prisoner on-actions, knowledge predicate/disclosure event, owner-attribution evidence, stories and memories. Knowledge and responsibility probes are prerequisites, not facts inferred from an engine killer reference. CK3 1.20.0.4 source inspected; Task 3 acceptance is recorded below; Task 4 lifecycle acceptance is separate, and no DLC-dependent branch is promised. Saved identifiers follow schema 1 and core migration policy.

## Task 3 stable event allocations

Reserve `asp_vengeance.1` for origin interpretation, `.2` for terminal narrative, and `.10` for post-death candidate processing. Dev IDs: `asp_test_vengeance.1` is the shared V01-V06 regression entry, `.10` is the four-case knowledge probe, `.20` prepares an actual player execution, and `.21` asserts its observed action result. Never repurpose these IDs.

Task 3 also reserves runtime `asp_vengeance.11` for deferred fixed-target validation. Pending records `asp_vengeance_pending` and consumed records `asp_vengeance_consumed` are owner-local victim reference lists captured by the death child hook; pending records never contain a hidden culprit. Only the current eligible player receives them. `asp_vengeance_custody_available` preserves initial lack of custody; `asp_vengeance_owner_responsible` records an exact target death callback with that owner as killer; `asp_vengeance_public_fulfillment` marks verified public death reasons.

Validated knowledge route: explicit public death reasons with `public_knowledge=yes`, or a matched `any_known_secret` murder secret identifying the same owner and victim. Quarterly delayed checks examine retained post-activation candidates only. Direct public exposure before a known-secret observation is unsupported: CK3 1.20.0.4 removes the secret from the known-secret iterator and exposes no generic read-side killer-knowledge predicate or additive disclosure hook. No vanilla secret type is overridden. This conservative gap can miss a public revelation; it never authorizes exposing hidden responsibility.

Dev `asp_test_vengeance.30` and `.31` reserve visual unresolved-closure setup and observation after the separate actual execution acceptance.

Terminal event context copies known victim/culprit references and uses numeric outcome values (fulfilled 1, forgiven 2, impossible 3, abandoned 4) plus a boolean accountability indicator, because native event-value transport cannot copy flag variables. Persisted aspiration interpretation/outcome flags and schema 1 remain unchanged. Natural deaths without a supplied killer do not create pending killing candidates.

Dev `.32` is reserved for scripted visual custody after `.30` setup and actual accountability choice; the real GUI execution remains the separate mandatory action check. The custody on-action runs in its own effect chain, so caller assertions use exact victim-bound memories/rewards rather than assuming child event values return to the caller.

Own-act death evidence is recorded on matching stories owned by the supplied killer, including a former player. This preserves attribution for Task 4 return handling without resuming absent-owner events or rewards. Full switch/return policy remains Task 4 acceptance. Story-card localization uses the validated case-sensitive native `Story` getter.

## Task 3 observed acceptance

V01-V06 passed the registered native regression in CK3 1.20.0.4; the documented manual `.1` entry uses identical fixtures. The actual vanilla Execute UI action on a Compassionate player produced +100 Stress, with a separate aspiration -20 and exactly one memory. Native cards show the fixed cause/target, exact chosen condition, age and reflection interval; personal, accountability, forgiveness and impossible terminal descriptions were visually verified. Direct public exposure before observation remains unsupported. Task 4 acceptance below covers scheduled reflection, pledge, replacement and switch/return; cross-family acceptance remains a later stage. See the family scenarios for reproducible commands and required manual steps.

## Task 4 first-story lifecycle

Core now supplies the family’s review, retention, private reinterpretation, minimum-age declaration, once-only settlement and suspension/return ordering. Family `asp_vengeance_can_declare_trigger` requires an implemented interpretation, a living culprit outside custody and no recorded irreversible owner responsibility. `asp_vengeance_has_terminal_progress_trigger` reports exact dead-target or newly acquired accountability custody to core before terminal dispatch. Imprisonment callbacks use core refresh so they cannot bypass deadline precedence.

A major incident at three ambitions captures an explicit replacement offer using the same 0.4 occupancy tuning value. Origin remains consumed on cancellation. Cause revalidation precedes old-story release and includes exact owner, culprit, verified knowledge, range and duplicate guards; the death hook’s original qualifying bond is retained rather than querying a friendship already removed by native death. Core owns all old-ambition costs and reservation limits.

The family story checks maintenance daily, while AI owners only suspend. Owner attribution continues to be recorded for a former player, without processing their action events or rewards. Private known-secret discovery is not public fulfillment. Public causes retain the Task 3 whitelist; the direct exposure-before-observation gap remains unchanged. Dev `asp_test_vengeance.2` calls the same P01-P06 lifecycle fixture as registered `lifecycle-regression` and core `.30`; it is separate from the stable `.1` family regression.

Origin and reconsideration accountability visibility use character-context `asp_vengeance_event_can_choose_accountability_trigger = { STORY = <event-held reference> }`. It validates the link before entering the Story-scoped family predicate. Ended native modal references cannot expose an eligible action or trigger missing-target/weak-Story errors while rendering.

The existing origin Close option is a native fallback: it appears when no interpretation remains valid, including a queued origin whose exact Story has ended. It never acts on state and does not introduce a close choice while normal interpretations are valid.

Task 7 combined replacement tooltips exclude invisible context Stories with a native schema-presence branch before reading aspiration fields. Registered integrated-regression exercises mixed caps and rejects native tooltip diagnostics.

# Core specification

Status: authoritative living contract migrated from the approved 2026-10-12 design. Task 2 native core and C01–C04 gameplay acceptance are complete for the development prototype. Schema: `1`. Core owns cross-story state; family modules cannot mutate one another's private state.

[Product intent](../../docs/design.md) · [Repository contract](../../docs/repository.md) · [Acceptance scenarios](tests/scenarios.md)
## Core model

Each aspiration has an owner, an originating circumstance, a target, an interpretation, explicit completion conditions, an origin date, a next review date, and a terminal outcome. Public declaration adds an audience, a deadline, and a reward or penalty policy. Store the relevant characters and titles as references, not names or a changing selection of suitable targets.

The three player-facing terms are:

| Term | Meaning | Initial review age |
| --- | --- | --- |
| Desire | A concrete near-term personal undertaking | 24 months |
| Ambition | A sustained direction for part of the character's life | 8 years |
| Declared aspiration | A public commitment attached to an existing eligible aspiration | Explicit deadline from declaration |

Public commitments are a visibility and commitment state, not another set of goal slots. A revenge ambition and a relationship desire can coexist and make incompatible demands on the player.

Use **Ambition** for the long-term category, **Declared** for its public state, and **Declare intention** for the action; supporting prose can say public commitment or pledge. The Ambition category does not require the Ambitious trait. These terms describe a secular commitment; a religious variant may use faith-specific language when such content is added.

## Emergence and interpretation

Events create aspirations automatically when a meaningful, eligible circumstance passes a weighted selection. The first event explains the cause and offers interpretations of that same circumstance. It is not a shop of unrelated goals or rewards. The aspiration occupies its slot before the interpretation event; choosing an interpretation does not create another instance or grant a reward.

An interpretation defines what satisfaction means. For a killing, personal vengeance can require personally causing the culprit's death, while public accountability can require taking that culprit prisoner through an existing valid game action. Options retain CK3's normal consequences and show any additional personality stress before selection. The player can decline or abandon the impulse through an explicit option; before the normal review age, that uses the same modest abandonment cost as later management.

Circumstances establish eligibility. Traits adjust selection weights, wording, interpretations, and emotional costs. A single trait must not repeatedly assign the same generic task. Content suppresses spontaneous aspirations for greater wealth, rank, or power; it does not suppress contextual protection, recovery, love, or reactions to bereavement. Personality changes can prompt reconsideration but never silently rewrite the chosen objective.

A target must be alive or otherwise valid, relevant to the character, and meaningfully reachable when selected. Do not create an aspiration that is already fulfilled. Preserve the selected target and starting conditions so later changes cannot move the goalposts.

The prototype observes new events after activation. It does not reconstruct every historical grievance from a loaded save. At activation or succession, current circumstances may supply an eligible relationship desire, with a truthful explanation that does not invent a past meeting.

## Population and cadence

Normal density should be approximately one or two ambitions and one to three desires. Hard caps are three ambitions and five desires. The caps are ceilings, not targets to fill.

Routine relationship selection runs quarterly for the player only. Start with a 20% chance when a valid candidate exists and apply an occupancy multiplier: 1.0 with no active desires, 0.6 with one, 0.3 with two, 0.1 with three or four, and zero with five. Allow at most one routine new aspiration in twelve months. Major new losses use contextual event selection and may bypass that routine cooldown, but never the hard cap.

For a major loss, use an initial 50% base selection chance, with a 1.5 multiplier for Vengeful in the vengeance family and a maximum final chance of 90%. Apply ambition occupancy multipliers of 1.0, 0.7, and 0.4 with zero, one, and two active ambitions. These probabilities are test parameters, not claims about human psychology.

At the ambition cap, a qualifying major event may offer to replace a chosen existing ambition, showing its ordinary abandonment cost, or leave the existing ambitions intact. It never silently removes an old aspiration. Closely related notifications from one incident should be consolidated.

Only one active aspiration in the same family may target the same person or county. The same originating incident cannot generate repeated rewards or proposals. Completion, abandonment, and invalidation all consume that incident. A new eligible incident is required to revisit that target; routine selection additionally respects the twelve-month cooldown.

## Lifecycle and reconsideration

The lifecycle is: originating circumstance, active aspiration with an interpretation event, pursuit, optional declaration, then fulfillment, abandonment, reconsidered closure, or invalidation. Every terminal transition grants its effects once, records the outcome, removes active management options, and frees the slot.

Unproclaimed aspirations have no mandatory completion deadline and incur no passive, accumulating stress merely for remaining unfinished. At the review age, offer retain, release, or a supported reinterpretation. Retaining schedules the next review in twelve months for a desire or three years for an ambition. Reinterpretation preserves the original cause and age; it is not a cooldown reset or a new reward opportunity.

Before the review age, voluntary abandonment uses base 5 stress for a desire or base 10 for an ambition; CK3 applies the owner’s Stress Gain modifiers to the amount added. The action tooltip must identify the base value and the modifier effect. For early release of vengeance, use 15 for Vengeful characters, 5 for Compassionate characters without Vengeful, and 10 otherwise. At the scheduled age, release has no added penalty. Demonstrably impossible circumstances permit cost-free closure regardless of age. Costs for an active public pledge are governed by its public commitment, not erased by reaching the personal review age.

The current player controls interpretation and reconsideration events. On owner death, personal aspirations end; an heir does not inherit active obligations automatically. Switching to another living character suspends pursuit processing and rewards for the former player's personal aspirations; owner-death cleanup still applies. On returning, validate them and present any necessary review before resuming. Objectives already achieved during the absence close with a memory and no retrospective reward. An expired pledge resolves once on return before its remaining private aspiration resumes. Elapsed age and pledge deadlines continue to refer to their recorded dates; events and rewards must never be delivered to the wrong player character.

## Public commitments

The prototype supports public commitments for vengeance and recovery only. Declaration states the target, exact completion condition, audience, deadline, success reward, and failure cost before commitment. Use a five-year deadline from declaration as the initial default.

Require an aspiration to have existed for at least twelve months, remain incomplete, and have no irreversible qualifying milestone already achieved. For vengeance, the target cannot already be in the owner's custody. For recovery, neither the required control threshold nor the qualifying completed construction may already be satisfied. These rules reduce last-minute reward collection without claiming to eliminate every optimization.

A fulfilled eligible pledge adds public recognition, not another copy of the personal satisfaction reward. Missing the deadline applies the failure penalty once and removes the pledge state; the underlying aspiration may continue privately. Voluntary early withdrawal from the pledge uses that same penalty once. Simultaneous abandonment of the underlying aspiration does not additionally charge the ordinary abandonment penalty.

Target death outside the owner's responsibility excuses an impossible vengeance pledge; voluntary actions that make fulfillment impossible are not treated as an automatic excuse. The event explains the distinction. No generic pledge changes a whole faith's fervor.

## Initial reward parameters

These numbers are centralized balancing defaults. They are assessed against the player's choices and CK3's existing rewards during playtesting.

| Outcome | Initial extra reward or cost |
| --- | --- |
| Fulfilled desire | Remove 10 stress |
| Fulfilled ambition | Remove 20 stress |
| New friendship | Add 50 diplomacy lifestyle experience |
| Public accountability | Add 100 prestige |
| Holding recovery | Add 100 stewardship lifestyle experience; local +5% tax modifier for 3 years |
| Fulfilled public pledge | Add 100 prestige, once |
| Broken or withdrawn public pledge | Remove 100 prestige and add 15 stress, once |

No gold reward reimburses construction. No aspiration removes vanilla tyranny, scheme discovery, opinion consequences, or action-related stress. Territorial rewards are local, temporary, and non-stacking. Faith, treasury, travel, conquest, and religious fervor goals remain future families; they are not hidden additions to this prototype.
## Native ownership and interfaces

One visible story instance represents one aspiration. Current-player eligibility is revalidated before reservation; origin consumption, capacity and one-per-family-and-target guards precede creation. Debug forcing bypasses randomness only. Suspended instances remain owned by their original character; elapsed dates and owner-death cleanup continue.

Core dispatch recognizes only `vengeance`, `holding_recovery` and `personal_bond`. All three dispatch progress and terminal effects to their owning family modules. Unknown flags are rejected. Core never rewards unimplemented family progress.

Native scripted effects take parameters in braces and return no value. Task 2 probes confirmed direct story references through event options and actual save/load, numeric date values advancing by one per day, and native timer durations of 720 days for 24 months and 2920 days for eight years. Task 4 adds bounded registered lifecycle assertions and mandatory native UI/save/load/switch procedures for full review and pledge boundaries.

| Scope | Interface | Contract |
| --- | --- | --- |
| Story | `asp_initialize_story_effect = { FAMILY = <flag> CLASS = <flag> TARGET = <reference> }` | Save schema, family, class, owner, target, origin, next review and a monotonically allocated owner-local instance ID before showing the origin event. Family adds cause and interpretation. |
| Story | `asp_resolve_story_effect = { OUTCOME = <flag> REWARDS = <normal\|none> }` | Sole terminal payout entry. Revalidate and latch resolution before consequences, memory, cleanup and `end_story`. Effective rewards become `none` for suspended, dead or AI owners before family dispatch. Early forgiveness uses the ordinary private release cost. Outcomes: fulfilled, abandoned, forgiven, impossible, owner_dead. |
| Story | `asp_refresh_story_effect = yes` | Validate ownership/objective, process dates and check family progress. No suspended rewards. On return, settle expired pledge before closing objectives achieved during absence with no reward. |
| Story | `asp_can_manage_story_trigger = yes` | Live, unresolved story owned by current player; every event option rechecks it. |
| Story | `asp_family_check_progress_effect = yes` | Dispatch to that family's `asp_<family>_check_progress_effect`. |
| Story | `asp_family_resolve_effect = { OUTCOME = <flag> REWARDS = <flag> }` | Dispatch to that family's `asp_<family>_resolve_effect`; no other story access. |
| Story | `asp_declare_story_effect = yes` | Once per instance; save five-year deadline and public audience. |
| Story | `asp_settle_pledge_effect = { RESULT = <fulfilled\|withdrawn\|expired\|excused> }` | Latch settlement before effects, clear public state and prevent reentry. |
| Character | `asp_open_management_effect = yes` | Save up to eight story references into event-context `asp_choice_1` through `asp_choice_8`; selection carries `scope:asp_selected_story` through actions. Never store a mutable character-global selected story. |

Persisted story fields: `asp_schema`, `asp_instance_id`, `asp_family`, `asp_class`, `asp_target`, `asp_origin_date`, `asp_next_review_date`, `asp_interpretation`, `asp_resolved`, `asp_suspended`, `asp_declared`, `asp_pledge_deadline`, `asp_pledge_settled`. Family-specific fields stay in family contracts. Task 2 stores numeric `current_date` values in origin and next review, adding the measured native day count for the initial 24-month/8-year review. The independent probe preserved target, origin, review and timer; C04 preserved the core instance's exact target, instance ID, origin and next review through native save/load. Task 4 records exact review, pledge and suspension boundary procedures in the acceptance scenarios.

Shared namespaces are `asp_core`, `asp_management`, `asp_pledge`; dev namespace is `asp_test_core`. Task 2 reserves `asp_test_core.1` for the C01-C04 suite entry; `.2` for C04 verification after an actual reload; `.3` for the stale-action C03 observation; `.4` for the independent second-instance callback; `.20` for C02 and C03 setup; `.21` for early forgiveness/effective reward-policy regressions (C09/C10); `.22` for combined AI/landless eligibility (C11); `.10` for native scope/timer setup and `.11` for calendar/save-load probes. `asp_management.1` is the eight-entry selector, `.2` the selected-instance actions, and `asp_core.1` the scheduled-review notification. Never repurpose these IDs. Runtime files belong under `game/`; core debug entry points under `tests/game/`. There is no runtime plugin registry or framework.

## Explicit prototype defaults

- One declaration per instance; redeclaration never resets a settled pledge.
- Pledge expiry occurs at the recorded deadline, including an exact-boundary check.
- Full-cap major offers use the prospective two-remaining-ambitions multiplier `0.4`; replacement is explicit and charges the chosen story's ordinary abandonment cost unless its pledge policy takes precedence.
- Pledge audience is the owner's court and realm; add no extra opinion effects.
- Shared value IDs include `asp_desire_review_months = 24`, `asp_ambition_review_years = 8`, `asp_desire_repeat_months = 12`, `asp_ambition_repeat_years = 3`, `asp_declare_min_months = 12`, `asp_pledge_years = 5`. These are parameters, not assumptions about engine time-unit conversion.

## Presentation and compatibility

The Task 2 native debug story shows a target and is dev-only; family stories will add cause, exact condition, age, next review and private/declared state in their owning stages. The management decision uses at most eight conditionally visible options, each bound to the shown instance and labeled by class and target. Management provides Abandon, Declare intention when eligible, Reconsider, Withdraw commitment while declared, and Back. Replacement uses a separate exact-instance selector and confirmation. No GUI replacement, raw identifiers or dev controls in normal play. Demonstrate a native UI limitation before changing the approach.

Use additive child on-actions, story cycles, decisions, events, memories and English BOM localization. Required engine surfaces and outstanding knowledge, attribution, timing and event-context probes are recorded in [modding notes](../../docs/modding-notes.md). Source and accepted Task 2 gameplay version: CK3 1.20.0.4 (Crozier). Initial coverage: current player, single player, adult landed ruler. DLC branches are unimplemented and unsupported unless documented after verification. Persisted-state migration is not needed before the first implemented schema; document it before changing saved fields.

## Task 2 reproducible checks

The bounded `core-regression` runner scenario invokes shared dev-only native effects for C01, C02, C09, C10 and combined C11 eligibility. The manual event entries reuse those assertions. C03 and C04 retain mandatory real UI and actual save/load steps, with scripted setup and post-action assertions in `tests/scenarios.md`. All new automatable behavior checks and fixes must add a registered runner scenario or an assertion in one, with measured native evidence. Required UI checks must have scripted setup and post-action assertions plus exact mandatory manual steps; they cannot be reported as automated passes.

## Task 4 stable allocations

Reserve `asp_test_core.30` for the shared P01-P06 lifecycle regression; `.31` for near-boundary calendar/UI setup; `.32` for its next-day assertions; `.33` for post-save/load assertions; `.34` for switch-away/return setup; `.35` for return assertions; `.36` for absence completion setup; `.37` for absence return assertions; `.38` for owner-death setup; `.39` for death cleanup assertions; `.40` for full-cap replacement UI preparation; `.41` for replacement UI assertions. Runtime `asp_management.3` owns review choices, `.4` replacement confirmation; `asp_pledge.1` declaration confirmation, `.2` settlement narrative; `asp_core.2` full-cap replacement offer. Family dev `asp_test_vengeance.2` is the shared pledge/lifecycle entry. No existing stable ID is repurposed.

Dev `.42` asserts the actual switched-away owner and snapshots return-boundary costs; `.43` completes the exact old owner’s objective while the new player remains active. Both belong to mandatory P04/P05 switch procedures, never a scripted replacement for `play` input.

Dev `.44` opens the exact calendar ambition’s review UI, `.45` observes actual retention, `.46` observes actual reinterpretation. `.50` prepares a native vengeance origin for lifecycle UI replay, `.51` opens its exact management context, `.52` observes actual declaration, and `.53` completes/observes that declared UI replay through a scripted public target death. These do not claim real Execute input.

## Task 4 lifecycle ordering and state

Native initial durations remain 720/2920 days. The actual Task 4 saved boundary fixture serializes `months=12` as 360 days, `years=3` as 1095 days, and `years=5` as 1825 days. The numeric declaration minimum, repeated review and pledge defaults use those observed values.

Free private release compares original age with the initial class threshold, independently of `asp_next_review_date`. Retain and a supported private reinterpretation schedule the repeated interval only when due; neither resets origin or creates/rewards an instance. `asp_review_notified` latches one notification per due reminder. The implemented vengeance story maintains its lifecycle daily; quarterly core maintenance remains a backstop. Returning a still-unfinished aspiration clears suspension and offers any due review.

Every current-player refresh settles an active pledge at `current_date >= asp_pledge_deadline` before checking family terminal progress. Resolution applies the same expiry-first ordering. Fulfillment after expiry receives no pledge recognition; the remaining private result follows its own policy. `asp_family_has_terminal_progress_trigger` routes only implemented family predicates, so terminal processing is the final effect on a story it can destroy. Suspended return keeps its latch through progress, closing completed goals with memory and `REWARDS=none`; it never pays retrospective private or public success rewards. Expired return settles the original owner once before that progress path. AI maintenance suspends and queues no action/reward event; owner-death hooks retire the story without penalties or inheritance.

Declaration uses story-scope `asp_family_can_declare_trigger`; implemented vengeance and recovery can be eligible, and personal bond always fails. One declaration records immutable `asp_pledge_deadline` and `asp_pledge_audience=court_and_realm`; `asp_pledge_settled` permanently prevents redeclaration. Settlement records `asp_pledge_result` before effects and clears declaration. Public success requires verified family attribution, rather than private known-secret evidence. An unexpired personal secret success withdraws the pledge at -100 Prestige/base +15 Stress while retaining ordinary private closure. External impossibility excuses an unexpired pledge. Owner-caused impossibility withdraws it; reaching the deadline takes precedence over later excuse or success. Simultaneous abandonment/forgiveness of an active pledge sets terminal-only `asp_terminal_public_release`, suppressing the extra ordinary private cost. Native Stress Gain modifiers still apply.

Full-cap vengeance selection consumes the qualifying incident before probability or offer; it uses the existing two-or-more occupancy multiplier 0.4. The offer captures owner, victim and known culprit into event-held `asp_replacement_cause_*` references and three exact old ambition references, never mutable character selection. Confirmation rechecks the current owner, living reachable culprit outside custody, retained knowledge/consumption, duplicate prohibition and selected old ambition. The original qualifying bond comes from the death hook: CK3 removes friendship after death, so it is not retrospectively re-queried. If the new cause or old story is stale, no old state/cost changes. Cancel creates/rewards nothing; confirm releases only the chosen old ambition under private or pledge cost precedence, then creates exactly one new instance. The consumed cause cannot propose again.

New optional schema-1 fields are the review notification latch, pledge audience/result, and terminal public-release guard. Existing saved IDs, references, origin and deadlines are not renamed. Core .2/.3 dev IDs retain their Task 2 save/load/stale-action meaning. Future family implementation must extend terminal-progress and declaration dispatch explicitly; inert recognized families cannot earn a core reward merely through maintenance.

Dev `.54` snapshots the actual dead owner and successor before a stale management click; `.55` requires both Prestige/Stress snapshots and both empty story sets to remain exact afterwards.

Event-facing declaration eligibility is evaluated from the live event character through `asp_event_can_declare_trigger`. It checks the selected Story link before entering any family predicate. A missing or ended link returns false, including during later-frame native tooltip construction; direct same-frame negative predicate assertions alone do not establish this render safety.


## Recovery integration

County-target recovery uses the existing core lifecycle, replacement and pledge ownership. Generic replacement validates the saved recovery county and consumed incident serial before releasing one exact selected Story; vengeance proposals clear stale county proposal state. Declaration and terminal progress dispatch explicitly to the recovery family. Event-character guards validate the saved live Story before entering county family predicates. County management and public-settlement wording use title getters; core captures the county transport flag before terminal destruction. Recovery never owns a second Stress, pledge or terminal payout latch.

## Personal-bond integration and routine cadence

Core dispatch now recognizes implemented personal-bond terminal progress and family resolution. Bonds remain desire-class only and never support declaration/public fulfillment. The shared quarterly child runs `asp_try_personal_bond_effect` after maintenance; current-player/adult/landed/cap/cooldown guards precede selection. Central values are routine base20, occupancy1/0.6/0.3/0.1/0.1/0 and routine cooldown12 native months (360 measured days). Family context/eligibility/consumption are owned by personal_bond, not core. Debug force cannot bypass them. Shared terminal, review, suspension and Stress behavior remains the sole core policy.

Registered bond-regression covers B01–B07 through the shared family fixtures with complete independently checked numeric telemetry, replay and diagnostic failure. The family scenarios separately require actual native Befriend input/outcome; scripted relationship setup and modified dates cannot certify that UI action or elapsed calendar time.

## Task 7 integrated allocations

Reserve dev `asp_test_core.60` for registered I01/I02 state regression; `.61` mixed-family actual persistence setup; `.62` post-reload exact identity; `.63` actual switched-away observation; `.64` unfinished return; `.65` absent completion; `.66` no-reward return; `.67` target-death/loss observation; `.68` death/succession setup; `.69` successor cleanup; `.70` mixed selector; `.71` exact selected UI assertion; `.72` romantic card setup. Existing `.3` remains C03. Native gameplay economics and saved identifiers are unchanged.

Public fulfillment while suspended retains the existing zero-reward settlement policy. Event-held result code5 selects explicit withheld-reward wording for character and county targets; ordinary code1 still pays100 Prestige. Codes are presentation transport, not renamed saved flags. Registered integrated-regression checks both target classes and normal fulfillment independently.

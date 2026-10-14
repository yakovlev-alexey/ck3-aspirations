# Holding recovery specification

Status: implemented on CK3 1.20.0.4; registered H01–H05, real GUI payment/completion/reward and later-frame stale-window acceptance observed. Independent Task 5 source review accepted the exact token-ownership fix; combined actual persistence is owned by core scenarios.

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

Namespace: `asp_holding_recovery`; dev namespace: `asp_test_holding_recovery`. Source files use `game/common/.../asp_recovery.txt`, including the non-stacking county modifier, `game/events/asp_recovery_events.txt` and `game/localization/english/asp_recovery_l_english.yml`. Shared fields and operations are owned by core.

## Parameters, transitions and consequences

Origin requires personally held county control below 70 after an observed enemy siege/raid and an available appropriate construction/upgrade. Apply core's 50% major-event chance and ambition occupancy multipliers. Content remains eligible. Repeat damage while active adds context without another reward track; consumed incidents and family/target guards prevent farming.

Fulfillment requires control at least 80 and one eligible owner-funded construction begun after origin and completed while the county remains personally held. Existing, in-progress-at-origin, cancelled, foreign-funded and ownership-interrupted work never qualifies. A fresh construction token is needed after cancellation or ownership interruption; restoring ownership cannot revive invalid evidence.

Protection of inhabitants, family prestige and income are narrative interpretations of the same conjunctive objective. Loss of county prompts reconsideration: involuntary loss closes free with memory and excuses an uncontrollable pledge; voluntary grant uses abandonment/pledge policy. No target substitution or reconquest family. Later recovery requires a new qualifying incident. Owner death and switching follow core; absent-period completion grants no retrospective rewards.

Fulfillment removes 20 stress, adds 100 stewardship lifestyle experience and a local +5% tax modifier for 3 years once. Modifier never stacks; no construction reimbursement. Early private abandonment costs core's 10 stress; review release and uncontrollable impossibility are free unless an active pledge's rules apply.

Declaration uses core's age/deadline policy and requires both control below 80 and no qualifying completed construction. A nearly completed objective cannot declare for an immediate bonus. Public success adds 100 prestige once; failure/withdrawal applies -100 prestige and +15 stress once, taking precedence over simultaneous private abandonment costs.

## Presentation and compatibility

Use the [writing guide](../../../docs/player-facing-writing.md). Origin prose must fit both raid and siege without inventing a particular destroyed building. Protection, family standing and income receive distinct roleplay option flavor. Exact Control, construction, funding, ownership, cancellation and supported building rules remain in effect descriptions and labeled cards, with conditional future rewards. Future Stress relief is a base value subject to Stress Loss modifiers. Declaration disclosure is county-specific; it must never describe a living culprit or custody.

The existing captured numeric terminal outcome drives display-only `immediate` summaries for fulfillment1, involuntary/unclassified loss2 and release3. Summaries report the existing memory/reward policy without executing it or traversing an ended Story. Fulfillment summaries state base Stress relief and modifier applicability; normal event emission still excludes absent no-reward completion. Native editorial comparison supplements H01–H05 and core I05, preserving exact one-time resource/modifier measurements and later-frame stale coverage.

Explain incident, recorded control, exact two-part condition and eligible building categories without naming an unavailable building. Show ownership loss and voluntary grant consequences. Use English localization and game-provided art references; no original or extracted art in Task 1.

Required surfaces: siege/raid, construction start/completion, title ownership callbacks, county control and modifiers, stories/memories. Native payment/start/cancellation/completion and actual GUI grant probes establish the implemented callback route; never infer payment from holder substitution. CK3 1.20.0.4 runtime acceptance is recorded in the scenarios. No DLC-dependent branch promised; schema 1 and core migration policy apply.

## Task 5 stable allocations

Runtime `asp_holding_recovery.1` is the origin, `.2` terminal narrative. Dev `.1` is H01-H05, `.10` attribution setup, `.11` attribution observations. Dev hooks measure only native callbacks and remain excluded from release.

Dev `.12` prepares a funded AI engine build attempt; `.14` observes a typed conquest batch. Neither is represented as an actual GUI grant or war.

## Task 5 approved availability boundary

The prototype's explicit candidate pool is Tribal Markets and Palisades levels 1–2, and Pastures, Cereal Fields and Hill Farms level 1. Eligibility must establish the next building's native holding, terrain, slot, category absence or upgrade prerequisite, government and innovation restrictions. An empty slot alone is insufficient. Origin and story text list exactly these supported categories. Other constructions cannot satisfy this prototype objective.

“Available” means legally and technologically possible to construct next. Treasury affordability is not an origin gate: an ambition may emerge before the ruler has saved the money. Native costs and discounts remain authoritative; the mod promises no fixed construction price and grants no reimbursement. Actual payment is established through the original native payer callback, never the current holder. Registered native and actual GUI acceptance are recorded in the scenarios.

Dev `.13` checks an actual AI start callback, exact original payer and resource decrease after `.12` prepares a legal vacancy in an existing AI holding. The dedicated AI capability launch omits the deterministic runner’s `-disable_ai`; its policy remains unchanged.

## Implemented callback contract

Runtime namespace `asp_holding_recovery`, origin `.1`, terminal `.2`; source files use `asp_recovery.txt`. Incident observation is a character effect with fixed county and explicit cause, deduplicated per county/owner/day. The incident serial is consumed before selection and capacity decisions. A duplicate active target receives no new Story or payout. At capacity the generic core replacement event preserves three exact old Story references and requires revalidation of the consumed recovery county/serial before abandonment. No implicit replacement occurs.

Legal candidate scope is a personally held holding in the personally held county. Native tribal government/holding prerequisites, tier-I-to-II technology (innovation_barracks or native permafrost alternative), category absence and available slots apply to Markets/Palisades. Native castle/city/temple holding level, government exclusion, terrain and category absence/slots apply to the three level-I economy categories. Ongoing work cannot supply the origin candidate.

Province callbacks retain original payer and a monotonically allocated start serial. Each new start invalidates the old pending token; an accepted start snapshots exact Province, payer, serial, date, supported category levels and which categories were legally possible. Completion needs the same serial and payer, the original owner still holding the county, and an increase in a supported eligible category. Province lists mark work already ongoing at origin; its delayed native start callback is excluded until cancellation/completion clears the block. Missing/foreign payer cannot substitute the current holder. Cancellation invalidates the pending token; a fresh verified restart may qualify. Completed evidence is a milestone, but control80 must also be met.

Title loss irreversibly marks the original Story and invalidates its pending tokens. Only exact native transfer_type=granted is voluntary; conquest, other classified causes, and absent/unknown causes take conservative free impossible closure. Actual GUI Grant has confirmed the granted flag. Registered typed cause fixtures do not claim to be a played war. Reacquisition cannot revive the original Story or construction token.

Core remains sole terminal latch, Stress and pledge settlement owner. Recovery supplies a memory and, only with normal fulfilled reward policy, 100 Stewardship experience and one non-stacking county tax modifier for three years. Native Stress controls must independently match modified release/pledge costs. Absence/death follows core's no-retrospective-reward policy. Three interpretations share the objective, preserve cause/age when reconsidered, and are guarded from live event-character context before weak Story traversal. Stale origin has native harmless Close fallback.

Dev `.20` prepares a disposable active recovery for real GUI construction, `.21` only sets the control milestone, `.22` reuses registered H02 measurement logic to observe actual payment/reward. These are explicit UI acceptance exceptions, not a second scripted construction system.

## Verified native reservation boundary

Generated native trigger documentation says `free_building_slots` includes buildings in construction. Actual GUI callback at09:19:49 confirmed slots0/ongoing1/original-payer-owner1/strict-origin-legality0 before any start snapshot. Thus slot availability is an origin prerequisite only. An authoritative native start callback supplies the already selected/reserved work; its tracking predicate retains holding, government, terrain, category and innovation requirements and snapshots the original payer/serial/category levels, without demanding another free slot. Completion must still prove the same pending work and supported category increase.

Registered H03 invokes the native child on_action at slot0 with a verified original payer and checks both token and completion. Its scripted occupancy model reports ongoing0 and makes no actual payment claim; actual GUI ongoing1/payment is a separate mandatory acceptance. This covers the specific reserved-slot defect rather than merely rerunning the old direct helper path.

Repeat incidents preserve the active Story's original control/date/serial; the county stores the latest observed damage context. They cannot start a duplicate Story or reset its age. Origin displays the recorded Control, and county management explains both milestones and valid payment.

The visible Story card supplies the native implicit English title and description, and its private/declared body reads the exact fixed county, recorded raid or siege, frozen origin Control, chosen interpretation, age and next review from the Story. It states both Control 80 and new owner-funded supported construction. The declared state adds the public deadline, 100 Prestige success reward, and once-only withdrawal/expiry penalty. This is presentation of existing Story state; it does not change eligibility, payment or settlement.


## Exact Province token ownership regression

A Story's historical started-Province list grants no ownership of a newer Story's token. Title-loss and terminal cleanup may remove pending Story/payer references only when the Province currently points to that exact old Story. Registered H04 models a suspended older AI owner's historical list and a current player's fresh start in the same Province; it tests matching ordinary cleanup, title-loss isolation, no-reward terminal isolation and the newer Story's subsequent one-time reward. This is scripted native state/callback coverage, not an actual player switch or payment claim.

Registered H03 also dispatches the dev native start observer with original AI payer, initialized AI snapshot and absent GUI state; fresh setup must clear cached payer/Province. The AI observer and GUI observer are independent. This assertion does not replace earlier genuine AI payment evidence.

Task 7 combined replacement tooltips exclude invisible context Stories with a native schema-presence branch before reading aspiration fields. Registered integrated-regression exercises mixed caps and rejects native tooltip diagnostics.

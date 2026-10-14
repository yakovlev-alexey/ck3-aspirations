# Aspirations interface design

Status: proposed interface specification for written review, 2026-10-14. The separate-window direction was accepted in conversation. Implementation and native acceptance are pending.

[Product design](../../design.md), [core lifecycle](../../../src/core/SPEC.md), the [family contracts](../../design.md#purpose-and-scope), and [story acceptance](../../story-authoring.md) remain authoritative for existing gameplay. This proposal extends the prototype's presentation boundary to an additive Aspirations window. When implementing it, reconcile the owning presentation contracts and scenarios in the same change; this proposal must not become a competing gameplay contract.

## Purpose and scope

Make each aspiration understandable without reading a long paragraph: identify its exact target, see the remaining completion conditions, inspect why a condition or action is unavailable, and manage the chosen instance. Keep the ruler's personal motive visible without giving it the same visual weight as requirements.

The main view is a separate Aspirations window in CK3's native visual style. Existing Story cards become concise discovery and status surfaces. Story instances continue to own gameplay state; opening the window or inspecting a tooltip cannot advance, resolve, declare or reward an aspiration.

The supported families are holding recovery, vengeance and personal bond. This work adds no new family, gameplay action, reward, relationship, scheme access, construction category or completion rule. Selection means which aspiration is being inspected, not a main aspiration with different gameplay priority. There is no overall ambition score, percentage or incentive to fill slots.

The player's requested date presentation applies throughout the browsing interface:

- Show the month and year the idea arose, for example `Since October 1178`.
- Do not show elapsed age in days, months or years, or the day of origin.
- Do not show a scheduled review date, countdown, progress bar, age threshold or review cadence in list rows, details, Story cards or their browsing tooltips.
- Keep the public commitment deadline visible because it governs a player promise and its consequences. It is separate from origin and internal review timing.

Internal origin, review scheduling, declaration eligibility and free-release rules are unchanged. Existing review notifications and choices remain governed by core. Relevant actions disclose current eligibility and the actual cost before confirmation; hiding the review schedule cannot hide a cost.

## Screen structure and visual conventions

Use one window with a short list on the left and the selected aspiration on the right. The header, list and detail header remain visible while long detail content scrolls. Keep the action footer outside the scrolling body. The maximum current capacity is eight aspirations, so no search, filter controls or pagination are needed.

The ASCII diagrams specify grouping, information hierarchy and interactions, not textures, pixel sizes or final localized wording. Names, dates and measured values in diagrams are illustrative. All shipped prose and localization remain English.

Legend:

- `[portrait]`, `[shield]` and `[icon]` are native visual elements.
- `[Button]` is an available action; `(Button)` is disabled and has an explanation on hover.
- `[x]` and `[ ]` represent fulfilled and unfulfilled requirement icons. They are read-only, never checkboxes the player can toggle.
- `(i)` marks a hoverable explanation; it is not a replacement for the visible condition.
- `>` marks the selected list row. Selection also has a native highlight.
- Bars appear only for actual numeric quantities. Color always has a text/icon equivalent.

### Main window with recovery selected

```text
+----------------------------------------------------------------------------------------+
| Aspirations                                                                       [X]  |
+----------------------------+-----------------------------------------------------------+
| AMBITIONS                  | [icon] Restore a wounded holding                          |
|                            | [shield] Jamana of Sibi                                   |
| > Restore Jamana of Sibi    | Ambition | Private | Since October 1178                  |
|   [shield] Private          +----------------------------------------------------------+
|   Control below 80          | I cannot bear to leave this county wounded.              |
|   Since October 1178       | I mean to protect its inhabitants.                        |
|                            |                                                           |
|   Vengeance for Alda       | FULFILLMENT REQUIREMENTS                                  |
|   [portrait] Private       | [x] Personally hold Jamana of Sibi                    (i) |
|   Culprit still free       | [ ] Restore Control to at least 80                    (i) |
|   Since June 1177          |     Current: 69 / Required: 80                            |
|                            |     [=================---]                                |
| DESIRES                    | [x] Complete qualifying construction                  (i) |
|                            |     Qualifying work has been completed.                   |
|   A wish for closeness     |                                                           |
|   [portrait] Friendship    | ON FULFILLMENT                                            |
|   Relationship not formed  | Stress relief | Stewardship experience | County tax  (i)  |
|   Since March 1178         |                                                           |
|                            | ORIGIN                                               (i)  |
|                            | An enemy raid. Control when the idea arose: 69.           |
|                            +---------------------------------------------------------- +
|                            | (Declare intention) [Reconsider] [Release]                |
+----------------------------+-----------------------------------------------------------+
```

List rows contain a short family/target title, class-appropriate status, one concise unmet-goal summary and the origin month/year. The selected row must remain recognizable even when names wrap. Use `Ambitions` and `Desires` group headers only when that group has entries; these are existing classes, not new capacity rules. Do not display unused slots.

The detail header contains the title, target, class, private/public state and origin month/year. The body contains a brief motive, requirements, conditional rewards and concise origin context in that order. The footer contains management actions for this exact instance.

The illustrated recovery cannot declare because a qualifying construction milestone is already complete. Its disabled action explains that rule. Condition progress and declaration eligibility must never be conflated.

## Requirements and tooltips

Display each independently meaningful part of fulfillment as a separate row. Every row has a state icon, concise text and an explanation available by hovering the row or its information icon. Use the same family predicates and evidence as gameplay, with explicit family scope branches before evaluating Character or Title targets.

Native requirement explanations should use engine trigger descriptions where they are truthful and readable. Use authored explanations for recorded milestones, supported construction or attribution that cannot be understood from a raw engine description. Do not expose variable names, construction token serials, internal lists or hidden murder knowledge. The custom window does not inherit the decision-detail requirement model automatically; exact native tooltip generation is a feasibility gate below.

### Construction explanation

```text
+-------------------------------------------------------------+
| Complete qualifying construction                            |
| [x] Qualifying work has been completed.                     |
|                                                             |
| The work must be started after this idea arose, funded      |
| by you, and completed while you personally hold the county. |
|                                                             |
| Supported work where legal:                                 |
| - Tribal Markets or Palisades I-II                          |
| - New Pastures, Cereal Fields or Hill Farms I               |
|                                                             |
| Existing or already-started work does not count.            |
| Cancelled or foreign-funded work does not count.            |
| Cancellation requires a fresh start. Costs are paid         |
| normally; fulfillment does not reimburse construction.      |
+-------------------------------------------------------------+
```

Recovery has three rows: personal ownership, current Control at least 80, and recorded qualifying completion. Show the actual Control value; size its bar against the required threshold and keep the actual value visible when it exceeds 80. A completed construction milestone is persistent evidence; ownership and Control are current conditions. Never mark construction fulfilled merely because a building exists or a generic progress bar finished. Show a verified pending-work description only if the recorded state supports it; otherwise use `No qualifying completion yet` rather than guessing which native building is being constructed.

A lowered Control value must return its row to unmet even after it was previously sufficient. The construction row remains fulfilled only under the family's valid recorded evidence. When all conditions resolve the Story through existing lifecycle logic, remove it from the active list; do not add a manual claim button or a persistent completed entry.

### Personal bond details

```text
+-----------------------------------------------------------+
| [icon] A wish for closeness                               |
| [portrait] Beatrice                                       |
| Desire | Private | Since March 1178                       |
+-----------------------------------------------------------+
| I would like to know her beyond the business of my court. |
|                                                           |
| FULFILLMENT REQUIREMENT                                   |
| [ ] Form a new friendship with Beatrice               (i) |
|     Friend or Best Friend                                 |
|                                                           |
| PURSUIT                                                   |
| Use existing interactions, schemes and events.        (i) |
|                                                           |
| ON FULFILLMENT                                            |
| Stress relief | Diplomacy experience                  (i) |
+-----------------------------------------------------------+
| [Reconsider] [Release]                                    |
+-----------------------------------------------------------+
```

Friendship and romance use the same structure with their correct relation alternatives and reward policy. Friendship requires a new Friend or Best Friend; romance requires a new Lover or Soulmate and grants no friendship experience. Do not add percentage progress or treat opinion as relationship completion.

No public declaration or withdrawal action appears for bonds. The pursuit explanation says that the aspiration grants neither a relationship nor access to locked schemes. It does not claim a currently available route unless native eligibility has been checked. Temporary distance or occupied scheme capacity is not a failed fulfillment condition and does not automatically close the desire. The first implementation does not add shortcuts that start Befriend or Seduce; normal character interactions remain the pursuit surface.

### Vengeance details

```text
+------------------------------------------------------------+
| [icon] Vengeance for a loved one                           |
| [portrait] Alda, remembered | [portrait] Fulco, culprit    |
| Ambition | Private | Since June 1177                       |
+------------------------------------------------------------+
| I remember Alda and the part Fulco played in that loss.    |
|                                                            |
| FULFILLMENT REQUIREMENT                                    |
| [ ] Bring Fulco into my custody                       (i)  |
|     Custody must be acquired after this idea arose.        |
|                                                            |
| ON FULFILLMENT                                             |
| Stress relief | Public accountability recognition     (i)  |
|                                                            |
| Choosing this ambition grants no imprisonment reason.      |
+------------------------------------------------------------+
| [Declare intention] [Reconsider] [Release]                 |
+------------------------------------------------------------+
```

This example uses the accountability interpretation. Personal vengeance instead shows the requirement for recorded owner responsibility for the culprit's death, with a truthful attribution explanation. A target being dead is not sufficient evidence; unrelated death takes the family's impossible-closure path. Public and secret attribution remain distinct, and no tooltip discloses an otherwise unknown culprit.

The remembered victim and current target have separate roles. Do not replace the target with an heir or silently swap interpretation. Applicable vanilla tyranny, secrecy and personality Stress remain in force.

## Public commitment and management actions

### Public recovery commitment

```text
+-----------------------------------------------------------+
| [icon] Restore a wounded holding                          |
| [shield] Jamana of Sibi                                   |
| Ambition | Public pledge | Since October 1178             |
+-----------------------------------------------------------+
| I have given my word to restore this county.              |
|                                                           |
| FULFILLMENT REQUIREMENTS                                  |
| [x] Personally hold the county                        (i) |
| [ ] Restore Control to at least 80       Current: 69  (i) |
| [ ] Complete qualifying construction                 (i)  |
|                                                           |
| PUBLIC COMMITMENT                                         |
| Fulfill before 1 November 1184.                       (i) |
| Audience: my court and realm.                             |
| Public success: additional 100 Prestige.                  |
| Withdrawal or expiry: 100 Prestige lost and Stress.   (i) |
|                                                           |
| ON FULFILLMENT                                            |
| Ordinary recovery rewards                            (i)  |
+-----------------------------------------------------------+
| [Withdraw commitment] (Reconsider) [Release]              |
+-----------------------------------------------------------+
```

Use an exact native calendar deadline, including the day, for the promise. `Fulfill before` reflects the existing expiry-first equality rule: reaching the deadline is already expiry. Keep this date adjacent to the consequences. Its tooltip explains exact-boundary precedence and native modified Stress costs. An origin's month/year and a promise's deadline must have distinct labels.

The public vengeance view additionally explains that secret personal vengeance ends the private aspiration but settles an unverifiable active pledge under withdrawal policy. No public bonus is promised for absent-period fulfillment where core withholds recognition.

Action availability follows the existing lifecycle. Private supported ambitions show Declare intention, Reconsider and Release. Once an instance cannot declare again, omit Declare intention rather than advertising a future opportunity. A temporary or milestone-based restriction disables an otherwise relevant action with its reason. Public instances show Withdraw commitment, disabled Reconsider while forbidden by core, and Release. Family-specific forgiveness remains available only where the owning family permits it.

### Disabled declaration tooltip

```text
+-----------------------------------------------------------+
| Declare intention                                         |
|                                                           |
| [x] This idea is old enough for declaration.              |
| [x] No public commitment has previously been made.        |
| [ ] No qualifying construction has been completed.        |
|                                                           |
| An existing construction milestone prevents declaration.  |
+-----------------------------------------------------------+
```

This diagram illustrates separate eligibility reasons, not a raw dump of every hidden guard. Show the actual failed reasons for the selected Story, with no invented review date or countdown. Explain a minimum-age block as `This idea is too recent for a public commitment` without displaying an age timer. Costs and conditions that matter to confirming a promise remain fully disclosed in the declaration confirmation.

### Release confirmation

```text
+-----------------------------------------------------------+
| Let this intention go                                     |
| [shield] Jamana of Sibi                                   |
|                                                           |
| I should decide whether I still mean to pursue its repair.|
|                                                           |
| WILL HAPPEN                                               |
| This exact recovery ambition will end.                    |
| Stress: the native modified release cost.                 |
| No fulfillment reward will be granted.                    |
|                                                           |
| [Release] [Keep pursuing it]                              |
+-----------------------------------------------------------+
```

Continue using the existing native event confirmations for declaration, withdrawal, release, forgiveness and reinterpretation where available. The mockup's `WILL HAPPEN` stands for the engine-generated effect section, not a heading authored in localization. Roleplay text expresses the choice; native effect previews disclose the actual resource changes before commitment.

Free release says there is no additional aspiration release cost, without explaining a scheduled review timer. For a declared Story, show pledge withdrawal cost and do not add the ordinary private release cost. Existing native confirmation logic remains the payout authority. Opening or closing a confirmation never changes the inspected Story by itself.

## Entry points and concise Story cards

Provide an additive window entry through the existing Review my aspirations management decision. Its effect opens the overview instead of immediately entering the event selector. Keep that selector as a guarded fallback during the initial feasibility stage; remove duplicate navigation from the release experience once the window is accepted.

A related decision on a Story card may provide the same overview entry if native presentation supports it. The inspected stock Story decision widget opens a Decision detail, passing a Decision rather than the enclosing Story. Therefore it must not be presented as an exact-target `Inspect this aspiration` shortcut without a verified binding. No new base-game window override is needed for the required overview entry.

### Concise native Story card

```text
+-----------------------------------------------------------+
| [icon] Restore a wounded holding                          |
| [shield] Jamana of Sibi                                   |
| Ambition | Private | Since October 1178                   |
|                                                           |
| I mean to protect the people of this county.              |
|                                                           |
| [ ] Control at least 80           Current: 69             |
| [x] Qualifying construction completed                     |
|                                                           |
| [Review my aspirations]                                   |
+-----------------------------------------------------------+
```

Keep exact essential conditions on the card in a concise form and make detailed rules reachable through the overview. Ownership, funding and fresh-start restrictions remain explicit in the full view; a short construction summary cannot redefine those rules. A public card also shows the pledge deadline. No Story card shows elapsed age or review scheduling. Preserve all implicit Story title/description keys and the existing Story localization scope conventions.

## Selection and changing state

### Empty view

```text
+-----------------------------------------------------------+
| Aspirations                                          [X]  |
+-----------------------------------------------------------+
| No active aspirations                                     |
|                                                           |
| My personal wishes may take shape as my life changes.     |
+-----------------------------------------------------------+
```

Opening the overview with no active aspirations shows the empty view. It does not create an aspiration, suggest filling slots or offer a generate button. Invisible bond context Stories never become list entries.

On first opening, select the first visible aspiration in stable instance-ID order within the class groups. Keep selection during refreshes while that exact instance remains valid. Reopening in the same player session may retain a still-valid selection; it must never select an instance belonging to a previous player character. UI selection is transient and must not become a mutable character-global selected-story gameplay variable.

### Selected Story ends while the window is open

```text
+----------------------------+----------------------------------------------------------+
| AMBITIONS                  | This aspiration is no longer active.                     |
| Vengeance for Alda         |                                                          |
|                            | Choose another aspiration from the list.                 |
| DESIRES                    |                                                          |
| A wish for closeness       |                                                          |
|                            +----------------------------------------------------------+
|                            | No management actions                                    |
+----------------------------+----------------------------------------------------------+
```

Remove the ended entry and clear its target, tooltip context and action availability. Preserve the no-longer-active message until the player chooses another remaining row; do not silently redirect a click to the next aspiration. If none remain, show the empty view. Existing outcome events explain how it ended; no history screen is added.

Every action and confirmation revalidates current player, live Story, unresolved state, exact instance identity and family policy. A later-frame hover over a stale selection must not traverse an ended weak Story. Player change closes the window and clears all selection and cached contexts; reopen against the new player's eligible Stories. When returning to an old character, core processes suspension, expiry and no-reward completion before the UI lists valid active entries.

## Implementation boundaries and feasibility gates

Use native GUI files and an additive `gui/scripted_widgets` registration, with core-owned window/navigation and family-owned condition text and presentation predicates. The installed CK3 1.20.1 definitions expose additive widgets and stock Story visualization modules. They do not establish runtime acceptance of this custom window, its Story enumeration or tooltips.

The intended file ownership is:

| Area | Owner and intended native category |
| --- | --- |
| Window, selection, shared status and entry | `src/core/game/gui/`, `gui/scripted_widgets/`, and core decisions/events as required |
| Safe UI checks and action routing | Core `common/scripted_guis/`, using guarded existing lifecycle interfaces |
| Family condition state and explanations | Owning family predicates and English localization; add native categories only when used |
| Concise cards and origin labels | Owning family Story visualization and localization |
| Reusable capability evidence | Relevant `docs/knowledge/` topic after native validation |
| Automated state assertions and actual UI procedures | Core and affected family `tests/scenarios.md` with registered runner coverage |

Do not copy an installation GUI file wholesale, replace the Situations or character window, add a runtime framework or dependency, or duplicate gameplay state in a new aspiration model. Preserve saved IDs, original instance ownership and all payout latches. Any added display field needs documented compatible persistence behavior before implementation.

Before building the full view, validate a disposable recovery-only probe with these gates:

1. Open and close the additive window from the existing management entry, using native styles without a base-window replacement.
2. Enumerate visible current-player aspiration Stories, select two exact instances, and retain their identities through pause, state refresh and actual save/reload. Filter schema and family before reading private fields.
3. Display ownership, current Control and recorded qualifying construction as independent read-only conditions; obtain truthful native requirement/eligibility explanations with safe Story context.
4. Render the original month/year from the persisted origin. The current origin is a numeric `current_date` snapshot, not a proven GUI date object. Verify an exact native conversion or a compatible display snapshot/migration before choosing getters. Never divide the numeric origin by a fixed month length, use the window-open date, or reset origin on reinterpretation. Existing saves must recover the same original month/year; inability to do so blocks date acceptance rather than silently showing an invented date.
5. Retire the selected Story with the window and a tooltip open, then hover and attempt its prior action in a later frame. Require no effect on any remaining Story and no new weak-link, DataFactory or scope diagnostic.

These gates answer feasibility within the selected design. A gate failure must be reported before substituting a different entry point, a static text approximation for interactive requirements or a base-game GUI replacement.

## Acceptance and contract reconciliation

Before runtime implementation, update the presentation sections of `docs/design.md`, core and affected family SPECs, the writing guide, the shared visible-state checklist and the owning scenario documents. Replace their old age/review display requirements with origin month/year and hidden review scheduling. Preserve lifecycle timing and historical measured evidence.

No new durable finding. Native capability validation belongs to the feasibility gates and their reproducible evidence.

Register reusable state assertions and actual-input procedures with the existing runner. Native screenshots and fresh diagnostics are required; static localization or layout checks cannot certify interaction or readability. Required coverage is:

| Case | Required observation |
| --- | --- |
| Recovery progress | Control below and above 80, valid completion and rejected existing/foreign-funded work match family state; ownership remains exact |
| Relationship modes | Friendship and romance show the correct alternatives and rewards, no percentages and no public actions |
| Vengeance modes | Accountability and personal responsibility show their distinct conditions without disclosing unknown knowledge |
| Public pledge | Exact expiry deadline, equality policy, success/withdrawal costs and secret-vengeance policy remain visible and correct |
| Dates | Origin month/year is unchanged across month/year boundaries, reinterpretation and actual reload; no elapsed age or review schedule appears anywhere in browsing surfaces |
| Release cost | Free and charged private release plus declared release preview native costs, charge once and obey pledge precedence |
| Exact selection | Two same-family and mixed-family instances retain distinct targets, origins and identities; only the explicitly confirmed instance changes |
| Stale interaction | Retired Story hover/click, changed target and ended confirmation dismiss safely without payout or wrong-instance mutation |
| Player change | Old selection clears; new player cannot manage old Stories; returning follows core suspension/no-reward policy |
| Empty view | No entries/actions generated; invisible context Stories remain excluded |
| Layout and navigation | List/detail scroll, long names, text wrapping, tooltip pinning, Close and reopen work at the supported UI scale and a smaller supported viewport |

Inspect each family in the actual custom window and concise native card, with private and public variants where supported. Costs require measured deltas before and after real confirmation. Completion retains existing registered gameplay checks. Opening the UI repeatedly must leave balances, milestones, origin, review timing and pledge deadline unchanged.

The implementation plan follows written-spec review and must resolve the native feasibility gates before expanding beyond recovery. This document authorizes no installation changes, playset mutation, publication or redistribution of extracted game assets.

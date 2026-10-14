# Player-facing writing guide

This is the editorial contract for agents writing Aspirations events, decisions, option flavor, story cards, modifiers and memories. Read it with [story acceptance](story-authoring.md) and the owning `SPEC.md`. Gameplay contracts remain authoritative for what actually happens. All localization is English.

## Voice and dramatic shape

Write from the ruler's experience, normally in first person. An event should establish a specific circumstance, show why it troubles or attracts this character, and leave a choice of response. Use the named person or county, one concrete image where the recorded context supports it, and an emotional turn. Prefer one or two short paragraphs; approximately 40–90 words is an editing target, not an engine limit.

An aspiration begins with a motive, not an announcement that the system has created an aspiration. Grief can invite vengeance, custody or forgiveness; a damaged county can provoke care, wounded pride or concern for income; an acquaintance can awaken affection without already returning it. Give these choices different voices. Do not make every ruler bloodthirsty, pious, sentimental or morally certain.

Titles name the moment or tension. Option labels are a short thought, spoken response or intention a character could express. Option flavor expands what the character does or means; it does not describe a state machine. Decision descriptions explain the ruler's reason for acting; selection tooltips describe the action in the world.

Use direct verbs and varied cadence. A small, apt image is better than several abstract words such as closure, fulfillment, interpretation and circumstance. Avoid purple prose, stock grandiosity, repeated templates, modern therapeutic language and deliberately archaic spelling. Grief need not be resolved just because a target dies. Friendship and romance should sound different.

## Truth before embellishment

Only narrate facts guaranteed by the event's saved context and branch. Do not invent a witnessed murder, funeral, letter, spoken promise, burned building, shared meal, relative's gender, mutual attraction or reciprocal affection. A court acquaintance is not automatically a friend. A known culprit need not be an exposed murderer. A generic damage origin must fit both raid and siege; use a verified cause branch before asserting one.

Use uncertainty and intention when the outcome is unknown. Choosing an ambition does not execute, imprison, start construction or launch a scheme. Forgiveness does not reconcile two characters or change their opinions. Declaring a pledge does not make later actions lawful. An absent-period result cannot imply public recognition or a paid reward when the contract withholds it.

Retain exact target getters, perspective variants and established localization scope safety. Do not introduce an unverified getter merely for prettier prose. Keep public and secret outcomes distinct without disclosing hidden responsibility.

## Separate narrative from mechanics

| Native surface | What belongs here |
| --- | --- |
| Event `desc`, decision `desc` | Situation, motive, tension and the character's response |
| Option `name` | A concise roleplay choice |
| Option `flavor`, decision `selection_tooltip` | What the character intends or does in roleplay |
| Effect descriptions / **Will Happen** | Immediate changes and explicitly conditional future consequences |
| Immediate effect descriptions / **Has Happened** | A truthful report of changes already applied |
| Requirement tooltips | Eligibility and why an action is unavailable |
| Story card | Brief motive plus clearly separated objective, current status, age, review and pledge information |
| Memory / modifier description | An account of the remembered event or condition; numbers belong in native modifier effects |

Never put Stress, Prestige, XP, tax percentages, thresholds, reward policies, review timers, duplicate suppression, recorded attribution, tokens or technical caveats in narrative or option flavor. An in-world promise may mention a term, but exact timing and settlement policy still need mechanical disclosure.

Use native `flavor = <key>` for an option's descriptive tooltip. Use actual effects, `custom_tooltip` and existing `show_as_tooltip` for the consequence section. Do not type the headings **Will Happen** or **Has Happened** into localization: the engine supplies them. A `custom_tooltip` is an effect description, not a substitute for roleplay flavor.

Disclose costs before commitment. Preserve native modified Stress previews; do not replace them with an unmodified hard-coded total. Separate the immediate action from a future condition: choosing friendship keeps a desire; it does not immediately grant Diplomacy XP. Describe future rewards as conditional on fulfillment. Declaration disclosure must include the correct family objective, five-year term, public success, withdrawal/expiry cost, exact-deadline precedence and secret-vengeance settlement. Recovery must disclose its supported building pool, owner funding, fresh start and conjunctive Control requirement. Bonds remain private and grant no scheme access.

For outcome events, show already applied consequences in **Has Happened**, using a display-only summary of captured outcome context when payout occurred before the event. Never replay rewards in `immediate`, an option or `after` merely to produce a tooltip. Do not traverse an ended Story to reconstruct a preview. If an exact native resource description cannot safely be produced, use a truthful localized past-tense summary and retain measured deltas in acceptance evidence. A pending choice belongs in **Will Happen**, not **Has Happened**.

Cards are an intentional mechanical reference surface. Keep exact completion conditions and progress available there, with clear labels; remove implementation vocabulary and redundant safety essays. Do not hide necessary gameplay information in pursuit of atmosphere.

## Editing examples

These are original illustrations, not base-game quotations.

- Narrative to reject: “This bereavement has become an ambition. Closure removes 20 Stress.”
- Narrative direction: “I still reach for a voice I will never hear again. The one who silenced it lives on.” Only use the surrounding event's verified victim and culprit references.
- Choice: “I will make them answer for this.” Flavor: “I turn my grief toward bringing the culprit into my custody.” Consequence section: acquire custody after origin to fulfill the ambition; then receive its documented rewards. Do not suggest custody changes on this click.
- Decision direction: “Between the demands of my realm, some wishes have grown quiet. I should decide which still deserve a place in my life.” Selection tooltip: “Take time to reflect on my intentions.”

## Agent workflow and review

1. Read the owning contract, event/effect branches and [native writing references](knowledge/narrative-presentation.md). Classify each key by its actual consuming surface; `_tooltip` alone does not establish whether it is flavor or an effect.
2. Inventory factual scope, immediate changes, deferred objectives and already settled outcomes. Draft prose without mechanical terms, then restore every necessary disclosure to its proper native surface.
3. Edit all perspectives and related origin/management/outcome text consistently. Preserve saved identifiers, BOM, native header and escaped newlines. Debug fixtures may remain diagnostic; release prose may not.
4. Review for unsupported claims, repeated phrasing, perspective mistakes, premature rewards and information lost in relocation. Inspect script diffs: presentation additions must not change payout, eligibility or lifecycle.
5. Run repository checks and affected registered scenarios. Capture actual origin, choice hover, decision, story card, management and outcome screens with fresh logs. Check both the narrative and native section placement; static tests cannot judge taste or certify rendering.
6. Record the comparison and any uncovered gaps. Keep screenshots and raw logs ignored. Update the owning presentation contract and acceptance procedure when a disclosure surface changes.

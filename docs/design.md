# Aspirations design

Approved on 2026-10-12. This living document owns product intent, language, presentation, and the module index. Behavioral authority belongs to the linked module contracts. Initial numbers are prototype defaults; change them only with documented playtesting and the owning specification.

**Aspirations** uses repository identifier `ck3-aspirations` and script prefix `asp_`. Branding changes never rename saved identifiers.

- [Core lifecycle, emergence, capacity, reviews, pledges and rewards](../src/core/SPEC.md)
- [Vengeance](../src/stories/vengeance/SPEC.md)
- [Holding recovery](../src/stories/holding_recovery/SPEC.md)
- [Personal bond](../src/stories/personal_bond/SPEC.md)
- [Repository and distribution](repository.md)
- [Versioned modding findings](modding-notes.md)

Task 1 supplies contracts and packaging tools. Task 2 implements and verifies the core lifecycle and instance-specific management in CK3 1.20.0.4. Task 3 implements and verifies contextual vengeance. Task 4 implements first-story reviews, public commitments, suspension/return and explicit full-cap replacement. Holding recovery, personal bonds and combined acceptance remain assigned to later stages; the current bundle is a development prototype.

## Purpose and scope

Give the player character credible personal reasons to act. Personality and lived circumstances should shape strategic choices as well as the tactical choices already present in CK3 events. Success means a player can explain why a particular character cares about a goal and can pursue, reinterpret, or abandon it without treating the system as a compulsory reward checklist.

The prototype serves the current player character only and contains three families: vengeance for a loved one, recovery of a damaged holding, and closeness to a particular person. Other characters participate as targets, victims, or witnesses; they do not acquire or pursue their own aspirations through this system. Initial acceptance testing uses a single-player game and an adult landed ruler. Additional government and landless combinations are separate compatibility coverage, not promised by this prototype.

Several aspirations coexist. There is no selected main aspiration, global ambition score, or reward for keeping every slot occupied. Existing rules for wars, imprisonment, schemes, relationships, tyranny, secrets, and personality stress continue to apply.

## Language and localization scope

All authored repository content is in English: specifications, documentation, code identifiers, comments, test scenarios, tooling messages, release metadata, and player-facing text. English is the only localization included in the prototype. Use localization keys from the start, with content under `localization/english/` and files ending in `_l_english.yml`. Do not add translated text, other language directories, or copies of English text under other language headers. Additional localizations require a later scope change.

## Integration and interface

Use ordinary CK3 script modding: one story instance per aspiration, event-driven causes and completion where available, bounded maintenance for active instances, decisions for management, and character memories for important outcomes. Each family owns its eligibility, objective, interpretations, and outcome text. Shared lifecycle logic owns capacity, age, declaration, one-time completion, and cleanup. Use a unique mod namespace.

Use additive child on-actions rather than replacing existing on-action effect blocks. Do not modify the installation's base game files or RICE files. RICE is a design reference, not a required dependency. Reference game-provided artwork from the installation; do not redistribute extracted assets.

Use the existing story-cycle display in the situation list for identity and status. A shared management decision opens selection of the particular active aspiration, followed by its available actions. Context must remain bound to that selected story even when another story has the same family. Custom character-window changes are outside the initial prototype.

Logical layout, using native styling:

```text
Situations / Personal stories
  [icon] Return life to my home county
  Ambition | Active for 3 years | Private
  Origin: the county was devastated during an enemy raid.
  Target: [county]
  [ ] Restore control to 80
  [ ] Complete qualifying construction begun after this ambition

Decisions
  Review my aspirations
    Select: [individual aspiration and target]
    [Declare intention] [Reconsider] [Abandon]
```

Show exact conditions and consequences in tooltips, with the personal reason in the main text. No raw variable names, hidden target substitutions, or debug controls in normal play. All player-facing text uses the English glossary and follows the language and localization scope above.

## Verification and acceptance

Create repeatable mod-side debug scenarios for the three families and lifecycle boundaries. Run them in a disposable test campaign after backing up affected saves and profiles. Inspect rendered screens and `error.log`; a successful static read or script load alone does not establish correct gameplay.

1. With debug selection forced to succeed, a known killing of a close relative creates one eligible aspiration, explains the cause, and offers relevant interpretations. A concealed killing does not disclose the culprit. With normal selection, the documented chance and occupancy weights apply.
2. A Content character can receive a contextual recovery or vengeance aspiration. Content does not generate spontaneous status accumulation through this system.
3. Personal vengeance completes only with recorded player-character responsibility. An unrelated death yields unresolved closure, without the execution reward. Imprisonment satisfies only the accountability interpretation.
4. A damaged county records its starting state. Existing or already-started construction does not complete the objective. New player-funded construction plus control 80 completes it exactly once.
5. A relationship desire references one eligible person. Existing friendship or romance cannot instantly fulfill a newly generated desire; a new qualifying relationship can.
6. At least two concurrent aspirations can be independently inspected, reinterpreted, completed, and abandoned. No operation affects an unselected instance.
7. Capacity suppresses routine generation; a major event at capacity does not silently evict an active story. The same incident cannot be repeatedly farmed by abandoning and regenerating it.
8. Early abandonment shows and charges the correct cost once. A scheduled review allows free release. Retaining postpones the next review without resetting origin age.
9. Declaration shows a deadline and consequences. Fulfillment, deadline failure, and voluntary withdrawal each resolve once; a nearly completed aspiration cannot collect an immediate pledge bonus under the declared milestone rules.
10. Killing with a conflicting personality trait retains vanilla stress. Secret success does not automatically grant public prestige. No prototype action changes fervor.
11. Save and reload preserve targets, age, progress, pledge deadline, and one-time reward guards. Owner death, target death, loss of a county, and a change of player character cleanly resolve or suspend the appropriate instances.
12. English views contain no unresolved localization keys, clipped essential conditions, or player-visible script identifiers. Capture screenshots of origin, active story, management, fulfillment, and one invalidation case. Source and output localization directories contain only English files; no translated or duplicated alternate-language files are packaged.

Test the first vengeance story through its full lifecycle before expanding to the other families. Then test all three together, including save/reload and succession. Compare at least one naturally played character session against debug scenarios: the prototype should supply credible motives without filling all slots, spamming events, or making refusal disproportionately costly.
## Delivery boundary

The complete prototype requires a separate local mod, install instructions, repeatable dev scenarios and observed runtime evidence. Verify the complete vengeance lifecycle before adding the other families, then exercise all three together and a natural character session. Static packaging evidence does not establish gameplay. Publishing, uploading, pushing, PR creation, active-playset changes, compatibility with RICE, multiplayer and additional governments or landless characters are outside this implementation authorization.

Faith, treasury, travel, conquest and religious fervor goals are future families. The prototype grants no gold construction reimbursement, free CB, imprisonment reason, relationship, unlocked scheme, or cancellation of vanilla tyranny, opinion, secrecy and personality stress.

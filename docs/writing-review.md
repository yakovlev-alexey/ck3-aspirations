# Player-facing text review, 2026-10-14

The [writing guide](player-facing-writing.md) now governs agent-authored player text and is linked from `AGENTS.md`, product design and story acceptance. Its basis is a bounded inspection of installed CK3 1.20.1 friendship, Befriend and decision sources, recorded in [native narrative findings](knowledge/narrative-presentation.md).

A delegated editor applied the guide to shared management/pledges and all three families. An independent source reviewer checked the result; fixes qualified base Stress relief, guarded new bond tooltip reads and kept a shared third-person vengeance memory from disclosing secret responsibility. Saved identifiers, eligibility, payout timing and lifecycle remain unchanged. Display-only outcome summaries use captured numeric/boolean context and never replay rewards or traverse ended Stories.

## Before and after in CK3

| Surface | Original prototype | Revised native view |
| --- | --- | --- |
| Vengeance origin | Announced that bereavement had become an ambition | Names the known loss, the returning thought and competing responses to grief |
| Recovery origin | Control value, supported building catalogue and legal availability in the narrative | A ruler considers care for people, family standing or prosperity; exact work and Control requirements appear in the choice preview |
| Friendship origin | Court membership, relationship enums, scheme availability and review timer in the narrative | The ruler wants to know an acquaintance beyond their duties, without assuming returned affection |
| Choice hover | A bare mechanical paragraph | A roleplay sentence followed by native **Will Happen**, with deferred fulfillment clearly conditional |
| Settled outcome | Resource arithmetic or no-reward policy in the story paragraph | Personal aftermath in prose; already applied consequences under native **Has Happened** |
| Decision description | A short instruction to inspect active aspirations | The ruler reflects on wishes outside the demands of the realm; the selection tooltip describes taking time to reflect |
| Story cards | Dense prototype rules mixed with narrative | Brief motive followed by labeled objective, fulfillment, status, age and review; both friendship and romance show their correct relationship condition |
| Stale bond origin | Existing harmless fallback policy | Old choices become disabled; later dismissal preserves resources and emits no aspiration runtime diagnostic |

The revised origins and hover text fit the inspected 2560×1440, GUI scale 1.3 native layout without clipped essential text or raw localization keys. Recovery's mechanical preview is necessarily longer because the prototype supports a restricted building pool; its narrative is now two short paragraphs. Normal game-provided event artwork and windows remain in use. Native diagnostic overlays are development-mode evidence, not release UI additions.

## Verification and reproduction

- Repository tooling tests, the Python runner suite, dev/release assembly and source checks passed. Focused localization tests cover BOM/key surfaces, live-character tooltip guards, base/modifier disclosure, neutral shared memory and a strict allow-list for display-only terminal blocks.
- A structural comparison of the six changed event files against their baseline, excluding presentation additions, found unchanged effects, guards, event structure and saved IDs. No gameplay scripted-effect or trigger implementation changed.
- Registered `integrated-regression` passed 24/24 assertions, including exact rewards, replay, mixed targets, absent results, replacement and immutable baseline.
- Registered `ui-regression` passed 10/10 assertions, including actual second-Story declaration, actual save/reload, unchanged first Story and zero aspiration runtime diagnostics.
- A separate final editorial inspection captured 32 native frames. Existing `.53`, bond `.17` and `.21` assertions confirmed once-only fulfillment, harmless stale dismissal and loss with no reward. Its source/build map and baseline remained unchanged; owned profile fields/files were restored and the exact test process stopped.
- A supplementary stable-source inspection captured 20 frames, including the actual decision description/selection hover and private recovery, friendship, romance and vengeance cards. All required card text fit without raw keys. The decision requirements displayed the known native debug warning for an `is_alive` first-person trigger description; this is outside the authored narrative and is not an aspiration runtime error. The standard classifier again found zero aspiration runtime diagnostics; profile/files and baseline were preserved.

Use the [core](../src/core/tests/scenarios.md), [vengeance](../src/stories/vengeance/tests/scenarios.md), [recovery](../src/stories/holding_recovery/tests/scenarios.md), [bond](../src/stories/personal_bond/tests/scenarios.md) and [registered runner](../tools/game_runner/tests/scenarios.md) procedures. Raw before/after screenshots, source maps, logs and reports are intentionally under ignored local evidence. The baseline screenshot pass ran against the original assembled copy while editing began; it is a visual comparison record, not a passing final-source regression. A first rewrite inspection was similarly superseded by the corrected, stable final source.

## Limits

This is an editorial improvement and bounded presentation verification. It does not certify every outcome or memory perspective in native rendering, ordinary campaign frequency, actual execution/construction/relationship gameplay, or other layouts/DLC combinations. Exact modified release totals remain in native pre-choice previews; outcome context does not transport that measured total, so summaries state that the applicable cost was settled. The engine's empty **Will Happen** section on a dismissal with only past consequences is retained.

# Native narrative and consequence presentation

Status: source-inspected; measured-native section placement on CK3 1.20.1. Editorial rules are a project decision; coverage remains bounded by the linked acceptance procedures.

CK3 version: 1.20.1 (Crozier), verified from the installed `launcher/launcher-settings.json` on 2026-10-14. Earlier scope observations remain attributed to their recorded versions.

## Observation

The inspected English friendship and Befriend texts generally use the ruler's first-person experience, a concrete social situation, a feeling or uncertainty, and a brief character response. They do not recite relationship validation or reward arithmetic in the scene. Decision descriptions similarly express motive, while selection tooltips identify the action. This is an editorial reading of the samples, not a claim that every vanilla event follows one style.

| Installed-game-relative source | Reproducible sample and implication |
| --- | --- |
| `game/localization/english/event_localization/relation_events/friendship_events_l_english.yml` | `friendship.0001`, `.0003`, `.0009`, `.0014`: estrangement, uncertain affection, bereavement and betrayal have different emotional turns; names and relationships supply context |
| `game/localization/english/event_localization/schemes/befriend/befriend_outcome_events_l_english.yml` | `befriend_outcome.2001`, `.2003`, `.4003`, `.9800`: scenes and reactions distinguish success, awkwardness and shared grief |
| `game/localization/english/decisions_l_english.yml` | `pet_dog_decision`, `meditate_in_seclusion_decision`, `commission_artifact_decision`: descriptions express motive; selection tooltips express action; separate effect text supplies mechanical information |
| `game/events/_events.info` | `option.flavor` is expressly documented as dynamic flavor text in the option tooltip; `name`, inline effects and `immediate` are separate surfaces |
| `game/events/relations_events/friendship_events.txt` | `friendship.0001`: `show_as_tooltip` previews a relationship change handled by a notification event, without applying it twice |
| `game/localization/english/gui/event_window_l_english.yml` | `EVENT_OPTION_WILL_HAPPEN` and `EVENT_OPTION_HAS_HAPPENED` supply native section headings |

The [CK3 designer's own account](https://www.baudelairewelchportfolio.com/crusader-kings-3) describes narrative events as responses to system interaction and demonstrates outcomes depending on character traits and circumstances. It supports context-sensitive characterization; it is not a formal Paradox prose style guide.

### Measured native separation on 2026-10-14

The original Aspirations origin options used `custom_tooltip` without flavor and rendered a bare mechanical paragraph. Adding native `flavor` separated the roleplay sentence from the engine's **Will Happen** section in all three family origins. Numeric terminal-context branches containing only `custom_tooltip` in `immediate` rendered already settled pledge and private vengeance results, and bond loss, under **Has Happened**. The engine also displayed an empty **Will Happen** section for a consequence-free dismiss option; no custom heading or GUI override was needed.

The final disposable inspection used the existing origin/management/fulfillment entries `asp_test_core.50`, `.51`, `.53`, recovery `.20`, and bond `.10`, `.16`, `.17`, `.20`, `.21`. Real choice/confirmation input plus `.53` measured the existing once-only private/public result. Retiring the exact bond Story while its origin remained open disabled the old options; a later hover/dismiss and `.17` preserved Stress/XP. Target loss followed by `.21` measured its zero-reward closure. The final source/build map remained unchanged, and the existing runtime diagnostic classifier found zero aspiration errors. Separate registered `integrated-regression` and `ui-regression` passed their measured assertions, including actual declaration/save/reload. These are controlled fixtures, not natural emergence, a real execution or a complete prose review of every branch.

A supplementary native view confirmed the rewritten decision description and selection tooltip, and private recovery/vengeance plus both bond-mode cards. The installed shortcut `situations = "0"` in `game/gui/shortcuts.shortcuts` opens the native Situations panel; the top notification diamond is the Tips panel and is not a card entry point. Decision requirements retained a native debug-only missing-first-perspective `is_alive` warning. That warning does not change the authored description or certify an aspiration error; retain it in raw evidence rather than claiming the whole vanilla log is clean.

## Evidence and reproduction

Inspect the named keys and their consuming event/decision definitions in a locally owned installation; do not copy game files into this repository. Apply [the writing guide](../player-facing-writing.md), then follow [core presentation acceptance](../../src/core/tests/scenarios.md) and the affected family's scenarios. Fresh native screenshots must show option flavor separately from consequences; source inspection alone does not establish the final section placement.

Portable implementation: [pledge result display](../../src/core/game/events/asp_pledge_events.txt), [vengeance origin/outcome](../../src/stories/vengeance/game/events/asp_vengeance_events.txt), [recovery origin/outcome](../../src/stories/holding_recovery/game/events/asp_recovery_events.txt), [bond origin/outcome and live-character guards](../../src/stories/personal_bond/game/events/asp_personal_bond_events.txt), and [display-only/accuracy regressions](../../tools/game_runner/tests/test_integrated_localization.py). The owning scenario documents retain exact fixture commands and UI requirements; raw screenshots and machine-specific reports remain ignored.

## Implication

Write motives and actions in narrative/flavor, expose consequences through native effect descriptions, and preserve a clearly labeled mechanical reference on Story cards. A preview of an indirect effect must not execute it. Outcome summaries must report the captured result without re-entering ended Story state or paying again.

## Limits

This is a deliberately small source sample, not statistical coverage of all CK3/DLC text. Sources demonstrate supported syntax and an editorial pattern; they do not certify this mod's scopes, localization, modified Stress values or taste. A designer's portfolio supplements direct installed-source inspection and does not replace it.

[Knowledge index](README.md)

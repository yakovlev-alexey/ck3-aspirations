# Installed native sources and capability boundaries

Status: source-inspected.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

The inspected installation reports CK3 1.20.0.4 (Crozier) in `launcher/launcher-settings.json`. Source inspection establishes available scripting surfaces; runtime acceptance tests establish whether our use of them works.

| Local source, relative to the CK3 installation | Relevant capability |
| --- | --- |
| `game/common/story_cycles/_story_cycles.info` | Story setup, termination, owner death, visibility, icons, target visualization, counters, decisions, interval effects |
| `game/gui/window_situation_list.gui` | Existing story-cycle entries and their visualization |
| `game/common/on_action/_on_actions.info` | Additive child on-actions without overriding an existing effect block |
| `game/common/on_action/death.txt` | Death reason and conditional killer reference; this alone does not establish character knowledge |
| `game/common/on_action/army_on_actions.txt` | Siege and raid hooks |
| `game/common/on_action/province_on_actions.txt` | Construction start and completion hooks; completion may identify the payer |
| `game/common/on_action/relations/relation_on_actions.txt` | Relationship set, removal, and death hooks |
| `game/common/on_action/player_change_on_actions.txt` | Player-character changes |
| `game/common/character_memory_types/_character_memories.info` | Memory participants, descriptions, and duration |

The installed RICE reference uses historical aspiration modifiers, important actions, and events. Its Polabian content includes the sons of Gottschalk avenging their father; its Red Sea content includes the sons of Najah. These illustrate contextual goals but do not prove compatibility of this new system with RICE or every installed mod.

## Evidence and reproduction

[Repository compatibility rules](../repository.md), [core required surfaces](../../src/core/SPEC.md) and family contracts referenced by the index preserve the consuming code and procedures. The game-relative source table above is an inspection map; do not commit copies of installed assets.

## Implication

Inspect the relevant native definition before selecting a hook or scope. Add child on-actions and use the existing Story display; preserve installation files as read-only references.

## Limits

A listed hook or reference mod demonstrates an available surface, not correct attribution, character knowledge, actual callback delivery or compatibility with RICE/DLC/other mods. Initial bootstrap did not launch CK3; later registered acceptance has its own measured bounds.

[Knowledge index](README.md)

# Modding notes

## Local technical evidence

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
## Outstanding probes

These are implementation obligations, not verified runtime findings:

- Read-side knowledge of a killer must be verified independently of a hidden engine killer reference. No omniscient fallback.
- Construction start/completion must prove player payment and continuous county ownership; holder substitution is insufficient.
- Saved calendar dates, exact deadline comparisons and elapsed age through save/load/suspension require a minimal dev probe.
- Event-held story references must keep the chosen instance through subsequent options and stale-event attempts.
- Additive native on-actions and visible story entries must be observed in-game before accepting their use.

No CK3 process was launched for Task 1. No native gameplay fixture passed. Durable findings include game version, game-relative source reference, probe and observed result. Machine paths, saves, backups, logs, screenshots and transient attempts belong in ignored `.local/MODLOG.md`.

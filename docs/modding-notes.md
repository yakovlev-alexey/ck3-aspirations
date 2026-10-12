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

The initial repository-bootstrap task did not launch CK3 or pass a native gameplay fixture. Later automation findings are documented below; they do not certify unrelated gameplay. Durable findings include game version, game-relative source reference, probe and observed result. Machine paths, saves, backups, logs, screenshots and transient attempts belong in ignored `.local/MODLOG.md`.

## Verified console-file automation — CK3 1.20.0.4 Crozier

A real one-command smoke ran three fresh owned processes from the same disposable baseline, measured its private counter 0→7 once despite replaying request 3, and observed native `current_date` 430243→430244 after `tick_day 1`. These are automation fixture findings, not evidence for unfinished core gameplay.

Installed `game/_commandline_options.info` documents `-loadsave=<name>`. On this host an absolute baseline path was rejected with `Could not load save game`; placing a uniquely named disposable `.ck3` copy under selected user-data `save games/` and supplying its filename loaded directly into the intended paused campaign. `-suppress_error_log` prevents auto-opening the log and still writes error.log. No menu navigation is needed between repeated launches.

`run asp_automation_request.txt` reads that owned filename from the user-data `run/` directory. Fresh debug.log records `Running console command: run ...`, then native effects. UTF-8 BOM is required for request and authored native TXT/YML bytes on this engine. The current/root scope of the run file was the player character, but debug localization via ROOT getters produced empty fields; `GetPlayer.MakeScope.Var('variable').GetValue|0` emitted measured integer values. Installed effects docs explicitly support localized `debug_log` strings, and vanilla English localization contains this player-variable getter pattern.

Console effect description generation evaluates conditions before setters in the same request execute. Capture/initialize the next request during bootstrap and guard absent variables before comparisons. Documented native `hidden_effect` hides internal descriptions but still evaluates conditions; it alone does not prevent premature reads. Native completion for day advancement is a delayed hidden event with saved session/request identity, and the Python side waits for matching ACK before the bounded `tick_day` command. A requested number alone is never completion evidence.

One tick generated tens of thousands of unrelated native debug lines. Bound the retained partial record and drain complete lines in chunks; rejecting the whole batch for being large loses valid terminal telemetry. Rotation/truncation must fail rather than silently accepting old logs. Console-only fixture use can produce static unused-variable/flag diagnostics; retain and classify those separately from actual namespace Script system errors and baseline vanilla religion-on-action errors.


## Task 2 story and calendar capability probes — CK3 1.20.0.4 Crozier

Generated script docs in the disposable test record show `is_landed` requires a county or barony; `is_ruler` alone also accepts landless title holders. The core reservation guard uses both predicates. Engine acceptance of the complete eligibility path still requires a negative in-game case.

A direct `create_story` saved reference survived an event option and actual native save/load. In the loaded campaign, a one-day tick changed the numeric `current_date` delta by exactly one while retaining the captured target, origin, next review and timed-variable state. Native serialized durations for `months = 24` and `years = 8` were 720 and 2920 days. The core stores origin and next review as numeric date values using these measured initial durations. Full scheduled-review and pledge boundary behavior remains assigned to Task 4.

The scope/calendar probe emitted `ASP_PROBE CORE EVENT_SCOPE PASS`, `CALENDAR_DAY PASS`, and `SAVE_LOAD_STATE PASS` in the recorded fresh intervals. These markers prove the primitive capabilities, not C01–C04 core gameplay. UI presentation, terminal callbacks, count caps and core-instance reload remain pending their own live fixtures.

Automation safety review found real-profile `game.autosave=YEARLY`; October1→2 smoke does not certify autosave behavior across arbitrary boundaries. The runner now uses a read-only structural preflight requiring `NO_AUTOSAVE` and actual redirected Windows Documents user data before launch. It has no verified alternate-profile flag and does not automatically edit settings. Keep any short-test preference backup/restoration targeted to this field; never probe preservation by overwriting real autosaves.

CK3 1.20.0.4 native Settings → Game → Autosave Interval → No Autosave persists `game.autosave.value="NO_AUTOSAVE"`. `NEVER` is not a valid enum: debug.log reports a fallback to YEARLY. Automation checks the accepted enum before launch, after startup and before input, including retained-session day advancement. Keep the preference disabled until the owned game closes, then restore only the captured original field.

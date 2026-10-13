# Console transport, profile ownership and DPI

Status: measured-native (console/profile); source-inspected (Windows coordinates); unverified (general DPI portability).

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

A real one-command smoke ran three fresh owned processes from the same disposable baseline, measured its private counter 0→7 once despite replaying request 3, and observed native `current_date` 430243→430244 after `tick_day 1`. These are automation fixture findings; Task 2 core gameplay was accepted separately through the later core-regression and UI/save-load evidence.

Installed `game/_commandline_options.info` documents `-loadsave=<name>`. On this host an absolute baseline path was rejected with `Could not load save game`; placing a uniquely named disposable `.ck3` copy under selected user-data `save games/` and supplying its filename loaded directly into the intended paused campaign. `-suppress_error_log` prevents auto-opening the log and still writes error.log. No menu navigation is needed between repeated launches.

`run asp_automation_request.txt` reads that owned filename from the user-data `run/` directory. Fresh debug.log records `Running console command: run ...`, then native effects. UTF-8 BOM is required for request and authored native TXT/YML bytes on this engine. The current/root scope of the run file was the player character, but debug localization via ROOT getters produced empty fields; `GetPlayer.MakeScope.Var('variable').GetValue|0` emitted measured integer values. Installed effects docs explicitly support localized `debug_log` strings, and vanilla English localization contains this player-variable getter pattern.

Console effect description generation evaluates conditions before setters in the same request execute. Capture/initialize the next request during bootstrap and guard absent variables before comparisons. Documented native `hidden_effect` hides internal descriptions but still evaluates conditions; it alone does not prevent premature reads. Native completion for day advancement is a delayed hidden event with saved session/request identity, and the Python side waits for matching ACK before the bounded `tick_day` command. A requested number alone is never completion evidence.

One tick generated tens of thousands of unrelated native debug lines. Bound the retained partial record and drain complete lines in chunks; rejecting the whole batch for being large loses valid terminal telemetry. Rotation/truncation must fail rather than silently accepting old logs. Console-only fixture use can produce static unused-variable/flag diagnostics; retain and classify those separately from actual namespace Script system errors and baseline vanilla religion-on-action errors.

### Historical bare-runner profile findings

Automation safety review found real-profile `game.autosave=YEARLY`; October1→2 smoke does not certify autosave behavior across arbitrary boundaries. The bare runner added a read-only structural preflight requiring `NO_AUTOSAVE` and actual redirected Windows Documents user data before launch. It has no verified alternate-profile flag and does not automatically edit settings. Keep any short-test preference backup/restoration targeted to this field; never probe preservation by overwriting real autosaves.

CK3 1.20.0.4 native Settings → Game → Autosave Interval → No Autosave persists `game.autosave.value="NO_AUTOSAVE"`. `NEVER` is not a valid enum: debug.log reports a fallback to YEARLY. Automation checks the accepted enum before launch, after startup and before input, including retained-session day advancement. Keep the preference disabled until the owned game closes, then restore only the captured original field.

### Windows coordinate boundary

The inspected pre-UI `WindowsBackend` binds foreground HWND/PID to its owned process, calls `SetProcessDPIAware`, and captures the client rectangle using `GetClientRect` plus `ClientToScreen`. This establishes implementation behavior only. It does not establish that screenshot pixels, DPI-scaled client positions and native input coordinates are interchangeable. A click sent to a coordinate is not proof of correct Story selection.

### Measured exact-Story UI and tooltip dispatch

Status: measured-native on CK3 1.20.1 (Crozier, modified checksum) at a 2560x1440 client, Windows DPI120, GUI scale1.3 and local saves. The earlier observations above remain attributed to CK3 1.20.0.4.

The registered `ui-regression` opened native management, selected its second eligible vengeance Story and reached the correct declaration confirmation. Its first confirmation option appeared in the left half of the centered event panel; clicking the earlier right-side coordinate left the confirmation open. After correcting that measured point, native telemetry showed exactly the second Story declared, the first private, deadline+1825, and unchanged targets, IDs, origin/review dates, Stress and Prestige. A new native Save Game file was loaded by a fresh process; its new HWND/PID required a fresh geometry measurement before screenshots or input. Reload telemetry matched the saved state at the same native date. The final managed report recorded 10/10 assertions, zero aspiration runtime diagnostics, ten ordered frames, a retained save hash, exact-process cleanup, profile restoration and an unchanged baseline. Reproduce with the [registered UI scenario](../../tools/game_runner/tests/scenarios.md#a13-registered-ui-regression) and [native fixture](../../src/core/tests/scenarios.md#registered-exact-story-ui-and-persistence-sequence); local raw evidence remains ignored.

The first otherwise state-correct UI pass failed its strict diagnostic gate: opening a vengeance Story's management tooltip evaluated the recovery `asp_holding_recovery_can_declare_trigger` on the vengeance Character target. CK3 logged a landed-Title `holder` type error and null `county_control` errors from `asp_recovery.txt:64`. Adjacent family checks inside an ordinary `OR` did not isolate the branches during tooltip construction. Explicit `trigger_if` family limits in `asp_family_can_declare_trigger` prevented entry into the recovery predicate; the same registered native sequence then passed with zero aspiration runtime diagnostics. Keep this strict log gate alongside exact state checks when changing mixed-family UI dispatch.

## Evidence and reproduction

[Runner SPEC](../../tools/game_runner/SPEC.md), [automation scenarios](../../tools/game_runner/tests/scenarios.md), [Windows backend](../../tools/game_runner/windows.py), [profile negative tests](../../tools/game_runner/tests/test_profile.py), [transport/evidence tests](../../tools/game_runner/tests/test_runner.py) and [native bridge](../../src/core/tests/game/common/scripted_effects/asp_automation_debug.txt). Reproduce launch/day/replay with registered `automation-smoke` from a disposable baseline; the runner SPEC owns the current managed-session command and profile-restoration policy. The measured UI sequence uses [named operations](../../tools/game_runner/ui_scenario.py), [family declaration dispatch](../../src/core/game/common/scripted_triggers/asp_core.txt) and the registered `ui-regression` with both native log intervals.

## Implication

Resolve actual OS Documents, keep launch preferences targeted and owned, wait for matching native ACK/DONE identity, preserve log provenance and stop only the owned process before restoration/rebuild. Use the managed workflow documented in the runner SPEC for temporary profile preparation. Named UI operations must validate geometry, native identity and postconditions as well as capture actual frames.

## Limits

The historical bare runner required an already safe profile and did not automatically edit it; this does not describe newer managed preparation. No alternate-profile flag was verified. The UI measurements validate only the stated CK3 1.20.1 host layout and input sequence, not arbitrary DPI/scales, popups, autosave boundaries or other versions. Recheck the visible panel location and exact telemetry before adopting a new geometry.

[Knowledge index](README.md)

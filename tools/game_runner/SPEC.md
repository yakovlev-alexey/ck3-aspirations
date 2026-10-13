# CK3 scenario automation

Approved direction: the user requested implementation and verification on 2026-10-12 after reviewing console/file transport, native test helpers, measured log results and an optional thin MCP interface. This is a development tool for Aspirations, not player-facing gameplay.

## Contract

A Python standard-library runner controls one explicitly configured, disposable CK3 single-player session. It writes native CK3 requests atomically, asks the debug console to run the request file, reads fresh tagged telemetry and returns structured JSON. No LLM or screenshot interpretation is required between scripted scenario steps. MCP is a thin local stdio adapter over the same runner. No package installation or global agent configuration changes are included.

Keep Python code and this living specification together under tools/game_runner/. Keep automation acceptance scenarios under tools/game_runner/tests/scenarios.md. Native bridge fixtures belong in src/core/tests/game/ and must be excluded from release. Story-specific tests remain beside their stories; this bridge must not certify incomplete gameplay. Core runtime source is owned by its gameplay task; bridge-only automation commits do not certify it.

Use English throughout. Machine paths, configuration, logs, screenshots, saves and reports belong under ignored .local/. Use the existing Python runtime; standard library only. Optional screenshots may use already-installed Pillow but the command protocol and tests cannot depend on it. Do not copy AGI-CK3 code or vanilla game files. No installation-directory edits, custom GUI overrides, new loader or release dependency. Console keyboard input is authorized for short test sessions; validate the intended game process/window before each input batch, fail on focus loss, and do not drive unrelated applications.

## Execution and protocol

Public operations are a bounded scenario registry, observation and bounded day advancement. Registered automation-smoke verifies measured fixture mutation and date advancement; core-regression verifies bounded Task 2 gameplay cases C01, C02, C09, C10 and combined eligibility C11. The registered vengeance-regression executes shared V01-V06 native family fixtures and validates complete identity-bound numeric measurements; actual GUI execution/rendering remain mandatory separate acceptance. Scenario IDs and argument schemas are validated before any side effect. No arbitrary shell/effect execution API is exposed by MCP.

Each request carries protocol version, unique session identity and monotonic request ID. Native handlers consume each request once and re-acknowledge duplicates without applying the effect twice. A completed result is distinct from accepted/ACK. Reject conflicting duplicate results, malformed messages and mismatched identities; ignore historical/unrelated logs. Atomic request replacement, fresh byte cursors, partial-line buffering, log rotation/truncation detection, bounded waits and single-flight execution prevent false success. A save/load rollback cannot silently turn an old request into a new mutation: establish a fresh session after reload and validate it before work.

Report status as passed, assertion_failed, transport_error or timeout. Include scenario/version, request identity, initial/final measured state, elapsed game date where relevant, assertions, evidence paths and repeat count. Never claim a value observed solely because it was requested. Day advancement completes only after observing the requested date delta. Use a controlled disposable baseline. Focus loss, an unresponsive console or absent ACK/DONE stops boundedly. Generic event-window inspection and automatic event choices are not implemented; debug `tick_day` is not proof that normal simulation can proceed through every popup.

Configuration explicitly identifies game executable, existing user-data directory, disposable baseline save and local output root. Resolve and validate paths; do not follow reparse points into unexpected roots or overwrite arbitrary files. Request files use a dedicated owned name and are cleaned or restored. Only exact processes launched by this runner may be stopped. Do not adopt an unrelated running CK3 session automatically. Avoid logging full launcher command lines or credentials.

The runner can restart its owned game with the same baseline save to reset scenarios if an in-session load route is not verified. The three-run acceptance command must need no manual navigation after initial configuration. Save/checkpoint commands beyond that verified path are not promised. Track affected profile settings and restore only owned changes; preserve all user saves. Restore the original launcher selection (No mods) at final cleanup if the prior task's test playset remains selected, using supported UI.

## Acceptance

A01: one command runs automation-smoke three times from the same baseline save; measured starting state and final assertions agree across repetitions. It runs the actual game, without manual menu navigation between repetitions.
A02: deliver one mutation request twice; both responses refer to the same identity and only one measured state change occurs.
A03: stale/unrelated/partial/malformed telemetry, a truncated/rotated log and a conflicting result cannot create a passing report; unit tests cover these without launching CK3.
A04: missing game, lost foreground, timeout, invalid scenario/arguments and concurrent requests produce bounded, explicit errors. The runner never types into the wrong window.
A05: an actual day-advance request is acknowledged and completes only after the game date advances; save reload establishes a fresh session. Native observations verify real state.
A06: the MCP server completes initialization, tools/list and tools/call over real subprocess stdin/stdout. It advertises only implemented operations; stdout contains protocol messages only. Invalid requests yield protocol/tool errors and no game input.
A07: existing build tests and dev/release checks pass; release contains no bridge scripts, markers or automation files. Real evidence remains ignored. The final task-owned game process is stopped and affected settings/playset restored.

## Current status

CLI/native implementation is present. Standard-library tests and real CK3 1.20.0.4 smoke acceptance have passed; detailed final evidence is recorded in the ignored task report. The local MCP adapter implements A06 with real-subprocess tests; measured live acceptance is recorded in the ignored task report. Automation-smoke alone does not certify core gameplay; Task 2 has a separate accepted core-regression report and mandatory UI/save-load evidence.

## Stable native IDs

Reserve `asp_test_automation.1` for bootstrap and `asp_test_automation.2` for delayed day completion. All bridge variables/effects use `asp_test_automation_`. These IDs must never be repurposed.

## Implemented Python interface

`GameRunner(config)` accepts a validated `Config` or JSON configuration path. `run_scenario(scenario, repeat=1)` for `automation-smoke`, `core-regression`, `vengeance-regression`, `lifecycle-regression` and `recovery-regression` accept integer repeat counts 1–10. `observe()` and `advance_days(days)` lazily open an owned baseline session; days is an integer 1–30. `close()` is idempotent and returns a JSON object. Each operation returns a JSON-serializable report. Invalid scenario/argument/configuration raises `ValueError` before game input; concurrent calls return `transport_error`. Native/Windows/log failures return `transport_error`, and absent completion returns `timeout`. The CLI prints only its final JSON report and exits 0 for `passed`, 1 for operational failure, or argparse's 2 for invalid CLI arguments.

A runner holds an exclusive directory lock in the selected user-data directory until `close()`. CLI and MCP must reuse this implementation, including its lock; the MCP adapter must close the runner on stdio shutdown. A stale lock is not adopted or automatically removed. Transport failure stops the exact owned process and clears its session; a later operation starts again with a new identity. Runner instances may not adopt an existing CK3 process.

```json
{
  "game_executable": "<absolute path to ck3.exe>",
  "user_data": "<explicit existing CK3 user-data directory>",
  "baseline_save": "<absolute disposable baseline .ck3 path>",
  "output_root": "<repository>/.local/automation",
  "startup_timeout": 90,
  "request_timeout": 15,
  "startup_settle_seconds": 25
}
```

All paths are explicit absolute paths; unknown configuration fields and reparse ancestors are rejected. Output stays under this checkout's ignored `.local/`. User-data must already exist and contain `save games/`. The baseline is read-only; the runner makes an exclusive uniquely named `asp_automation_<random>.ck3` copy in that save directory, supplies its filename to `-loadsave`, and removes only that copy on close. It starts CK3 with `-debug_mode`, `-suppress_error_log`, `-skip_checksum`, and `-disable_ai`. The suppress flag prevents automatically opening error.log; it does not disable the log. The existing selected dev playset must contain Aspirations; the runner does not edit launcher selection.

A startup settling bound gives CK3 time to load; the first matching native bootstrap result proves readiness. If this host loads more slowly, adjust the explicit bound (positive, maximum 180 seconds). Missing dev content or an unresponsive console produces bounded failure; arbitrary visible event windows are not inspected or handled. HWND/PID/foreground are checked before every key event. A failed chord releases only its own held modifier. An optional screenshot uses already-installed Pillow; it is not a transport dependency.

## Native wire and scenario

The runner atomically replaces `run/asp_automation_request.txt` under selected user data. Existing bytes of that dedicated file are restored on close; a newly created file is removed. Request content is UTF-8 BOM native script calling a bounded bridge effect with `VERSION = 1`, numeric random `SESSION`, monotonic `REQUEST`, literal operation and bounded days. It is wrapped in `hidden_effect` to hide internal effect descriptions. Bootstrap also guards variable existence before comparing freshly set state: hidden effects still evaluate conditions during console description generation. There is no user-facing arbitrary effect input.

Localized native telemetry is `ASP_AUTOMATION|1|<session>|<request>|ACK` or `...|DONE|counter=<measured integer>|date=<current_date integer>`. Rejection is `...|ERROR|reason=<bounded reason>`. `GetPlayer.MakeScope.Var(...).GetValue|0` reads actual player-owned bridge state; the console-run ROOT localization getter did not work on this engine. The report keeps raw native numeric dates and checks their measured difference. Fresh cursors ignore pre-existing log bytes; partial byte lines and split UTF-8 remain buffered, and complete unrelated daily output is drained in bounded chunks. Rotation, truncation, in-place replacement, malformed tagged records and conflicting terminals fail.

The native bootstrap preserves a pre-existing fixture counter, initializes absent counter to zero, and establishes session/request identity plus the expected next request. Only the most recently accepted request's result is cached. Delivering it again re-acknowledges pending work or re-emits the same completed result; it never repeats the mutation or schedules another callback. Older/out-of-order requests are rejected. A new process always loads the pristine copy before fresh bootstrap; in-session reload is not offered.

`automation-smoke` observes initial zero, adds 7 to its private fixture counter, replays the same mutation identity, independently observes unchanged counter 7, then requests one day. Advance waits for its matching ACK before `tick_day 1`; `.2` completes only when its delayed native event executes. Each repetition restarts the owned game from the same staged baseline, receives a fresh session and verifies the same initial date. Reports contain measured initial/mutation/replay/observation/final states, assertions, baseline SHA-256, owned PIDs, per-repetition fresh logs and an optional actual final screenshot. Engine/static errors are retained as evidence; a passing fixture does not establish unrelated mod gameplay correctness.

`.1` is a manual debug bootstrap/observe entry with fixed session 1; production automation uses the parameterized equivalent effect. `.2` is the pending advance callback. The manual `.1` is explicitly orphan; `.2` has a native delayed-event caller. Automation-smoke uses only `asp_test_automation_` bridge variables and does not touch core gameplay. The separately registered core-regression case invokes dev-only Task 2 assertions.

## Verified commands

```powershell
python -m unittest discover -s tools/game_runner/tests -v
python -m tools.game_runner --config .local/automation/config.json run automation-smoke --repeat 3
python -m tools.game_runner --config .local/automation/config.json run core-regression --repeat 1
python -m tools.game_runner --config .local/automation/config.json run vengeance-regression --repeat 1
python -m tools.game_runner --config .local/automation/config.json observe
python -m tools.game_runner --config .local/automation/config.json advance-days 1
```

Resolve `python` to the existing host runtime. No SDK, package install, global MCP setup or game-install edit is required. The CLI always closes its owned session; MCP can keep one runner alive between supported operations and must explicitly close it on shutdown. Profile/playset cleanup shared across CLI and MCP acceptance belongs to the overall test owner. Preserve concurrent gameplay work when changing the runner; Task 2 core source and the bounded runner extension are reviewed together in their owning task.

## Autosave/profile preservation preflight

Version1 has no verified alternate-profile launch flag. Before any CK3 process launch, the Windows backend resolves actual redirected Documents with `SHGetFolderPathW(CSIDL_PERSONAL)` and requires configured `user_data` to equal its `Paradox Interactive/Crusader Kings III` directory. Launcher-specific/alternate profile overrides are unsupported and rejected.

The backend reads `pdx_settings.txt` without changing it and structurally parses the `game` → `autosave` → `value` preference. It requires exactly `NO_AUTOSAVE` (the native No Autosave option); missing, duplicate, malformed or unsafe settings are rejected before process launch. `NO_AUTOSAVE` in comments or another section cannot satisfy this preflight. This protects real autosave files when a1–30-day operation or a retained MCP session crosses an autosave boundary.

Prepare a disposable test session by selecting No Autosave in CK3 settings before launching automation. If the overall test owner changes this preference for a short test, take a current targeted backup, change only this exact owned preference and restore its original value after closing the owned game. The runner never changes it automatically. Existing October1→2 smoke evidence predates this safety preflight and does not establish arbitrary-boundary autosave behavior. No destructive autosave probe is authorized or needed.

## MCP stdio interface

Start from the repository directory with the existing Python runtime:

```powershell
python -m tools.game_runner --config '<absolute configuration JSON path>' mcp
```

This is a local subprocess transport implementing **MCP 2025-11-25** explicitly, following the official [lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle), [stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) and [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) contracts. This statement does not claim that version is the newest specification. No SDK, network listener or global MCP registration is provided. Use the same configuration schema above and a client launch command/argument array such as:

```json
{
  "command": "<absolute existing python.exe path>",
  "args": ["-m", "tools.game_runner", "--config", "<absolute configuration JSON path>", "mcp"],
  "cwd": "<absolute repository path>"
}
```

`cwd` is illustrative client configuration; actual client launch settings vary. Configure the repository working directory or equivalent module search path. All stdout is newline-delimited UTF-8 JSON-RPC 2.0; diagnostics go to stderr. Initialize with `protocolVersion`, object `capabilities`, and `clientInfo` containing string `name`/`version`. The server negotiates only `2025-11-25`, returning that supported version if the client's requested version differs; an incompatible client must disconnect. Then send `notifications/initialized`. Tools cannot execute before this notification. `ping` returns an empty object. `tools/list` returns one fixed page and advertises only tools, with `listChanged: false`.

| Tool | Arguments | Runner operation |
| --- | --- | --- |
| `aspirations_run_scenario` | Required `scenario` in `automation-smoke`, `core-regression`, `vengeance-regression`, `lifecycle-regression`, `recovery-regression`; optional integer `repeat: 1..10`, default 1 | `run_scenario` |
| `aspirations_observe` | Empty object or omitted arguments | `observe` |
| `aspirations_advance_days` | Required integer `days: 1..30` | `advance_days` |

Tool argument schemas use JSON Schema 2020-12; additional properties, booleans/fractions in integer positions, and out-of-range values are rejected before runner input. Envelope errors/unknown methods/unknown tools use JSON-RPC errors. Tool validation and backend failures return `isError: true`; a passed runner report returns `isError: false`. The unchanged report is both `structuredContent` and serialized text `content`. No arbitrary script, shell, path, console or filesystem tool is exposed. Observe may launch/bootstrap a disposable session, so it is not advertised as a side-effect-free operation.

For example, send each object below as one physical line:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"local-client","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"aspirations_run_scenario","arguments":{"scenario":"automation-smoke","repeat":1}}}
```

Implementation limits: each input line is at most 65,536 bytes including newline. Oversized or unterminated lines receive an error and close the connection; malformed JSON/UTF-8, duplicate JSON keys, non-finite numbers and batch arrays are rejected. Request IDs are non-null strings/integers and cannot be reused; reconnect after 10,000 requests. Notifications receive no replies and never invoke tools. The dispatch loop runs one call at a time in arrival order; all calls reuse one runner and its user-data ownership lock. Another CLI/server cannot acquire that lock. There is no progress reporting, asynchronous task API or interruptible cancellation: notifications arriving during a call are read after its bounded native work finishes. Client timeouts must allow configured startup/native waits across the requested repeat count (not a single 15-second request timeout). Close stdin for clean shutdown; EOF finishes any current bounded operation, calls `close()` and exits. A cleanup/transport failure exits nonzero and reports on stderr; forcibly terminating the server cannot guarantee cleanup.

A retained server keeps its disposable session until EOF, so autosave NO_AUTOSAVE must remain configured throughout. Overall live-test cleanup restores only the test-owned autosave preference and original launcher selection after shutdown, audits staged save/request/lock/process absence, and preserves source baseline/user saves. A single live MCP smoke invocation verifies the full client→stdio→runner→native→measured-report path; Task1's separate triple CLI proof remains the restart acceptance evidence.

CK3 1.20.0.4 accepts the persisted enum `NO_AUTOSAVE`, verified by the native settings UI. The previously assumed `NEVER` enum is invalid and falls back to YEARLY; it is now rejected. Windows input validation repeats the read-only profile check after startup settling and before console/key batches, including before a retained-session day tick. A normalized or externally changed unsafe preference therefore stops work before further input. Deterministic regressions cover post-load and pre-tick rewrites; live evidence confirms no enum fallback with the accepted setting. This establishes the controlled launch route, not a destructive arbitrary-boundary autosave probe.

## Core regression contract

The registered core-regression operation starts each repetition from the pristine disposable baseline. The dev-only native fixture measures C01 cap counts and rejected extras, C02 callback/slot/stress deltas, C09 forgiveness stress compared with measured ordinary early abandonment on the same owner, C10 effective no-reward policy and stress, and C11 combined AI and landless exclusion. A result requires the full identity-bound case field set and exact expected values; absent fields or missing completion are transport failures, while a native FAIL marker or wrong measured value is assertion_failed. Duplicate replay must carry the same cached measurements. Existing automation-smoke wire fields and behavior remain valid. Reports keep each measured value, assertions and fresh log evidence.

This operation does not open or choose selector events. C03 requires a real click on the second of two same-family stories, an independent callback, and a stale-action click. C04 requires an actual save and reload. Native setup/assertion events and the exact UI procedure are specified in the core scenarios; neither screenshot existence nor a scripted callback alone certifies UI interaction. New automatable behavior checks and fixes must gain a registered scenario or assertion in an existing one with inputs, observable assertions and retained evidence. Shared native fixtures alone are insufficient; required UI actions use scripted setup/assertions plus mandatory documented manual steps.

## Vengeance regression telemetry

`vengeance_regression` uses the unchanged synchronous identity/replay flow and returns all 23 numeric fields in `VENGEANCE_FIELDS`: case flags plus independent origin counts, hidden/known/exposure counts, death and custody deltas, memory count, eligibility/cost flags and vanilla action versus closure deltas. The parser rejects unknown, missing, malformed or conflicting measurements; the runner independently checks literal expected outcomes even if a native case flag says pass. Duplicate delivery replays the cached completed result without rerunning fixtures. The suite reads the same baseline date, uses actual native death/prison child hooks, and does not advance days or substitute scripted execution for an actual player click.

## Registered lifecycle-regression

The bounded `lifecycle-regression` scenario runs shared P01-P06 effects with complete integer telemetry, independently checks costs/counts/absence and UI-replay memory postconditions, and verifies exact cached replay. It snapshots that logic interval, restarts from the same unchanged baseline, prepares shared near-boundary calendar state, verifies its exact saved-state precondition, advances one real native day, and checks review/declaration/expiry measurements plus replay. Separate fresh sessions prevent intentional logic-fixture deaths and delayed native grief from contaminating the calendar test. The precondition is not actual save/load; native Save Game/load and UI/player-switch/succession procedures remain mandatory in core scenarios.

Reports retain both logic and calendar logs, request/session identities, baseline hash, raw deltas and an aspiration parser/runtime diagnostic count. Any such diagnostic in either interval fails the scenario, while known static unused-state and unrelated vanilla frames are classified separately. All operations remain private scenario implementation; there is no arbitrary script API or new framework. CLI and MCP expose only the registered scenario name and existing bounded repeat/day parameters.


## Registered recovery-regression

`recovery-regression` invokes the shared dev-only H01–H05 effects. All 28 numeric fields in `RECOVERY_FIELDS` are mandatory: five case flags, Stress/XP/modifier payout, independent nominal-base10 abandonment and base15 pledge Stress controls, Prestige penalty, invalid-payer/cancellation/replay counts, and recorded origin Control. The runner independently compares actual outcomes, rejects missing/malformed telemetry, verifies fresh session/date/baseline, checks exact cached replay and rejects aspiration runtime/parser diagnostics. ACK or native PASS alone cannot pass.

H03 includes native child-on_action dispatch after slot reservation: slot0 must retain a valid original-payer start token and completion proof. Its scripted occupancy model is ongoing0; actual GUI ongoing1/payment/completion/three-year modifier and later-frame UI procedures remain mandatory in the owning recovery scenarios. H04 typed transfer fixtures establish policy, not a played lost war. There is no arbitrary effect API, new dependency or change to deterministic `-disable_ai` launch policy; the separately bounded AI payer capability launch is evidence only.

The additional recovery measurements independently require title-loss/terminal token isolation, matching ordinary cleanup, newer-Story Stress/XP/modifier/replay and AI-only observer/cache-reset checks; missing measurements or incorrect outcomes cannot pass.

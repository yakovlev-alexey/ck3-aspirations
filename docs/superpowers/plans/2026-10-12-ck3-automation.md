# CK3 Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. The user selected fresh gpt-6.1-sol/high implementers and the controller as reviewer.

**Goal:** Run repeatable CK3 scenarios without per-step computer use, exposed through CLI and local MCP.
**Architecture:** Python standard-library runner, console-triggered atomic request files and dev-only CK3 telemetry helpers. A thin stdio MCP adapter reuses the runner.
**Tech Stack:** Existing Python, ctypes Win32 input, unittest, CK3 native script, existing PowerShell assembly tools.
**Spec:** tools/game_runner/SPEC.md

## Global Constraints

- English only; no new dependencies, global MCP registration, push, PR or publication.
- Preserve all existing unfinished core changes. Do not stage or modify them unless a narrow integration conflict is reported to the controller.
- Native automation content lives only in src/core/tests/game/ and is excluded from release.
- Single sequential implementer owns the real game; controller reviews code and evidence.
- Machine state/evidence stays ignored in .local/; use explicit paths and exact owned PIDs.
- User authorized short launcher/CK3 input and disposable-save tests; restore original No mods playset.
- Repository writes outside sandbox roots require require_escalated. No installation-directory edits.

## Review Focus

- Old or partial log records masquerading as current results: task 1 parser/identity tests.
- Repeated requests mutating twice, including reload rollback: task 1 unit and live replay tests.
- Keyboard focus loss or unknown process: task 1 driver failure tests and live process verification.
- Timeout/exception leaving live processes or altered profile state: task 1 cleanup tests, task 2 final cleanup evidence.
- Protocol wrapper bypassing validation or emitting diagnostics to stdout: task 2 subprocess tests.

### Task 1: Implement and verify the CLI and native bridge

**Files:**
- Create: tools/game_runner/{__init__.py,__main__.py,runner.py,protocol.py,windows.py}
- Create: tools/game_runner/tests/{test_protocol.py,test_runner.py,scenarios.md}
- Create: src/core/tests/game/events/asp_automation_debug_events.txt
- Create as needed: src/core/tests/game/common/scripted_effects/asp_automation_debug.txt and localization/english/asp_automation_debug_l_english.yml
- Update: tools/game_runner/SPEC.md, docs/repository.md, docs/modding-notes.md, README.md
- Existing core implementation and its fixtures are outside ownership; use distinct asp_test_automation namespace and variables.

**Interfaces:**
- Consumes: existing build.ps1/check.ps1/install-dev.ps1; explicit local configuration with paths from the real host.
- Produces: GameRunner(config).run_scenario(name, repeat=1), .observe(), .advance_days(days), .close(), returning JSON-serializable reports; single-flight ownership guard shared by CLI/MCP. CLI: python -m tools.game_runner --config PATH run automation-smoke --repeat 3, with observe and advance-days subcommands. Small justified signature adjustments must be recorded in SPEC for task 2.

- [ ] Read the spec, existing builder and previous local UI/script-doc probes; record initial dirty-file hashes and baseline HEAD. Read applicable test-driven-development and game-automation skills. Do not resume unfinished core implementation.
- [ ] Write failing unittest cases for A02-A05 failure boundaries: identity filtering, duplicate/conflicting terminals, split UTF-8/partial lines, rotation/truncation, timeout, focus rejection, process ownership and cleanup. Use deterministic injected clock/I/O boundaries rather than sleeps.
- [ ] Verify the tests fail for the absent behavior, then implement the small protocol parser, safe atomic request writer and Windows input/process adapter. Bind input to the validated HWND/PID; keep output structured and logs credential-free.
- [ ] Implement dev-only native bootstrap/request dispatch/observation and an independent automation-smoke fixture. Reserve stable event IDs in SPEC first. Use measured numeric state and game dates, not requested-value echoes. Test replay by attempting the same mutation twice.
- [ ] Implement the scenario runner/CLI and an owned-session reset to an explicit disposable baseline, using verified launch flags or native load behavior. Keep all loops bounded and obtain a fresh session after reset. Use installed source/generated docs to resolve engine syntax; stop repeating an identical failing approach after three attempts.
- [ ] Run unit tests, existing PowerShell tooling tests and dev/release build checks. Do not rebuild dev while CK3 runs. Verify bridge files are excluded from release.
- [ ] Run A01/A02/A05 in CK3: one CLI invocation, three repetitions from the same baseline, no manual navigation between runs. Preserve structured reports, fresh logs, baseline hash and one actual screenshot. Inspect error.log for this namespace and distinguish pre-existing incomplete-core issues. If the real bridge exposes a defect, fix it and rerun the affected acceptance.
- [ ] Update living docs and local MODLOG with verified commands/limits, self-review the diff, commit only owned files, and write task-1-report.md with exact tests/exit codes, evidence paths, PID/profile state and concerns. Keep an explicit handoff for task 2; terminate task-owned game processes when done.

### Task 2: Add the MCP adapter and finish integration

**Files:**
- Create: tools/game_runner/mcp_server.py
- Create: tools/game_runner/tests/test_mcp_server.py
- Update: tools/game_runner/{SPEC.md,__main__.py}, tools/game_runner/tests/scenarios.md, README.md, docs/repository.md

**Interfaces:**
- Consumes: GameRunner and local configuration from task 1, including its validated lifecycle/lock.
- Produces: python -m tools.game_runner --config PATH mcp serving local MCP over stdio, tools aspirations_run_scenario, aspirations_observe, aspirations_advance_days. No arbitrary scripts, shell or filesystem tools.

- [ ] Read task 1's accepted contract/report and the current official MCP stdio/protocol specification. Use standard library JSON-RPC with explicit supported protocol negotiation; no SDK installation. Keep the adapter narrow, with implementation limits documented.
- [ ] Write failing real-subprocess tests for initialize, initialized notification, tools/list, each tools/call dispatch using a fake backend, invalid arguments/unknown tools, backend failures, oversized/malformed input, clean EOF and protocol-only stdout.
- [ ] Implement the thin adapter with no gameplay duplication; initialize before tool execution, bounded input and ordinary JSON-RPC/MCP errors. Advertise only accepted task-1 operations and keep mutation single-flight across callers. Diagnostics go to stderr.
- [ ] Run all Python and existing tooling checks. Run a real MCP subprocess client against the live automation-smoke once, checking the returned measured report rather than only mocked dispatch. This verifies the complete agent-to-game path; do not re-run the full triple proof without a change justifying it.
- [ ] Verify dev/release exclusion, preservation of original unfinished-core hashes, exact owned-process shutdown, and restore original launcher No mods selection via supported UI if still selected. Preserve saves and unrelated settings.
- [ ] Document executable CLI/MCP examples with placeholders, configuration schema, supported operations, limitations and evidence. Self-review and commit owned work. Write task-2-report.md with complete verification and cleanup evidence for controller review.

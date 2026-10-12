# CK3 automation acceptance scenarios

Automation-smoke is independent of Aspirations gameplay; core-regression invokes Task 2 native gameplay assertions. Native fixtures are dev-only. A06 exercises the thin MCP adapter over actual subprocess pipes.

| ID | Given / When | Required measured result |
| --- | --- | --- |
| A01 | Explicit disposable baseline, selected dev playset and actual-profile autosave NO_AUTOSAVE; run `python -m tools.game_runner --config PATH run automation-smoke --repeat 3`. | Three owned process launches without navigation; fresh session per repetition; initial counter 0 and identical date; all assertions passed; unchanged baseline hash. |
| A02 | A mutation request is completed and delivered again with the same identity. | Both terminals match exactly; counter changes by 7 once; independent observation remains 7. |
| A03 | Unit tests inject unrelated/stale/malformed/partial UTF-8, duplicate terminals and rotated/truncated logs. | Wrong identities never complete; identical terminal repeats are inert; conflicts and log replacement fail. A large complete daily log batch cannot hide a valid terminal. |
| A04 | Invalid scenarios/days/repeats, missing executable, lost HWND/PID/foreground, concurrent ownership or absent DONE. | Reject before game input; timeout is bounded; ACK alone cannot pass; release only own modifier; stop exact owned process; next operation establishes a fresh session. |
| A05 | Advance one day after native ACK, then reset from baseline. | Delayed native completion measures date +1; next process starts at initial date with a different session. Never infer completion from requested days. |
| A06 | Initialize and notify ready over real subprocess stdin/stdout; list exactly three bounded tools; dispatch all calls with fake runner; send invalid arguments/envelopes and backend failures; close stdin. Run one real MCP automation-smoke call from the disposable baseline. | Protocol-only stdout; no input before ready or on invalid tool arguments; correct JSON-RPC/tool errors; bounded oversized input; EOF closes owned resources. Real returned report contains measured 0→7 once, duplicate identity, date +1 and all eight assertions. |
| A07 | Existing tooling tests and dev/release checks; close the runner. | Release contains no automation files/markers; only owned save/request/lock are removed or restored; no task-owned CK3 process remains. Overall MCP test owner restores the original launcher selection afterward. |
| A08 | Selected dev playset and NO_AUTOSAVE; run `python -m tools.game_runner --config PATH run core-regression --repeat 1` from pristine baseline. Inject wrong and incomplete native terminals in runner tests. | Fresh identity-bound complete C01/C02/C09/C10/C11 measurements and exact assertions; duplicate replay returns the same snapshot. Wrong counts/deltas or native FAIL yield assertion_failed; missing fields/DONE cannot pass. No selector or popup is opened. |

Run unit tests with `python -m unittest discover -s tools/game_runner/tests -v`; existing assembly tests with `pwsh -NoProfile -File tools/tests/run.ps1`. Close CK3 before rebuilding dev output. Preserve `.local/automation/` reports, three fresh log snapshots and one real screenshot. Inspect namespace errors separately from pre-existing core/vanilla issues; a fixture PASS is not gameplay certification.

The first version uses a controlled disposable baseline. It does not inspect or choose generic visible events. `tick_day` is a bounded debug-time operation; successful date advancement does not prove normal simulation would proceed through every popup.

A04 also requires actual-profile/autosave launch preflight: missing, unsafe YEARLY/MONTHLY, duplicate settings, NO_AUTOSAVE in another section/comment, and alternate user-data profile all fail before process launch. Unit tests exercise these without launching the game. The overall test owner restores any temporary NO_AUTOSAVE preference after the owned session closes.



C03 selector clicks, C04 actual save/load and visible UI remain separate native acceptance in [core scenarios](../../../src/core/tests/scenarios.md); they are not inferred from A08.

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

Vengeance registration: `vengeance-regression` invokes shared V01-V06 fixtures. Added standard-library tests cover measured results/replay, incorrect custody prestige despite a PASS flag, hidden origin despite a PASS flag, incomplete telemetry, and native aspiration diagnostics. Native game evidence and mandatory actual GUI execution are recorded separately in the owning family scenarios/report.

Core, vengeance, lifecycle, recovery, bond and integrated runs share the same strict `asp_` runtime diagnostic assertion and numeric count for each fresh log interval. Script system, compiler argument, event-target, DataFactory and no-valid-options errors fail despite complete PASS measurements; lifecycle examines both logic and calendar intervals. Tests inject these formats at the existing fake native boundary. Startup unused-state/orphan-event notices and bounded Trigger Localization notices remain separately classified. Historical native reports are not rewritten by this runner correction.

## Registered lifecycle-regression

The bounded `lifecycle-regression` scenario runs shared P01-P06 effects with complete integer telemetry, independently checks costs/counts/absence and UI-replay memory postconditions, and verifies exact cached replay. It snapshots that logic interval, restarts from the same unchanged baseline, prepares shared near-boundary calendar state, verifies its exact saved-state precondition, advances one real native day, and checks review/declaration/expiry measurements plus replay. Separate fresh sessions prevent intentional logic-fixture deaths and delayed native grief from contaminating the calendar test. The precondition is not actual save/load; native Save Game/load and UI/player-switch/succession procedures remain mandatory in core scenarios.

Reports retain both logic and calendar logs, request/session identities, baseline hash, raw deltas and an aspiration parser/runtime diagnostic count. Any such diagnostic in either interval fails the scenario, while known static unused-state and unrelated vanilla frames are classified separately. All operations remain private scenario implementation; there is no arbitrary script API or new framework. CLI and MCP expose only the registered scenario name and existing bounded repeat/day parameters.

Withdrawal tooltip regression: registered P03 covers the four literal settlement outcomes and repeated withdrawal. Mandatory native UI replay uses `.50`/`.51`/`.52`, hovers declared Withdraw, and requires a fresh error-log interval without aspiration tooltip errors; a screenshot alone is insufficient.


Recovery registration: `recovery-regression` invokes shared H01–H05, including the native child-on_action slot0 reservation regression. Transport tests reject missing fields, conflicts, wrong identity and incorrect measured payout/penalty despite native PASS flags; they require exact cached replay. Native assertions compare nominal costs with independent modified Stress controls and exclude foreign/unproven/cancelled/replayed work. Real GUI payer/payment/completion, modifier duration and stale modal hover/dismissal remain separate mandatory procedures in the recovery scenarios.

## Registered bond-regression

The registered `bond-regression` CLI/MCP operation runs shared native B01–B07. All86 numeric fields in BOND_FIELDS are mandatory. The runner independently checks case flags, native locked/unlocked/romance controls, exact Stress/XP/memories/replay, target invalidation, chance values20/12/6/2/2/0, cooldown360, consumed/fresh contexts, Content/Lustful, all four relation modes, independent early-cost control, cap/cooldown/no-pledge, review/suspension and actual bounded routine-selector behavior. Missing/malformed/conflicting telemetry is transport failure; wrong values/native diagnostic yield assertion_failed. Duplicate identity replays cached measurements without executing fixtures again. Each repetition starts from the same pristine disposable baseline, preserving numeric date and hash.

No arbitrary script API, dependency or framework is added. Test contacts/perks/relations/date stamps are controlled setup; this registered scenario does not certify an actual relationship action, elapsed year, player switch or save/load. The family [scenarios](../../../src/stories/personal_bond/tests/scenarios.md) require actual native Befriend input followed by disclosed native progress acceleration, exact target relationship/slot/memory and measured outcome. Main source manifests and final fresh diagnostic classification belong to ignored task evidence.

Successful reinterpretation is shared registered B07 coverage: friendship→romance before review and romance→friendship at due review. Both supported pursuits and absent desired relationships qualify on the exact adult court contact. Each direction exposes observed before/after mode, same Story/target, instance/allocation/origin/context signature/incident/serial/consumed/cooldown deltas, active desires, Stress/XP/memory deltas and next-review/notified state. Required changes are1→2 and2→1; all identity/consumption/resource deltas are0 and active desires remain1. Non-due review stays720 days; due reinterpretation clears the reminder latch and schedules360 days while preserving origin. The existing achieved-Friend rejection remains. Date/perk/contact setup is artificial; this does not claim actual UI reinterpretation or elapsed review time. Original `origin_preserved` remains the retention-only field; reinterpretation has its own independent measurements.

Combined `integrated-regression` requires all21 identity-bound measurements and cached replay; transport tests mutate every field, omit identity and inject a native DataFactory error. Core actual I02 procedures retain their separate mandatory input/evidence boundary.


## Managed lifecycle acceptance

| ID | Given / When | Required measured result |
| --- | --- | --- |
| A09 | Explicit baseline/config, closed CK3/launcher and current dev manifest; execute `session core-regression --repeat 1 --deadline 240`. | One command prepares only targeted preferences/selection and a unique descriptor, runs registered native assertions, retains fresh PNG/log/request evidence plus JSON/Markdown provenance, stops its Job and restores owned targets; immutable baseline hash and no temporary save/request/descriptor/lock remain. |
| A10 | Inject malformed profile, partial preparation/copy, startup/worker error, assertion failure or worker deadline. | Explicit failure with generated report; successfully applied owned changes restored, exact child/descendant processes stopped, unrelated process/saves/files preserved. Process-exit failure retains profile/backups/lock for recovery. |
| A11 | Another writer changes an owned preference, selection, staged save, dedicated request or temporary descriptor. | Concurrent target content retained and a cleanup conflict reported; unaffected owned targets restored; no false success. Unrelated fields are preserved while owned values restore. |
| A12 | Missing/stale PNG/log/request/report evidence, incomplete repeats, source/build drift or unmapped output. | Managed session fails even if the native result says passed. The existing generated dev descriptor mapping remains valid. |

Offline `test_session.py` uses real temporary files and real bounded subprocesses for Job ownership/deadline checks, including one unrelated process that must survive. Injected native boundaries verify parent lifecycle failures without claiming game semantics. Live A09 evidence remains ignored; inspect actual screenshot and measured C01/C02/C09/C10/C11 fields before acceptance.

## A10: Registered ui-regression

Use the managed command in [SPEC](../SPEC.md#registered-ui-regression) with the supported native geometry/profile. Shared dev setup and postconditions are in [core scenarios](../../../src/core/tests/scenarios.md#registered-exact-story-ui-and-persistence-sequence). The sequence includes exact second-Story input/declaration, native Save Game, a fresh process loading the actual file, exact target/ID/origin/review/deadline persistence, and both native log intervals. Mandatory ordered frames are open-aspirations, select-story, declare-confirmation, declare-result, save-menu, save-dialog, save-name, save-result, reload-selector and reload-story. A label or click never proves the pictured state: inspect actual frames and require numeric native identity checks.

Focused tests cover125% virtualized and aware conversion, changed geometry, foreground-loss release, wrong/stale/cancelled selection, malformed/missing measurements, missing/stale/invalid frames, bounded stable save bytes, exact reload state, saved-byte/log provenance, and partial/external/unowned save cleanup. Offline boundaries simulate Windows/CK3 only; they do not certify native rendering. The parent managed report requires actual fresh artifacts and restoration.

The CK3 1.20.1 measured run completed all ten assertions after selecting and declaring only the second vengeance Story, saving through the native dialog, and reloading the same state in a new process. Both log intervals must remain free of aspiration runtime errors. This is also a regression for family dispatch during vengeance management tooltip construction: a recovery landed-Title predicate reached through an ordinary `OR` emitted `holder` type and null county-control errors even though the vengeance state checks passed. The registered diagnostic gate caught that path; the explicit family-limited branches passed the same native sequence with zero such errors.

# Aspirations

An English-only, player-character CK3 prototype for contextual vengeance, holding recovery and personal bonds. [Design](docs/design.md) · [Core specification](src/core/SPEC.md) · [Repository contract](docs/repository.md) · [Engine findings](docs/modding-notes.md)

Current status: native core lifecycle/pledges, vengeance, holding recovery and personal bonds with registered disposable regression scenarios on CK3 1.20.0.4. Recovery acceptance includes actual GUI-funded construction, completion and its three-year county modifier. Personal-bond acceptance includes actual native Befriend input/outcome with disclosed existing-scheme progress acceleration. See the [automation contract](tools/game_runner/SPEC.md) and [acceptance scenarios](tools/game_runner/tests/scenarios.md).

Use installed PowerShell 7 and Git. Packaging and tooling tests need no additional dependencies; optional engine-aware validation uses the pinned xTiger CLI. The installed game is a read-only scripting reference; author native files under `src/core/game/` or the owning `src/stories/<family>/game/` when implementing a family.

```powershell
pwsh -NoProfile -File tools/tests/run.ps1
pwsh -NoProfile -File tools/build.ps1 -Profile dev
pwsh -NoProfile -File tools/check.ps1 -Profile dev
pwsh -NoProfile -File tools/build.ps1 -Profile release
pwsh -NoProfile -File tools/check.ps1 -Profile release
pwsh -NoProfile -File tools/package.ps1
```

Commands default to the repository containing the scripts, independently of caller directory. Add `-RepositoryRoot <directory>` for controlled disposable fixtures. Generated profiles are `.build/dev/mod/` and `.build/release/mod/`; manifests, `.local/` and `dist/` are ignored. Close CK3 before replacing dev output.

Resolve actual Documents using `[Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)`. Select the existing CK3 user-data folder, including redirected Documents or launcher-specific configuration. Then explicitly register development output:

```powershell
pwsh -NoProfile -File tools/install-dev.ps1 -UserDataPath '<selected CK3 user-data directory>'
```

Registration writes `mod/aspirations_dev.mod` with the title Aspirations (Development), preserves unrelated files and leaves playset selection to the user. No real-user-data installation occurs in the tooling tests. See [manual installation](packaging/INSTALL.md), [credits and licensing boundary](packaging/CREDITS.md), and [reviewed implementation plan](docs/superpowers/plans/2026-10-12-ck3-aspirations.md).

Native fixture files under module `tests/game/` are dev-only. Release excludes them. Static validation checks assembly, encoding, links, metadata and identifiable duplicate IDs; CK3 runtime scenarios remain the authority for behavior. Source scripts/localization never come from generated output, and extracted game assets are never committed.

Add engine-aware static validation with [xTiger](docs/quality.md). Install once, then
check each assembled profile against the installed vanilla game:

```powershell
pwsh -NoProfile -File tools/setup-xtiger.ps1
pwsh -NoProfile -File tools/check-xtiger.ps1 -Profile dev -GamePath '<CK3 installation root>'
pwsh -NoProfile -File tools/check-xtiger.ps1 -Profile release -GamePath '<CK3 installation root>'
```

Error/Fatal diagnostics fail the command; add `-FailOnWarning` for strict warning
policy. Existing checks run automatically as preflight. Reports and the hash-verified
validator stay under `.local/`. See [coverage overlap and limits](docs/quality.md#coverage-overlap).

For bounded real-game smoke tests, use the existing Python runtime with standard-library modules only. Put explicit machine configuration and a disposable baseline under `.local/automation/`, select the dev playset, select No Autosave (`NO_AUTOSAVE`) in CK3 settings for the disposable session, and close other CK3 sessions:

```powershell
python -m unittest discover -s tools/game_runner/tests -v
python -m tools.game_runner --config .local/automation/config.json run automation-smoke --repeat 3
python -m tools.game_runner --config .local/automation/config.json run core-regression --repeat 1
python -m tools.game_runner --config .local/automation/config.json run recovery-regression --repeat 1
python -m tools.game_runner --config .local/automation/config.json run bond-regression --repeat 1
python -m tools.game_runner --config .local/automation/config.json run integrated-regression --repeat 1
```

Registered scenario commands restart only their own game from the same baseline, check native measured state and duplicate delivery, record JSON/log evidence, and clean up the owned session. Automation-smoke and lifecycle-regression advance one actual day. `observe` and `advance-days 1` are also supported. Configuration, bounds and failure behavior are documented in the [automation contract](tools/game_runner/SPEC.md). No game-install edits or additional packages are needed.

The launch preflight requires the actual Windows Documents CK3 profile and its exact `game.autosave` preference `NO_AUTOSAVE`, preserving existing autosaves across date advancement. Alternate profiles and missing/ambiguous settings are rejected. The existing `run`, `observe`, `advance-days` and MCP operations read the preference; restore any manually changed test preference after cleanup.

For a complete managed regression, build/check dev output, close CK3 and its launcher, and use:

```powershell
python -m tools.game_runner --config .local/automation/config.json session core-regression --repeat 1 --deadline 240
python -m tools.game_runner --config .local/automation/config.json session ui-regression --repeat 1 --deadline 240
```

This additive command prepares/restores only the autosave preference and enabled-mod selection, uses a unique temporary descriptor/save, and stops its exact owned worker/game Job on failure or deadline. It retains generated `report.json` and `report.md` with build provenance, measured assertions, required fresh screenshot/log evidence and restoration results under configured `.local/` output. Changed external targets are retained as explicit failures. Repeat is 1–10 and deadline is 1–900 seconds; existing commands/MCP remain available. See the [managed lifecycle contract](tools/game_runner/SPEC.md#managed-session-lifecycle).

The managed `ui-regression` additionally selects the exact second native Story, declares its eligible ambition, saves through native Save Game and reloads that actual campaign with exact persistence assertions and ordered screenshots. This UI sequence was measured on CK3 1.20.1 at a 2560x1440 client, GUI scale1.3 and local saves; other layouts fail clearly. Bare `run` and MCP calls reject this managed-only sequence. See [UI operations and evidence](tools/game_runner/SPEC.md#registered-ui-regression).

For a local MCP client, start `python -m tools.game_runner --config '<absolute configuration JSON path>' mcp` from the repository directory. It supports MCP 2025-11-25 initialization, a fixed three-tool list and calls to `aspirations_run_scenario`, `aspirations_observe` and `aspirations_advance_days`. Calls share the same bounded runner and ownership lock; close client stdin to stop the owned game and restore temporary runner files. No global MCP registration or SDK is needed. See the [stdio examples and implementation limits](tools/game_runner/SPEC.md#mcp-stdio-interface), including serial dispatch without progress or interruptible cancellation.

## Prototype coverage and limits

Tested game version: CK3 1.20.0.4 Crozier. The supported prototype is single player with an adult landed current ruler, English localization and ordinary native UI. Registered combined regression covers mixed three-ambition/five-desire capacity, exact selected-instance rewards, unlike family target types and suspended public settlement. Separate actual acceptance covers all-family save/reload, player switching, absence closure, native title transfer, owner death/succession and the mixed selector. A fresh release-only campaign was observed from 1 October 1178 to 19 September 1182 with ordinary AI and randomness: natural bond offers, a battle-death vengeance origin and scheduled reviews appeared. This one-character sample does not establish offer frequency or balance. Source assembly checks alone do not certify those behaviors.

Construction/action acceptance includes disclosed setup and acceleration: the recovery test prepared Control80 and accelerated already paid native construction; the bond test accelerated an already started Befriend scheme. Ordinary construction or scheme duration is not certified. Recovery supports only the explicit Markets/Palisades1–2 and Pastures/Cereal Fields/Hill Farms1 pool. Direct public murder exposure before known-secret observation can be missed. Landless/government expansion, multiplayer, external-mod/RICE compatibility and additional pursuit routes remain outside verified coverage.

Manual deliverable: `dist/aspirations-0.1.0.zip`. Upload source for any future Workshop publication: `.build/release/mod/` itself. No push, PR, Workshop upload or subscribed-download acceptance has occurred. The public license is undecided; see the packaged credits and installation instructions before public distribution.

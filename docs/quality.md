# Quality checks and xTiger

The project uses complementary assembly, source-contract, engine-aware static and
native gameplay checks. [The repository contract](repository.md) owns this integration;
[tooling scenarios](../tools/tests/scenarios.md) document its regression boundaries.

## Install and run

The optional validator is [9mirx0r/xTiger](https://github.com/9mirx0r/xTiger), not
upstream amtep/tiger. The pinned [v1.5.9-alpha release](https://github.com/9mirx0r/xTiger/releases/tag/v1.5.9-alpha)
targets CK3 1.20.0.4. Its executable is still named `ck3-tiger.exe`.
PowerShell and .NET remain sufficient for ordinary packaging and tooling tests.

```powershell
pwsh -NoProfile -File tools/setup-xtiger.ps1
pwsh -NoProfile -File tools/build.ps1 -Profile dev
pwsh -NoProfile -File tools/check-xtiger.ps1 -Profile dev -GamePath '<CK3 installation root>'
pwsh -NoProfile -File tools/build.ps1 -Profile release
pwsh -NoProfile -File tools/check-xtiger.ps1 -Profile release -GamePath '<CK3 installation root>'
```

Close CK3 before rebuilding dev. `-GamePath` is the installation root containing
`game/` and `launcher/`, not `game/` itself. Installation verifies the Windows ZIP's
SHA-256 from [the tracked pin](../tools/xtiger/release.json) and extracts only
`ck3-tiger.exe` under `.local/tools/xtiger/<version>/bin/`. For offline installation,
pass `-ArchivePath '<downloaded pinned ZIP>'`; the same hash and pinned archive entry
are required. An existing
validator can be selected with `-TigerPath`, but its version must match the pin.
Updating the pin requires reviewing the upstream release and new asset digest together.
No update subcommand is run automatically.

`check-xtiger.ps1` runs existing `check.ps1` before and after validation. Stale source,
output, manifest, executable or config changes during analysis fail. The validator receives the exact assembled profile's
`descriptor.mod`, installed vanilla files and the explicit
[English-only config](../tools/xtiger/ck3-tiger.conf). Vanilla and other-mod diagnostics
are hidden, while vanilla definitions remain available for resolving references.
There are no report suppressions, baselines or broad scope overrides.

Each run retains raw `reports.json`, separate `stderr.txt`, and `summary.json` under
`.local/xtiger/<profile>/<run-id>/`. The summary records validator/config hashes,
validator and installed game versions, profile, manifest hash, counts and policy.
Native execution errors and malformed reports fail closed and may have only raw
evidence. Successful transport does not mean a clean mod: xTiger can exit 0 with
diagnostics. Error and Fatal reports return command exit 1; Warning reports also fail
with `-FailOnWarning`. Tips and Untidy remain informational. The default timeout is
300 seconds; use `-TimeoutSeconds 1..900` if needed. A timeout stops only the owned
validator process tree.

The app, MCP server and game-launching features are separate xTiger capabilities.
This integration uses its CLI validator. It requires no launcher registration,
playset changes or user-profile mutation and adds nothing to shipped mod content.

## Coverage overlap

| Area | Existing checks | xTiger | Decision |
| --- | --- | --- | --- |
| Script syntax | Focused brace balance and top-level `asp_` definition scan in `Test-NativeContent` | Full Paradox parser and category-specific field validation | Partial overlap; keep fast project checks and add deeper parsing |
| Encoding/localization shape | English-only path/header/BOM, corrupted BOM and duplicate owned keys; targeted Python localization regressions | Localization parser, encoding and key checks | Partial overlap; project language and exact byte requirements remain independent |
| Identifiers/references | Duplicate owned definitions; narrow `ScriptValue` reference regression | Item databases, missing references and localization, effects/triggers, scope consistency | xTiger adds broad engine-aware coverage; retain the project's stricter duplicate policy |
| Visible Story cards | `check-contracts.ps1` explicitly requires title, implicit `_desc` and visualization body; targeted branch/getter regressions | Static localization and data-function checks | Partial overlap; retain implicit/native Story requirements and branch regressions |
| Bundle/metadata | Allowed source modules/categories, collisions, deterministic manifests/hashes, stale files, exact descriptor policy, dev exclusion and safe ZIP/registration | Some descriptor/packaging diagnostics | Limited overlap; xTiger does not enforce our repository/distribution contract |
| Documentation/evidence | Living SPEC/scenario links, six acceptance categories, registry membership, portable knowledge references | No project acceptance contract | Keep K01-K17 and source-contract checker |
| Runner infrastructure | Python transport, ownership, profile/timeout/restoration, protocol and UI geometry tests | Separate MCP/game-runner implementation exists | Keep our tested runner; its measured-state contract is project-specific |
| Gameplay/UI | Registered native assertions, exact deltas, stale actions, dates, save/load, actual input and screenshots | Static analysis cannot establish these outcomes | Keep all gameplay and native rendering acceptance |

No existing test or validation is removed. Overlap is principally cheap syntax and
localization safeguards with stricter project rules. A general lint pass cannot
replace regressions for previously observed native behavior. A future removal should
identify the exact rule, prove equivalent positive/negative controls in the pinned
validator and preserve any project-specific acceptance requirement.

Known interpretation boundaries for shared `asp_target` type inference and script
BOM warnings are recorded in [the static-validation knowledge note](knowledge/static-validation.md).

## Interpretation limits

xTiger is an alpha and its authors document incomplete validation for some CK3 1.20
features. Review each diagnostic against native sources and measured evidence.
Do not modify gameplay or silence a diagnostic merely to obtain a green static run.
Keep the installed-version warning in `stderr.txt`; a patch newer than the validator's
target is not a claim of complete compatibility. A clean report does not establish
runtime scope validity, later-frame tooltip safety, natural event frequency or balance.

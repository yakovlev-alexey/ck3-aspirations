# Aspirations contributor instructions

Read `docs/design.md`, `docs/repository.md`, `src/core/SPEC.md` and the affected family's `SPEC.md` before editing. Update the owning living contract and `tests/scenarios.md` in the same gameplay change. Historical review indexes and execution plans are not competing contracts.

Use English for all authored prose, identifiers, comments, tool output, metadata and localization. Only `localization/english/*_l_english.yml` is supported; preserve its UTF-8 BOM and native header. Do not use generic YAML formatters on CK3 localization. PowerShell/Markdown use UTF-8 and LF. No formatter is configured; use syntax checks and inspect diffs.

Author ordinary CK3 files in story-owned `game/` folders. Core owns lifecycle and cross-story coordination; stories cannot mutate each other's private state. No transpiler, runtime framework, dependency additions, custom GUI replacements or undocumented identifier changes. Create only categories that are used. Reserve stable event IDs in the owning SPEC before implementation and never repurpose saved IDs.

Use installed PowerShell 7, .NET and Git. Prefer `rg`. Preserve existing user edits; no push, PR, publication, game-install modification, Workshop-source modification or active-playset mutation without explicit authorization. Never redistribute extracted game/Workshop assets or commit secrets, saves, profiles, screenshots, runtime logs, local paths, `.build/`, `.local/`, `dist/` or `.superpowers/`.

Test tooling changes first with `pwsh -NoProfile -File tools/tests/run.ps1`, then dev/release build/check commands. No additional test framework is needed. Static checks cannot establish game semantics. Gameplay requires disposable campaign scenarios, measured deltas, fresh logs and screenshots; report unverified cases honestly. Inspect knowledge, construction attribution, calendar and event-story scope probes before relying on those capabilities.

Close the test CK3 process before rebuilding dev output. Resolve user data from actual OS Documents configuration and require the explicit user-data path for registration. Keep machine setup and transient findings in `.local/MODLOG.md`; transfer validated versioned discoveries into `docs/modding-notes.md`.

Commit only authored changes with short imperative English messages. No public license has been selected; document licensing before public release.

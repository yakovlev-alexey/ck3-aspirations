# Aspirations

An English-only, player-character CK3 prototype for contextual vengeance, holding recovery and personal bonds. [Design](docs/design.md) · [Core specification](src/core/SPEC.md) · [Repository contract](docs/repository.md) · [Engine findings](docs/modding-notes.md)

Current status: repository bootstrap and deterministic packaging tools. No gameplay scripts exist yet. A successful descriptor-only build is packaging evidence and cannot be played.

Use installed PowerShell 7 and Git. No additional dependencies are needed. The installed game is a read-only scripting reference; author native files under `src/core/game/` or the owning `src/stories/<family>/game/` when implementing a family.

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

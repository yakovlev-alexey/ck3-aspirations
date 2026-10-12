# Repository and packaging contract

Status: authoritative living contract migrated from the approved 2026-10-12 design. [Product design](design.md) and [core](../src/core/SPEC.md) own gameplay.

### Repository and installation locations

Keep one independent Git repository named `ck3-aspirations` in a development workspace outside the Steam installation, Workshop download directory, and CK3 user-data directory. Its absolute checkout path is a local setup choice and must not be embedded in source files. The installed game is a read-only reference for development. The repository owns all authored mod scripts, documentation, localization, original assets, packaging tools, and reproducible test scenarios.

The approved specification has been migrated from the chat artifact workspace into `docs/design.md`, this repository contract, `src/core/SPEC.md` and the three family contracts. The dated review document is now a historical index; the original artifact is a review record. Update the owning living contract rather than recreating a second editable copy.

Development output lives under `.build/dev/mod/`; release output lives under `.build/release/mod/`. A generated local `.mod` launcher descriptor can point to the development output through an absolute `path`. Only the local descriptor needs to be registered in the resolved CK3 user-data `mod` directory. Resolve that directory from the user's actual Documents configuration rather than assuming a fixed drive or ignoring redirected Documents folders. Keep the generated descriptor and local paths out of Git. Updating a playset and launching a test campaign are separate actions from assembling files.

### Alternatives and selected organization

| Organization | Benefit | Cost |
| --- | --- | --- |
| Native CK3 directories at repository root, with a central story documentation directory | Direct loading and minimal tooling | One story's implementation is spread across many unrelated directory branches |
| One source folder per story, each containing native CK3 directories | Story logic, prose, localization, and acceptance scenarios stay together | Requires a small file-assembly step |
| A custom story format that generates CK3 scripts | Could enforce a narrow content schema | Requires a new language or compiler and makes native debugging harder |

Select the second organization. Author ordinary CK3 scripts directly; the assembly step only copies files into the loader's native directory structure. It performs no script translation, macro expansion, or concatenation. This is the approved organization for the new repository, not a migration of the game's own layout.

### Source tree

```text
ck3-aspirations/
  README.md                         # Setup, commands, and links to current specifications
  AGENTS.md                         # Project workflow and source/generated-file boundaries
  .editorconfig
  .gitattributes
  .gitignore
  docs/
    design.md                       # Purpose, glossary, shared player-facing behavior
    repository.md                   # This repository and packaging contract
    modding-notes.md                 # Durable CK3 findings and compatibility notes
    decisions/                      # Significant architectural decisions, when needed
    superpowers/
      specs/                        # Historical review records or proposals with status
      plans/                        # Execution plans; not the current gameplay contract
  src/
    core/
      SPEC.md                       # Shared lifecycle, capacity, public commitments
      game/
        common/
          on_action/asp_core.txt
          scripted_effects/asp_core.txt
          scripted_triggers/asp_core.txt
          script_values/asp_core.txt
          decisions/asp_core.txt
        events/asp_core_events.txt
        localization/
          english/asp_core_l_english.yml
      tests/
        scenarios.md
        game/                       # Native CK3 debug fixtures, development profile only
    stories/
      vengeance/
        SPEC.md                     # Living specification for this story family
        game/
          common/
            story_cycles/asp_vengeance.txt
            on_action/asp_vengeance.txt
            scripted_triggers/asp_vengeance.txt
            scripted_effects/asp_vengeance.txt
            script_values/asp_vengeance.txt
            character_memory_types/asp_vengeance.txt
          events/asp_vengeance_events.txt
          localization/
            english/asp_vengeance_l_english.yml
        tests/
          scenarios.md
          game/events/asp_vengeance_debug_events.txt
      holding_recovery/
        SPEC.md
        game/                       # Same native-directory convention; only needed files
        tests/
      personal_bond/
        SPEC.md
        game/
        tests/
  packaging/
    descriptor.mod                  # Portable release metadata; no machine-specific path
    CREDITS.md                      # Asset origins and attribution
  tools/
    build.ps1                       # Deterministic assembly, dev and release profiles
    check.ps1                       # Source and output checks
    install-dev.ps1                 # Local descriptor registration; no playset edits
    package.ps1                     # Release archive from release output
    tests/                          # Focused tests of assembly and path handling
  .build/                           # Generated output and file maps; ignored
  .local/                           # Local paths, MODLOG.md, logs and screenshots; ignored
  dist/                             # Generated release archives; ignored
```

The tree describes ownership, not mandatory empty files. Create a script category only when a module uses it. Story-owned runtime artwork belongs under that story's `game/gfx/`; editable artwork sources and license information belong next to it under the story's `art/`. Shared artwork uses the same convention under `src/core/`. Do not commit extracted vanilla assets. Avoid dependencies for the initial assembly tools: use the PowerShell and .NET facilities already available on the development machine.

### Assembly and packaging contract

Assemble `src/core/game/` and each `src/stories/*/game/` into the selected output's root, preserving paths relative to each `game/` directory. For example, `src/stories/vengeance/game/common/story_cycles/asp_vengeance.txt` becomes `common/story_cycles/asp_vengeance.txt` inside the mod. The development profile additionally assembles each module's `tests/game/`; the release profile excludes all such fixtures and debug entry points.

Use the portable descriptor from `packaging/` at the output root, with the explicit development-profile metadata adjustments described below. Preserve authored game-content file bytes, including localization encoding. Verify the `_l_english.yml` naming convention, the `l_english:` language header, and the game's required encoding during content validation; do not run these files through a generic YAML reformatter. Source formatting must preserve CK3's script and localization conventions. Both development and release bundles include English localization only.

Two modules producing the same destination path are a build error, including case-only collisions. There is no last-file-wins override order. Different files appending child on-actions to a shared native hook are allowed where CK3 supports that pattern. Keep `asp_` identifiers globally unique, with family-specific prefixes such as `asp_vengeance_`; event namespaces and IDs are stable save-facing identifiers. A display-name change must not rename persisted identifiers.

Assembly is deterministic and emits an ignored file map containing source-relative path, destination-relative path, and content hash. This map helps trace a game-log filename to its authoring module. Write into a fresh staging directory, validate it, then replace only the selected generated output after validating its resolved absolute path lies inside this repository's `.build/`. Do not delete or mirror over the game, Workshop, or user-data roots. Files removed from source must disappear from the next output. Do not assemble or replace development output while the test game is running; close that test process before updating it.

Source scripts and localization are edited only under `src/`. Generated output is disposable and never edited by hand. `SPEC.md`, authoring assets, local logs, saves, paths, screenshots, tests, and implementation plans do not enter release game content. Release archives contain the release mod output plus concise install instructions and credits. Choose and document licensing before any public release; this design does not assume a license for the user's work.

### Steam Workshop distribution

Steam Workshop is a supported distribution target for Aspirations. Upload the contents of `.build/release/mod/`: `descriptor.mod`, `common/`, `events/`, `localization/`, and any authored runtime asset directories appear directly at the uploaded content root. The uploader must not receive the repository root or a containing directory that adds another `mod/` layer. The installed RICE Workshop package follows this native structure. Steamworks treats a Workshop item's content as a folder of files; its upload API takes that content folder, independently of the author's repository organization ([Steamworks implementation guide](https://partner.steamgames.com/doc/features/workshop/implementation)).

Prepare a separate local release descriptor pointing to the release output for registration and upload through the CK3 launcher. Package preparation and upload remain separate operations. Subscribers receive the ready-to-load CK3 files and require no PowerShell, Git, source tree, or assembly step. Manual-distribution archives are another output from the same release bundle, not an extra runtime dependency.

After a successful first publication, preserve the actual `remote_file_id` in `packaging/descriptor.mod` so subsequent release builds retain the existing Workshop identity. This public item ID is versioned release metadata, not a credential or disposable launcher state. Do not invent it before publication or copy another mod's ID. Development descriptors use a distinct display name and omit the release Workshop ID. Machine-specific `path` values remain confined to generated local descriptors. Release validation checks the root layout, descriptor metadata, absence of local paths and debug fixtures, and presence of any referenced preview image. Verify a subscribed download in the game when testing the publication workflow; source inspection alone is not evidence of a completed upload.

### Living specifications and ownership

`docs/design.md` explains why the system exists and indexes its modules. `src/core/SPEC.md` is the authoritative behavioral contract for shared emergence, capacity, lifecycle, review, declaration, and cleanup. Each story's `SPEC.md` is the authoritative contract for that story's unique behavior. Story specifications link to shared rules and describe explicit differences instead of repeating the entire lifecycle. `docs/repository.md` owns directory and packaging rules. Historical proposals and plans clearly link to the current contracts and do not compete with them.

A story family is the smallest module for the prototype. Vengeance interpretations live together while they share the same cause, state, and lifecycle. A substantially different independent story gets its own folder and specification rather than expanding a central event file indefinitely. Story code can call the core's documented effects and triggers; one story does not directly read or mutate another story's private state. Cross-story coordination belongs to core only when an actual shared requirement exists.

Every living story specification contains:

1. **Intent and scope:** the personal experience it should produce, stable story ID, category, supported characters, and exclusions.
2. **Origin and knowledge:** causes, target eligibility, what the owner knows, selection weights, and duplicate suppression.
3. **Interpretations and player choices:** available meanings, personality effects, explicit costs, and supported paths to satisfaction.
4. **State and ownership:** saved targets, variables, timestamps, parameters, namespace, and the core lifecycle operations it uses.
5. **Transitions:** exact fulfillment, review, abandonment, impossible-goal, owner-death, and player-switch behavior, including precedence when several conditions occur together.
6. **Consequences:** rewards, penalties, public recognition, public-declaration eligibility, and safeguards against repeated payouts.
7. **Presentation:** origin and outcome event requirements, interface conditions, localization keys or file links, and any original art.
8. **Acceptance scenarios:** stable scenario IDs with Given/When/Then outcomes and links to the runnable debug fixture or documented in-game procedure.
9. **Compatibility:** required game surfaces, tested game versions, DLC-dependent branches, and any migration needed for persisted state.

Document concrete story parameters next to their implementing values; link shared parameters to core rather than maintaining conflicting copies. A behavior change updates the owning `SPEC.md`, affected localization, and acceptance scenarios in the same change as its scripts. If the implementation and specification disagree, identify whether the change is a bug fix or an intentional design change and reconcile both before calling it complete. Specifications remain current prose contracts; the build does not pretend to prove every narrative rule automatically.

Keep durable discoveries in `docs/modding-notes.md` with game version and source references. Use `.local/MODLOG.md` for machine-specific paths, backup locations, current test attempts, and transient findings. Transfer reusable findings into the durable notes after validation; never commit saves, user profiles, launcher state, or raw runtime logs.

### Repository checks

Require a `SPEC.md` for every story source directory and keep its acceptance scenario links valid. Static checks cover destination collisions, unexpected package files, missing required documentation, localization naming and encoding, and identifiable duplicate mod-owned IDs. CK3 remains the authority for script semantics; these checks are not a replacement for loading and exercising the mod.

Give the assembly tools focused tests for identical relative paths, case-only collisions, preservation of relative directories and file bytes, removal of stale output, dev-only fixture exclusion, and containment of output replacement. Reuse those checks for local development and any future CI; do not introduce a new test framework solely for the initial file-copy tool. Story scenarios stay with their story; only cross-story lifecycle scenarios live under `src/core/tests/`.

Review changes by story ownership: a gameplay diff should normally contain the story's scripts, its live specification, its localization, and the directly affected scenarios. Keep generated packages and test recordings out of source-control diffs. The implementation plan will identify documentation migration and repository setup as its initial steps, followed by the exact source files to create for the first playable story. The first repository commit will contain the migrated current specifications and repository setup.

## Commands and failure boundaries

For these packaging commands, PowerShell 7 and Git already installed on the host are sufficient. No package manager, Pester, Python, runtime framework or third-party dependency is required. Run from any caller directory: each command defaults `RepositoryRoot` to its script's parent. An explicit `-RepositoryRoot` is available for disposable tooling fixtures.

```powershell
pwsh -NoProfile -File tools/tests/run.ps1
pwsh -NoProfile -File tools/build.ps1 -Profile dev
pwsh -NoProfile -File tools/check.ps1 -Profile dev
pwsh -NoProfile -File tools/build.ps1 -Profile release
pwsh -NoProfile -File tools/check.ps1 -Profile release
pwsh -NoProfile -File tools/package.ps1
```

Commands exit 0 on success and nonzero on validation failure. Build prints the verified mod root and `.build/<profile>/manifest.json`; each sorted entry contains repository-relative `Source`, mod-relative `Destination`, and lowercase SHA-256 `Hash` of output bytes. The dev descriptor is the only intentional byte transformation. No machine paths or timestamps appear in manifests.

Approved modules are core and the three named story families. Source traversal never follows reparse points. Native runtime roots currently supported are `common/`, `events/`, `localization/` and `gfx/`; root descriptor and any declared relative preview image are packaging metadata. Add another native category only when the owning module needs it and extend validation/tests explicitly. Documents, tools, local state, saves and archives are not native content.

Build rejects exact/case-only destination collisions before staging, creates fresh `.build/.stage-*`, copies file bytes, validates staged content and then replaces only `.build/<profile>/mod/` and its owned manifest. Old output is moved aside for rollback and stale files disappear; unrelated profile siblings remain. Existing ancestor/source/output reparse points are rejected before replacement. Failed staging leaves previous good output intact. Close CK3 before dev builds; the tool conservatively rejects dev replacement while any `ck3` process exists. Concurrent builds of the same repository/profile are unsupported; this is not a hostile-filesystem or concurrent symlink-race defense.

Checks verify current source versus ordered manifest/output hashes, required docs and relative links, English localization filename/header/strict UTF-8 BOM, descriptor metadata, package layout and identifiable top-level mod-owned assignment/localization IDs. Repeated additive vanilla hooks and nested effect invocations are not duplicate definitions. These are static heuristics, not an engine parser; they do not prove story semantics, scopes, knowledge, payer attribution, date comparisons, UI rendering or the approved narrative rules. A Workshop ID's authenticity cannot be established locally; obvious placeholders are rejected and the publisher must supply the actual item ID after publication.

`package.ps1` always rebuilds/checks release and writes `dist/aspirations-<version>.zip` with `mod/`, `INSTALL.md`, `CREDITS.md`, sorted entries and fixed ZIP timestamps. Repeated identical source produces identical archive bytes on the same PowerShell/.NET runtime. Compression byte identity across different .NET versions is not promised. The archive is not published by this command.

`install-dev.ps1 -UserDataPath <existing CK3 user-data directory>` rebuilds/checks dev and writes only `mod/aspirations_dev.mod` there, adding the absolute output path and distinct title without `remote_file_id`. It preserves other descriptors and does not change launcher databases or playsets. Tests register only in ignored disposable directories.

## Bootstrap milestone

The initial repository-bootstrap task supplied contracts and tested packaging commands with descriptor-only output. That milestone established packaging, not gameplay. Subsequent native implementation requires its own observed scenarios; runnable automation fixtures and their ownership are documented below.

## Local game automation

`tools/game_runner/` owns the Python standard-library CLI, local MCP stdio adapter, wire/parser, Windows input adapter and its living specification. `tools/game_runner/tests/` owns automation acceptance and deterministic failure-boundary tests. Native bridge files remain in `src/core/tests/game/` and are assembled only for dev. This tool adds no player-facing runtime framework or release dependency. Its package-local `.gitignore` excludes Python caches.

Keep configuration, disposable baseline copies, reports, fresh logs, screenshots and MODLOG updates under ignored `.local/automation/` or `.local/MODLOG.md`. A uniquely named save staged under selected user data is temporary runner-owned state; it is removed on close. The original baseline and all other saves remain untouched. CLI and MCP share the same exclusive ownership lock and runner. See the [runner contract](../tools/game_runner/SPEC.md) for exact commands and the host-independent configuration schema.

The optional automation commands use an existing Python runtime; the packaging commands above use PowerShell/.NET only. MCP explicitly supports protocol 2025-11-25 and only the three bounded runner operations. Subprocess lifecycle, strict argument schemas, protocol/tool errors and EOF cleanup are tested without a real game; final integration uses one measured native smoke call. Serial dispatch has no progress or interruptible cancellation. See the [MCP interface and limits](../tools/game_runner/SPEC.md#mcp-stdio-interface).

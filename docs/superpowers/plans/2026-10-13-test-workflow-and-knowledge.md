# Test workflow and agent knowledge implementation plan

> For agentic workers: use subagent-driven-development with scoped implementers and independent review. The user explicitly requested implementation of the retrospective priorities using Sol 6.1 High. Continue through all tasks without another approval handoff.

**Goal:** Reduce repeated CK3 test setup, brittle UI work and manual evidence bookkeeping, enforce shared story acceptance requirements, and preserve reusable discoveries for future agents.

**Architecture:** Extend the existing Python game runner and PowerShell checks. Keep native story-owned fixtures and living specifications. Reuse the build manifest and strict runtime diagnostics. Add versioned repository knowledge rather than a second gameplay specification.

**Tech stack:** Existing Python standard library, PowerShell 7, native CK3 scripts; no new dependencies.

**Spec:** Existing `tools/game_runner/SPEC.md`, `docs/repository.md`, `src/core/SPEC.md`, story specifications, and the user's approved retrospective priorities. Update these living contracts in the implementing tasks.

## Global constraints

- All repository content and tool output are English; no new gameplay or localization language.
- Work in the existing clean task checkout and branch; preserve user changes.
- No game-install edits, publication, push, PR, new dependencies, or unrelated refactors.
- Exactly one live CK3 owner at a time; disposable baseline and exact-PID cleanup only.
- Existing runner CLI/MCP behavior remains compatible; add bounded named operations, never an arbitrary script execution API.
- Newly automatable checks must be registered, reproducible and retain measured evidence. Unit tests do not certify native UI behavior.
- Local saves, profile backups, raw logs, screenshots and machine-specific paths remain ignored.
- Implementers use gpt-6.1-sol/high; reviewer uses gpt-6.1-sol/xhigh as previously requested. Parent orchestrates and validates evidence.

## Review focus

- Cleanup after partial setup, startup failure, assertion failure and deadline; never overwrite concurrent user changes or delete unowned files/processes.
- Source/build drift or missing screenshots/logs must not produce a successful evidence claim.
- DPI/window mismatch, stale event and wrong Story selection must not pass merely because input was sent.
- Contract checks must find missing requirements across all families without pretending to prove game semantics.
- Knowledge must distinguish measured behavior, source inspection and unsupported hypotheses, with reproducible references and no committed runtime artifacts.

### Task 1: Complete session workflow and generated evidence (priorities 1 and 4)

**Own:** `tools/game_runner/` session orchestration, profile management and evidence modules/tests, CLI additions, corresponding SPEC/scenarios and command documentation. Keep UI operation implementation for Task 2.

**Consumes:** existing Config, GameRunner, SessionGuard, strict diagnostics and `.build/<profile>/manifest.json`.
**Produces:** a documented one-command managed regression session, bounded subprocess lifetime, targeted profile preparation/restoration, and generated machine-readable plus concise human-readable evidence report. Record exact additive CLI/API in the owning SPEC for Task 2.

- [ ] Inspect existing setup helpers and runner ownership; write focused failing tests for normal and failed cleanup, external mutation, deadlines and provenance.
- [ ] Implement the smallest complete prepare/run/collect/restore workflow with explicit safe boundaries and failure results. Extend the existing source map, not a parallel source registry.
- [ ] Make reports identify revision/dirty state, built files/hashes, scenarios/assertions, evidence files, durations, process cleanup and profile restoration; missing/stale evidence cannot count as success.
- [ ] Run bounded offline suites and one live registered regression through the new command, retaining fresh evidence and restoration checks.
- [ ] Update living docs and commit scoped changes. Independent review before Task 2.

### Task 2: Reproducible UI operations (priority 2)

**Own:** runner Windows/UI modules and tests, registered UI scenario, dev-only native fixture/assertions, corresponding living docs.
**Consumes:** Task 1 managed session and evidence reporting, existing native Story identity/management callbacks.
**Produces:** bounded named operations for opening aspirations, selecting an exact Story, declaring an eligible goal, and saving/reloading a disposable campaign, exposed through a registered scenario and reusable within the runner.

- [ ] Inspect actual current UI and existing local helpers; design against supported window geometry and centralize screenshot/client/DPI coordinate conversion.
- [ ] Add failing tests for coordinate conversion, stale/wrong selection, identity/confirmation, missing evidence and cleanup. Do not implement a click-only success oracle.
- [ ] Implement named operations with native measured assertions and actual screenshots, using scoped fixtures for deterministic setup. Unsupported geometry/state must fail clearly.
- [ ] Run the registered UI sequence in real CK3, inspect frames, prove exact Story identity/declaration and save/reload persistence, then prove restoration.
- [ ] Update SPEC/scenarios, commit and pass independent review.

### Task 3: Shared story contract and agent knowledge base (priority 3 plus new request)

**Own:** story acceptance checklist/template, targeted automated contract checks and tests, `docs/knowledge/`, `AGENTS.md`, repository/design navigation and modding-note migration/index.
**Consumes:** existing three family contracts, durable modding notes and final runner interfaces.
**Produces:** reusable story authoring/acceptance guide plus checks, versioned searchable knowledge index and topic notes, and mandatory agent read/update workflow.

- [ ] Establish shared acceptance requirements for origin/target identity, lifecycle, completion/abandonment, stale actions, visible card keys/state and reproducible regression references; preserve legitimate family differences.
- [ ] Add meaningful negative/positive contract tests to existing tooling. Keep prose authority with existing SPEC files; do not add a new game DSL or claim static semantics validation.
- [ ] Create indexed topic notes with status, CK3 version, observation, evidence/reproduction, implications and limits. Seed construction reservation/payer/token ownership, Story scopes/localization, lifecycle/calendar, automation/profile/DPI and known unsupported knowledge hooks from verified project findings.
- [ ] Make AGENTS require consulting relevant notes first and updating findings in the same change; explicitly record no new durable finding when appropriate. Prefer portable tracked references over ignored historical reports as the only evidence.
- [ ] Replace duplication in modding-notes with navigation or carefully scoped retained material, update links and verify checks. Commit and pass independent review.

## Completion

- [ ] Bounded relevant offline/tooling checks and dev/release build/check pass; all new native operations have measured live evidence or an explicit unresolved blocker.
- [ ] Final independent review covers combined changes and knowledge discoverability; parent validates reports, manifests and native screenshots.
- [ ] Owned processes stopped, profile restored, baseline unchanged, worktree clean; report usable commands, evidence, limits and commits.

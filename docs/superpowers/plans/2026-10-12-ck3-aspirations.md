# Aspirations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a locally playable, English-only CK3 prototype whose three contextual aspiration families support character roleplay, with living specifications and Workshop-compatible packaging.

**Architecture:** Author native CK3 scripts in story-owned modules, each with a colocated specification and scenarios. A shared core owns lifecycle and management; a dependency-free PowerShell assembler copies modules into native mod directories. Prove the complete vengeance lifecycle in the game before adding recovery and personal bonds.

**Tech Stack:** CK3 1.20.0.4 (Crozier) script, story cycles, additive on-actions, decisions, events, memories, English localization; PowerShell and .NET; Git. No runtime framework or script transpiler.

**Spec:** [Approved design](../specs/2026-10-12-ck3-aspirations-design.md). Read the entire spec before execution. Task 1 migrates it to the authoritative living documents and leaves this link as a historical index.

## Global Constraints

- Mod name: **Aspirations**; repository identifier: `ck3-aspirations`; script prefix: `asp_`.
- All authored repository content is in English. English is the only localization included in the prototype: `localization/english/*_l_english.yml`, `l_english:` header, UTF-8 with BOM.
- Player character only; initial runtime acceptance uses a single-player campaign and an adult landed ruler. AI pursuit, additional governments, multiplayer, landless coverage, and RICE compatibility are not promised.
- Three families only: `vengeance`, `holding_recovery`, `personal_bond`. No free CB, imprisonment reason, unlocked scheme, construction reimbursement, or changes to fervor.
- One story instance per aspiration. No main aspiration. Hard caps: three ambitions and five desires; one active instance per family and target; a consumed incident cannot generate another proposal or reward.
- Routine relationship selection: quarterly, base 20%, desire occupancy multipliers `1.0 / 0.6 / 0.3 / 0.1 / 0.1 / 0` for counts `0 / 1 / 2 / 3 / 4 / 5`; twelve-month routine cooldown.
- Major loss selection: base 50%, ambition occupancy multipliers `1.0 / 0.7 / 0.4` for counts `0 / 1 / 2`; vengeance receives a Vengeful multiplier of 1.5; final chance at most 90%. At capacity, use an explicit replacement offer without eviction.
- First review: desire 24 months, ambition 8 years. Retain: next review in twelve months or three years, respectively. Preserve origin age on reinterpretation and player switching.
- Early abandonment: desire 5 stress; ambition 10. Vengeance: Vengeful 15, Compassionate without Vengeful 5, otherwise 10. Release at review age and uncontrollable impossibility are free, subject to a still-active pledge's rules.
- Fulfillment: desire removes 10 stress; ambition removes 20. Friendship adds 50 diplomacy lifestyle experience; accountability adds 100 prestige; recovery adds 100 stewardship experience and local +5% tax for 3 years, non-stacking.
- Pledges: vengeance and recovery only, minimum age twelve months, five-year deadline. Success adds 100 prestige once; failure or withdrawal removes 100 prestige and adds 15 stress once. Simultaneous abandonment does not add the private abandonment cost.
- Declaration requires no qualifying irreversible milestone: vengeance target not already in custody; recovery has neither control 80 nor qualifying completed construction. Secret vengeance grants private closure but settles an unverifiable pledge under the withdrawal policy.
- Content allows contextual grief, recovery, and relationships. Vanilla personality stress, tyranny, opinion, secrecy, and legal restrictions remain in force.
- Private aspirations have no mandatory completion deadline and no passive accumulating stress for remaining unfinished.
- Owner death ends aspirations. Switching away suspends processing and rewards; return closes objectives achieved during absence without retrospective rewards and settles expired pledges once.
- Installation and Workshop files are read-only references. No new dependencies. No publish, push, or PR. No source assets extracted from the game.
- Dev output: `.build/dev/mod/`; release output: `.build/release/mod/`; local state: `.local/`; archives: `dist/`. Only dev includes `tests/game/` fixtures. Never rebuild dev output while its test process is running.
- Preserve source bytes and relative paths. Reject destination collisions, including case-only collisions. Replace only verified generated paths under this repository's `.build/`; reject reparse-point escapes.
- The first repository commit includes the migrated specifications and working repository setup. Every gameplay change updates its owning specification and acceptance scenarios.

## Review Focus

1. Repeated callbacks, two aspirations in the same family, or an old management event must never pay twice or change the wrong story: `C02`, `C03`, `P06`, `I01`.
2. A concealed killer reference must not disclose a secret; death processing must distinguish fulfillment from unrelated death: `V02`, `V03`, `V04`.
3. Existing, cancelled, foreign-funded, or ownership-interrupted construction must not satisfy recovery: `H02`, `H03`, `H04`.
4. Save/load and switching away across review or pledge dates must preserve age, resolve once, and never deliver rewards or events to the wrong character: `P04`, `P05`, `I02`.
5. Windows paths with spaces, case collisions, stale output, and linked directories must not corrupt unrelated files or leak dev content into release: `T01`, `T02`, `T03`, `T04`, `T05`, `T06`, `I04`.

---

## Execution Environment and Evidence

The user selected `D:\Projects\ck3-aspirations` as the permanent repository location. Create it at execution time, after inspecting for existing contents; do not put absolute machine paths into portable source files. Use the host's required filesystem escalation for creating it outside the current writable roots. If approval review blocks creation, preserve the plan and explain the exact block rather than silently relocating the repository.

The source installation is `D:\SteamLibrary\steamapps\common\Crusader Kings III`. The current spec and plan are in the chat artifact workspace. Copy their authored content during Task 1; retain the artifact originals as review records. Do not initialize Git in the game installation. Create a task branch in the new repository; if an existing repository is discovered, inspect its status and follow `superpowers:using-git-worktrees` without reverting local work.

Use existing PowerShell and Git. The app also provides bundled Python, which can run the installed universal-modder tooling if needed. Resolve its location through `load_workspace_dependencies`, keep machine paths in `.local/`, and check CLI availability before relying on it. Do not bootstrap Python, uv, a package manager, Pester, or another dependency.

Local source evidence establishes syntax candidates, not runtime correctness:

| Game-relative reference | Evidence and implementation obligation |
| --- | --- |
| `game/common/story_cycles/_story_cycles.info`, `debug_test_story_cycle.txt` | Visible stories, lifecycle hooks, `create_story` with `save_scope_as`; retain the newly created instance directly. |
| `game/events/story_cycles/debug_story_cycle_test_events.txt` | Native debug-event setup examples; do not select an arbitrary owned story after creation. |
| `game/common/on_action/_on_actions.info` | Append mod child on-actions; do not replace native effect or trigger blocks. |
| `game/common/on_action/death.txt`, `game/common/secret_types/00_secret_types.txt` | Killer reference and secret discovery are distinct; `add_knows_of_killer` and `set_killer_public` exist, but the matching read-side knowledge predicate still requires verification. |
| `game/common/on_action/prison_on_actions.txt` | Prisoner root and `scope:imprisoner` for accountability. |
| `game/common/on_action/army_on_actions.txt` | Siege/raid causes; capture the affected county and pre/post incident state available from the actual hook. |
| `game/common/on_action/province_on_actions.txt` | Construction hooks; native start effects may substitute county holder when payer is absent. Never treat that substitution as proof of payment. |
| `game/common/on_action/relations/relation_on_actions.txt` | Relationship set/remove/death callbacks. |
| `game/common/on_action/player_change_on_actions.txt` | New player root and `scope:previous_player_character`; verify activation, succession, and switch behavior separately. |
| `game/common/character_memory_types/_character_memories.info` | Memories with character participants and saved references. |
| `game/common/story_cycles/ep3_story_cycle_admin_eunuch.txt` | Saving `current_date`; verify calendar comparisons and deadline behavior in the engine. |

Before implementing a rule dependent on unknown syntax, inspect generated script documentation and run a minimal dev-only probe. The knowledge predicate, construction attribution, calendar timing, and event-held story references are explicit capability checks. If the engine cannot express an approved condition, report that precise limitation and propose a design adjustment; never substitute omniscience or inferred payment and call the scenario passed.

## Ownership and File Map

All paths below are repository-relative unless explicitly marked as local execution context. Do not create unused empty categories.

| Files | Responsibility |
| --- | --- |
| `README.md`, `AGENTS.md`, `.editorconfig`, `.gitattributes`, `.gitignore` | Setup, workflow, encoding boundaries, ignored generated/local state. |
| `docs/design.md`, `docs/repository.md`, `docs/modding-notes.md` | Shared product intent; assembly/ownership contract; versioned reusable engine findings. |
| `docs/superpowers/specs/2026-10-12-ck3-aspirations-design.md`, `docs/superpowers/plans/2026-10-12-ck3-aspirations.md` | Historical review index and this execution plan. |
| `src/core/SPEC.md`, `src/core/tests/scenarios.md` | Shared state, lifecycle, capacity, pledge policies, cross-story scenarios. |
| `src/core/game/common/scripted_effects/asp_core.txt` | Instance initialization, resolution, capacity, suspension, and review. |
| `src/core/game/common/scripted_effects/asp_dispatch.txt` | Explicit dispatch to implemented family policies; no runtime plugin registry. |
| `src/core/game/common/scripted_effects/asp_pledges.txt` | Declaration and one-time pledge settlement. |
| `src/core/game/common/scripted_triggers/asp_core.txt`, `src/core/game/common/script_values/asp_core.txt` | Shared guards, counts, cadence, and centralized numerical defaults. |
| `src/core/game/common/on_action/asp_core.txt`, `src/core/game/common/decisions/asp_core.txt` | Player lifecycle hooks and the management decision. |
| `src/core/game/events/asp_core_events.txt`, `asp_management_events.txt`, `asp_pledge_events.txt` | Lifecycle notifications; selection and actions; public commitment presentation. |
| `src/core/game/localization/english/asp_core_l_english.yml` | Shared English text. |
| `src/core/tests/game/common/story_cycles/asp_core_debug.txt`, `src/core/tests/game/events/asp_core_debug_events.txt` | Dev-only neutral story and repeatable engine scenarios. |
| `src/stories/<family>/SPEC.md`, `tests/scenarios.md` | Family contract and Given/When/Then acceptance record. |
| `src/stories/<family>/game/common/{story_cycles,on_action,scripted_triggers,scripted_effects,script_values,character_memory_types}/asp_<family>.txt` | Native family implementation, with each directory created only when needed. |
| `src/stories/<family>/game/events/asp_<family>_events.txt`, `game/localization/english/asp_<family>_l_english.yml` | Family narrative and English text. |
| `src/stories/<family>/tests/game/events/asp_<family>_debug_events.txt` | Family fixtures, never present in release. |
| `src/stories/holding_recovery/game/common/modifiers/asp_holding_recovery.txt` | Temporary non-stacking county tax modifier. |
| `packaging/descriptor.mod`, `packaging/CREDITS.md`, `packaging/INSTALL.md` | Portable metadata, attribution, manual install instructions. |
| `tools/build.ps1`, `check.ps1`, `install-dev.ps1`, `package.ps1`, `tools/Aspirations.Build.psm1`, `tools/tests/run.ps1` | File assembly and validation, descriptor registration, packaging, focused tooling tests. |

Each family uses its `asp_<family>` event namespace; shared namespaces are `asp_core`, `asp_management`, and `asp_pledge`. Dev fixtures use `asp_test_core`, `asp_test_vengeance`, `asp_test_holding_recovery`, and `asp_test_personal_bond`. Allocate and document event IDs in the owning SPEC; never repurpose a saved ID for an unrelated event.

## Shared Script Contract

The signatures below describe native scripted-effect parameters and scope types, not a new source language. Effects return no value. Triggers return a native boolean. Define the exact native syntax only after the scope and timing probes pass.

Implementation defaults proposed for this plan's review where the approved spec did not fix a value: one declaration per instance; expiry at the recorded deadline rather than after it; full-cap offers use the prospective two-remaining-ambitions multiplier `0.4`; Lustful uses romantic weight multiplier `1.5`; pledge audience is the owner's court and realm, with no additional opinion effects. Record these in the owning living contracts during implementation.

- Character-scope family entry effects: `asp_start_vengeance_effect = { VICTIM = <character> KILLER = <character> }`, `asp_start_holding_recovery_effect = { COUNTY = <county title> }`, and `asp_start_personal_bond_effect = { TARGET = <character> MODE = <friendship|romance flag> }`. They revalidate eligibility, consume their origin, reserve capacity, create the story, and open interpretation for its owner. Debug forcing bypasses randomness only, never eligibility.
- Story-scope `asp_initialize_story_effect = { FAMILY = <family flag> CLASS = <ambition|desire flag> TARGET = <character|county title> }`. Store owner, origin time, review state, schema `1`, target, and a monotonically allocated owner-local instance ID. Family effects add their cause and interpretation before the first visible event.
- Story-scope `asp_resolve_story_effect = { OUTCOME = <fulfilled|abandoned|forgiven|impossible|owner_dead flag> REWARDS = <normal|none flag> }`. Guard and latch resolution before dispatching family consequences, memory, cleanup, and `end_story`. This is the sole terminal payout entry point.
- Story-scope `asp_refresh_story_effect = yes`. Revalidate owner and objective, process due dates, and request family checks; a suspended owner cannot earn rewards. On return, settle expired pledges before closing an objective achieved during absence without rewards.
- Story-scope `asp_can_manage_story_trigger = yes`. Requires a live unresolved instance owned by the current player. Recheck on every event option; saved selections are not authorization to affect a different or ended story.
- Story-scope `asp_family_check_progress_effect = yes` and `asp_family_resolve_effect = { OUTCOME = <outcome flag> REWARDS = <normal|none flag> }`. Core dispatch routes to the matching `asp_<family>_check_progress_effect` or `asp_<family>_resolve_effect` after that family exists. The three approved family flags are recognized from Task 2; before a branch is implemented it performs no family effects, while shared lifecycle effects remain testable. Unknown flags are rejected.
- Story-scope `asp_declare_story_effect = yes` and `asp_settle_pledge_effect = { RESULT = <fulfilled|withdrawn|expired|excused flag> }`. Declaration saves a five-year deadline; settlement latches before applying effects, clears public state, and cannot be re-entered for that declaration.
- Character-scope `asp_open_management_effect = yes`. Save up to eight story references into event-context slots `asp_choice_1` through `asp_choice_8`. Selection saves `scope:asp_selected_story`; actions carry that exact reference through later events. Never use a character-global mutable selected story.

Persisted story fields use `asp_` names: `asp_schema`, `asp_instance_id`, `asp_family`, `asp_class`, `asp_target`, `asp_origin_date`, `asp_next_review_date`, `asp_interpretation`, `asp_resolved`, `asp_suspended`, `asp_declared`, `asp_pledge_deadline`, and `asp_pledge_settled`. Use verified calendar dates or native timed-variable expiry with explicit origin dates; record the chosen representation in `src/core/SPEC.md`. Timers must continue through save/load and suspension. Re-declaration must not reset an existing or settled pledge on the same aspiration; one declaration per instance in this prototype.

Shared values include `asp_desire_review_months = 24`, `asp_ambition_review_years = 8`, `asp_desire_repeat_months = 12`, `asp_ambition_repeat_years = 3`, `asp_declare_min_months = 12`, `asp_pledge_years = 5`, and the costs, rewards, caps, and probabilities from Global Constraints. Family values own only family-specific parameters. Parameter labels here are script-value IDs, not assumed engine time-unit conversions.

## Interface Layout

Use native visible story-cycle entries and a decision opening an event selector. Eight fixed, conditionally visible event options cover the hard cap without replacing game GUI files. Selection order may follow enumeration, but every option must retain the displayed instance's reference.

```text
Situations / Personal stories
  [icon] Avenge [victim]       Ambition | Private / Declared
  Cause, target, exact condition, age, next review / deadline

Decisions
  Review my aspirations
    [Avenge victim A] [Restore county B] [Befriend person C] ...
      Selected aspiration: title, cause, target, progress
      [Declare intention] [Reconsider] [Abandon] [Back]
```

Use game asset references without redistributing art. If native event options cannot render an adequately readable eight-item selector, demonstrate the limitation before changing the interface approach. Capture actual rendered screens during Task 2 and the final combined test.

## Test Method

PowerShell tests use local temporary fixture trees and .NET assertions, with nonzero exit on failure; no added framework. Every CK3 scenario records an ID, setup, exact expected deltas, and a dev event or manual procedure in its owning `tests/scenarios.md`. Debug entry points emit `ASP_TEST <ID> BEGIN` and exactly one `PASS` or `FAIL` for that invocation; inspect only the fresh log segment. A launcher return code or missing errors is not a gameplay assertion.

For example, the repeated-resolution fixture must observe the reward before it ends the story and then call the stale path again. Assert the stored delta using real native triggers:

```text
if = {
    limit = { var:asp_test_stress_delta = -20 }
    debug_log = "ASP_TEST C02 PASS"
}
else = { debug_log = "ASP_TEST C02 FAIL: expected one ambition stress reduction" }
```

This illustrates fixture assertions; it does not claim a general `assert` effect exists. Keep all `asp_test_*` state and events in dev fixtures. Runtime suites use a disposable save with observed pre/post snapshots and screenshots; replay natural callbacks as well as forced setup. Negative assertions include absence of a story, missing reward, and no secret-bearing text in the player's events.

Before the first launch, use `universal-modder:game-automation` to inspect existing processes and back up only affected profiles/saves/settings. Verify a supported isolation method before using it; do not assume a `-userdir` flag. Register a separate dev mod and use a disposable test playset, preserving the user's selected playset. If automation cannot safely select a separate playset, complete the package and request that precise manual setup step. Record the launched test PID, close only that process, and restore changed settings after testing.

## Task 1: Create the Repository and a Deterministic Native Mod Bundle

**Files:** Create the root files, documentation, three family `SPEC.md` and `tests/scenarios.md` files, `src/core/SPEC.md`, `src/core/tests/scenarios.md`, packaging files, and all `tools/` files listed in the file map. Runtime modules are introduced by later tasks; this task tests assembly with disposable native-file fixtures.

**Interfaces:**
- Consumes: the approved spec and local repository path selected by the user.
- Produces: `tools/build.ps1 -Profile dev|release [-RepositoryRoot <directory>]`, `tools/check.ps1 -Profile dev|release [-RepositoryRoot <directory>]`, `tools/install-dev.ps1 -UserDataPath <directory> [-RepositoryRoot <directory>]`, `tools/package.ps1 [-RepositoryRoot <directory>]`, and `tools/tests/run.ps1`. Commands exit `0` on success and nonzero on validation failure. The root defaults to the script's parent, independent of the caller's directory.
- `build.ps1` outputs the verified mod root and an ignored source/destination/SHA-256 manifest. `install-dev.ps1` writes only `aspirations_dev.mod` in the selected user-data `mod/` directory and preserves existing unrelated files; no playset mutation. `package.ps1` produces `dist/aspirations-<descriptor version>.zip` containing `mod/`, `INSTALL.md`, and `CREDITS.md`.

- [ ] **1. Inspect and create the independent checkout.** If absent, create `D:\Projects\ck3-aspirations`, initialize Git, and create `feat/aspirations-prototype`; if present, inspect before editing. Copy the reviewed plan and migrate the spec into the living contracts. Replace the repository's dated design document with an approved historical index linking those contracts. Add ignore rules before running tools.
- [ ] **2. Write tooling regression fixtures.** Implement `T01` byte/path preservation with spaces and English BOM; `T02` exact and case-only destination collision rejection; `T03` stale output removal with unrelated sentinel preservation; `T04` dev-only fixtures absent from release; `T05` traversal/reparse escape rejection before deletion or replacement; `T06` failed staging validation leaves the previous good output intact. Use concrete assertions such as:

  ```powershell
  if ($actualHash -ne $sourceHash) { throw 'T01: source bytes changed' }
  if ($collisionExitCode -eq 0) { throw 'T02: collision accepted' }
  if (-not (Test-Path -LiteralPath $sentinelPath)) { throw 'T03: unrelated file removed' }
  if (Test-Path -LiteralPath $releaseDebugEventPath) { throw 'T04: debug fixture leaked' }
  ```

- [ ] **3. Run the tests red.** Run `pwsh -NoProfile -File tools/tests/run.ps1`; expect failures naming the missing assembly/check commands. Confirm failures originate from the intended assertions, not an unavailable shell.
- [ ] **4. Implement byte-preserving assembly and focused checks.** Enumerate only approved module roots; reject colliding paths and linked-directory escapes; stage, validate, and replace only contained generated output. Generate deterministic sorted manifests without machine paths. Validate English localization, story-spec links, identifiable mod-owned duplicate IDs, and descriptor metadata. Checks must state their limitations as static analysis.
- [ ] **5. Implement registration and archive commands.** Resolve Documents using the actual OS configuration in setup instructions, require the resulting CK3 user-data directory explicitly for installation, and generate a distinct dev title without `remote_file_id`. Preserve a real release ID when present; reject invented placeholder IDs and absolute paths in the portable descriptor. Do not register into real user data during this task's tests.
- [ ] **6. Run the tests green and verify output.** Run the same tooling suite, then `build.ps1 -Profile dev`, `check.ps1 -Profile dev`, `build.ps1 -Profile release`, and `check.ps1 -Profile release`. Expect all tests to pass; repeated builds have identical ordered content hashes. Descriptor-only output is packaging evidence, not a playable mod. Inspect `git status --short` for generated or private files.
- [ ] **7. Commit the bootstrap and migrated contracts.** Stage only authored paths and commit `Initialize Aspirations repository and build tooling`.

## Task 2: Prove Native Story Lifecycle and Instance-Specific Management

**Files:** Create the core runtime files in the map except `asp_pledges.txt` and `asp_pledge_events.txt`; create core debug story/events. Update `src/core/SPEC.md`, `src/core/tests/scenarios.md`, `docs/modding-notes.md`, and shared localization.

**Interfaces:**
- Consumes: Task 1 dev builder, validator, and descriptor installer.
- Produces: `asp_initialize_story_effect`, `asp_resolve_story_effect`, `asp_refresh_story_effect`, `asp_can_manage_story_trigger`, `asp_open_management_effect`, and the dispatch interfaces in Shared Script Contract. The initial dev-only story uses a recognized family flag and supplies controlled completion and terminal-callback observations; release contains no debug story type. Family memories arrive with the corresponding family in later tasks.
- Character counters are derived from active owned stories and class, not an independently drifting stored count. Story initialization reserves a slot before displaying the interpretation event.

- [ ] **1. Write core scenarios and engine probes.** `C01`: create 3 ambitions and 5 desires, then reject one extra of each class. `C02`: fulfill the same instance twice, expecting one terminal callback, one slot release, and one `-20` stress payout for an ambition, starting above 20 stress. `C03`: open two same-family instances, select the second, end it through another callback, then click the old action; the first must remain unchanged. `C04`: save/load preserves target, instance ID, origin, and next review. Test assertions compare exact counts and target scope identity, including `active_ambitions = 3` and `active_desires = 5`.
- [ ] **2. Set up the disposable runtime test environment and run red.** Back up affected local state; resolve supported launch and debug-console access; register dev output. Run `event asp_test_core.1` in a disposable ruler campaign. Expect explicit fixture failure until core behavior exists; record the log interval and capability-probe results in `.local/MODLOG.md`.
- [ ] **3. Implement instance state and guarded resolution.** Use direct `save_scope_as` from creation. Prove story scopes survive event options and save/load before using them for management. Unknown schema/family states receive no payout and a diagnostic during development. Leave slot availability derived from surviving active stories.
- [ ] **4. Implement the selector and native story presentation.** Save each displayed reference in its own event-context slot and revalidate actions. Use a maximum of eight options and a Back action. Centralize costs and tooltips; no shared mutable selected target. Record verified calendar representation and scope lifetimes in core SPEC.
- [ ] **5. Run core scenarios green and inspect UI.** Build/check dev after closing the test process, relaunch, run `event asp_test_core.1`, and confirm fresh `C01`-`C04` PASS markers plus the observed counts and identities. Inspect `error.log`, capture the eight-entry selection and a visible story, and verify no unresolved keys or clipped essential conditions. Stop the test process before another build.
- [ ] **6. Commit.** Commit `Add aspiration lifecycle and instance management` with core SPEC, scenarios, and engine notes.

## Task 3: Implement the First Playable Vengeance Story

**Files:** Create vengeance runtime files and `src/stories/vengeance/tests/game/events/asp_vengeance_debug_events.txt` from the map. Update vengeance SPEC/scenarios, `src/core/game/common/scripted_effects/asp_dispatch.txt`, and durable modding notes.

**Interfaces:**
- Consumes: Task 2 lifecycle/dispatch interfaces and shared balancing values.
- Produces: `asp_start_vengeance_effect`, story-scope `asp_vengeance_check_progress_effect = yes`, and `asp_vengeance_resolve_effect = { OUTCOME = <outcome flag> REWARDS = <normal|none flag> }`; visible type `asp_vengeance_story`.
- Stores `asp_vengeance_victim` and fixed culprit in `asp_target`; interpretation is `personal_vengeance` or `accountability`. Incident identity is the victim's observed death; family-owned consumed-origin records survive closing the aspiration.

- [ ] **1. Write vengeance scenarios.** `V01`: forced eligible known killing creates exactly one ambition naming victim and culprit; repeated callback and abandonment never recreate that death. `V02`: a concealed murder creates no named aspiration or culprit-bearing text; only verified later knowledge may allow one proposal. `V03`: owner-caused death fulfills personal vengeance before generic invalidation, while unrelated death closes without reward; each terminal path creates exactly one appropriate memory even on repeated callbacks. `V04`: custody acquired after creation fulfills accountability for `+100` prestige and `-20` aspiration stress; preexisting custody cannot select it. `V05`: exclude owner culpability and rival/nemesis victims; allow Content grief; Vengeful and Compassionate costs follow `15/5/10`, including both-trait precedence. `V06`: killing with a conflicting trait retains the vanilla action's stress, separately from the explicit aspiration reduction.
- [ ] **2. Run the knowledge probe and tests red.** Inspect debug-generated trigger documentation for the owner-knowledge predicate; compare a public death, concealed murder, discovery, and exposure in the engine. Run `event asp_test_vengeance.1`; expect fresh `V01`-`V06` failures before implementation. An unavailable predicate is a reported capability failure, not permission to read hidden responsibility.
- [ ] **3. Implement cause capture and knowledge-safe eligibility.** Append death/prison child on-actions. Retain only relevant post-activation bereavement candidates for delayed knowledge checks where a verified notification permits them; do not replace `secret_murder`, scan historical deaths, or expose engine-only killer references. Apply 50% base, occupancy multipliers, Vengeful 1.5, and 90% cap; preserve rejected/consumed origin state so repeated hooks cannot reroll the same known incident.
- [ ] **4. Implement interpretations, fulfillment, and closure.** Reserve the story before interpretation; use existing legal actions only. Evaluate own responsibility before unrelated-death closure. Distinguish forgiveness from fulfillment in memories and text. Family effects add accountability prestige only, while shared fulfillment grants the class stress reduction once.
- [ ] **5. Run vengeance green.** Build/check dev, run `event asp_test_vengeance.1`, and verify fresh `V01`-`V06` PASS markers with observed character deltas. Exercise one real prison or killing action rather than only invoking completion effects. Inspect `error.log` and origin/fulfillment/invalidation screenshots; record how the engine proves knowledge and responsibility.
- [ ] **6. Commit.** Commit `Add contextual vengeance aspirations` with the family contract and test evidence references.

## Task 4: Complete Reviews, Pledges, Suspension, and Capacity Replacement

**Files:** Create core pledge effects/events from the map. Modify core effects/triggers/values/hooks, management events, localization, SPEC/scenarios/debug fixtures, vengeance declaration presentation, and vengeance scenarios. This is the complete first-story milestone.

**Interfaces:**
- Consumes: Task 3 working vengeance story and Task 2 selected-instance management.
- Produces: `asp_declare_story_effect`, `asp_settle_pledge_effect`, completed `asp_refresh_story_effect`, review scheduling, and explicit full-cap replacement flow.
- Family declaration policy is reached through story-scope `asp_family_can_declare_trigger = yes` in `src/core/game/common/scripted_triggers/asp_core.txt`; branch to `asp_<family>_can_declare_trigger = yes` only when that family is implemented. Personal bond always returns false.

- [ ] **1. Write lifecycle scenarios.** `P01`: desire review at 24 months and ambition at 8 years; retaining schedules 12 months/3 years, reinterpretation preserves origin. `P02`: declaration at 11 months fails, at 12 succeeds if eligible; target in custody fails. `P03`: five-year expiry or withdrawal costs exactly `-100` prestige and `+15` stress once; simultaneous abandonment adds no extra private cost; recognized success grants one extra `+100`, secret vengeance instead settles withdrawal. `P04`: switch away across a deadline, return twice, and observe one penalty to the original owner, zero rewards to the new player. `P05`: fulfillment during absence closes with memory/no retrospective reward; owner death releases all state without heir inheritance. `P06`: a fourth major ambition offers explicit replacement; cancel preserves all three, confirm charges only the selected old ambition's proper cost and produces exactly one new instance.
- [ ] **2. Run lifecycle tests red.** Run `event asp_test_core.2` and the pledge branch of `event asp_test_vengeance.2`; expect missing review/pledge/switch behavior, not a script parse failure. Advance actual calendar time around boundaries in a disposable save and save/reload before at least one deadline.
- [ ] **3. Implement review and full-cap replacement.** Show exact costs before action; free release is available once the initial review age is reached, even if a reminder was retained. Never reset origin or issue a replacement bonus. For a full-cap major-event offer, use the two-remaining-ambitions multiplier `0.4` as a provisional tuning choice, then require explicit replacement before creating a third instance. Capture a pending cause for the replacement choice, revalidate it after selection, and keep the old story if the new one is no longer eligible. Consume the incident even if the offer is declined.
- [ ] **4. Implement public commitment settlement.** State audience as the owner's court and realm in the declaration narrative, without inventing opinion bonuses. Save one immutable deadline per declared instance. Record public attribution for success, excuses for external impossibility, and the secret-success cost upfront. Evaluate due pledge settlement before accepting post-deadline completion; equality with the recorded deadline is expired. Document this ordering in core SPEC and tooltips.
- [ ] **5. Implement switch, return, succession, and owner-death paths.** Suspend non-player owners; retain elapsed calendar state. On return settle an expired pledge first, then close an objective completed during absence with `REWARDS = none`, then offer due reconsideration for remaining goals. Never queue action events for an AI owner. End personal goals on owner death and evaluate the successor's own current context separately.
- [ ] **6. Run the complete vengeance lifecycle green.** Run both fixture entry points, confirm fresh `P01`-`P06` PASS markers, and replay birth of a goal through declaration and a terminal outcome in the game. Inspect saved targets/dates after reload, `error.log`, and screenshots of review and declared state. Do not proceed to Task 5 with unresolved first-story failures.
- [ ] **7. Commit.** Commit `Complete aspiration reviews and public commitments`.

## Task 5: Add Recovery of a Damaged Holding

**Files:** Create holding_recovery runtime files, modifier, and debug fixture from the map. Update its SPEC/scenarios and core dispatch/declaration branches; update modding notes with payer and ownership evidence.

**Interfaces:**
- Consumes: completed core lifecycle, pledges, and full-cap replacement.
- Produces: `asp_start_holding_recovery_effect`, `asp_holding_recovery_check_progress_effect`, `asp_holding_recovery_resolve_effect` with the same arguments as the core family contract, `asp_holding_recovery_can_declare_trigger`, and `asp_holding_recovery_story`.
- Family state records incident county/control/date, qualifying post-origin construction identity, verified payer, start/completion, and cancellation/ownership invalidation. `asp_target` is the county title; no replacement target is chosen silently.

- [ ] **1. Write recovery scenarios.** `H01`: newly observed enemy siege/raid, personally held county, control `69`, and available suitable construction can create one ambition; control `70`, another owner's county, and no buildable option cannot. `H02`: control `80` alone fails; an already-started building fails; new owner-funded completed construction plus control `80` succeeds for `+100` stewardship experience, `-20` stress, and one three-year `+5%` county tax modifier. `H03`: cancellation, restart, foreign payer, and missing reliable payer do not qualify the wrong construction. `H04`: involuntary loss closes free; voluntary grant uses abandonment or one pledge penalty; transfer and reacquisition cannot launder old construction. `H05`: declaration fails if either control `80` or qualifying completion already exists; repeat incident while active does not stack goals or modifiers.
- [ ] **2. Probe attribution and run red.** Observe genuine player-funded, AI-funded, and script-started construction callbacks before and after the native payer fallback; inspect cancellation and completion identifiers. Verify a supported way to tell a voluntary grant from an involuntary loss. Run `event asp_test_holding_recovery.1`; expect explicit scenario failures until implemented. Do not infer payer from the current county holder.
- [ ] **3. Implement incident and construction tracking.** Append verified siege/raid/construction/title-change child hooks. Deduplicate the same county incident conservatively and record its origin. Define eligible building categories from actual available engine data and show them in the origin event. Snapshot real post-origin starts and clear invalidated construction records; require both conditions while personally held.
- [ ] **4. Implement recovery narrative and consequences.** Provide protection, family-prestige, and income wording without creating separate construction systems. Use centralized class rewards and the family-only XP/local modifier; voluntary loss is not an impossible-goal excuse. Link observed engine constraints in the live SPEC.
- [ ] **5. Run recovery green.** Build/check dev, run the fixture suite, and verify fresh `H01`-`H05` PASS markers. Finish at least one construction started through the actual game interface and observe its payment, completion, control, and modifier. Compare county tax modifier presence/duration, not fluctuating total income. Inspect log and screenshots.
- [ ] **6. Commit.** Commit `Add holding recovery aspirations`.

## Task 6: Add Contextual Personal Bonds and Routine Cadence

**Files:** Create personal_bond runtime files and debug fixture from the map; update family SPEC/scenarios, core dispatch, core scheduling hooks/values, and shared scenarios.

**Interfaces:**
- Consumes: shared desire lifecycle and core occupancy/cooldown values.
- Produces: `asp_start_personal_bond_effect`, `asp_personal_bond_check_progress_effect`, `asp_personal_bond_resolve_effect` with the shared arguments, and `asp_personal_bond_story`. Declaration is always unavailable.
- Character-scope `asp_try_personal_bond_effect = yes` performs bounded quarterly current-player selection. It records concrete context and a consumed context key per target; an unchanged court connection cannot regenerate after abandonment. Fresh observed context is required to revisit a consumed target.

- [ ] **1. Write bond/cadence scenarios.** `B01`: adult reachable court acquaintance or known positive contact with a legitimate pursuit path is eligible; arbitrary stranger, unavailable scheme-only path, existing desired relation, or invalid attraction is not. `B02`: new friend/best friend grants `-10` stress and `+50` diplomacy experience once; new lover/soulmate grants `-10` and no diplomacy XP or pledge. `B03`: target death closes free; temporary range loss retains; permanent incompatibility offers free closure; rival transition offers retain/release without retargeting. `B04`: assert effective routine chances `20/12/6/2/2/0` percent at desire counts `0..5` and a twelve-month cooldown; no repeated reward from unchanged context. `B05`: Content remains eligible and Lustful increases romantic weight without forcing the choice or bypassing vanilla eligibility.
- [ ] **2. Run bond tests red.** Run `event asp_test_personal_bond.1`; expect the missing story and cadence assertions to fail. Inspect native interaction eligibility and event context instead of assuming every ruler can start Befriend or Seduce.
- [ ] **3. Implement bounded context selection.** Begin with verifiable current court connections and positive relations; use recorded shared-event context only where the engine exposes it reliably. An activation/succession seed may describe current acquaintance honestly. Observe fresh context changes to permit a later revisit; periodic polling is not itself a new incident. Centralize and test a provisional Lustful romantic weight multiplier of `1.5` in the family SPEC as a tuning choice, not a guaranteed outcome.
- [ ] **4. Implement interpretations and relationship outcomes.** Keep friend/best-friend and lover/soulmate goals distinct, with fixed targets and supported existing pursuit paths. An interpretation change never accepts an already achieved relationship or resets age. Preserve ordinary scheme, attraction, and activity requirements.
- [ ] **5. Run bonds and cadence green.** Run the fixture suite and confirm fresh `B01`-`B05` PASS markers. Test one actual relation-setting path. Verify chances by script-value assertions and forced boundary rolls where supported; do not claim statistical validation from a small random sample. Inspect events and confirm no public-declaration control for bonds.
- [ ] **6. Commit.** Commit `Add personal bond desires and routine emergence`.

## Task 7: Verify the Combined Prototype and Prepare Distribution

**Files:** Update core cross-story fixtures/scenarios, owning story specs when behavior changes, `README.md`, `docs/modding-notes.md`, `docs/repository.md`, and packaging files. No new gameplay family or unrelated refactor.

**Interfaces:**
- Consumes: all three playable families, shared lifecycle, and Task 1 packaging commands.
- Produces: verified local dev installation, a Workshop-compatible release mod root, manual archive, documented tested version/limitations, and local evidence references. Actual publication is a separate operation requiring user instruction.

- [ ] **1. Write combined acceptance scenarios.** `I01`: maintain three ambitions/five desires across all families, resolve a selected story, and prove other targets and rewards unchanged. `I02`: save/reload, switch/return, succession, target death, and county loss retain the required state and one-time guards. `I03`: naturally play one character session with ordinary randomness; record in-game duration, incidents, accepted/rejected proposals, occupied slots, stress costs, and notification frequency. `I04`: release contains only native runtime content plus descriptor at the upload root; no debug namespaces, fixture files, specs, local paths, non-English localization, saves, logs, or extracted assets.
- [ ] **2. Run combined tests before final fixes.** Run `event asp_test_core.3` and tooling checks. Record actual failures; if all scenarios already pass, do not manufacture a red test. Natural play is qualitative evidence and must not be marked passed by forced debug generation.
- [ ] **3. Fix only failures within the approved contract.** Update implementation, living SPEC, and scenarios together. If natural play suggests numerical changes, document observations and proposed values rather than silently changing the approved balance. Run the affected focused suite after each fix.
- [ ] **4. Verify the full relevant suite.** Run tooling tests, dev/release checks, all fixture entry points, and the required genuine gameplay paths. Save screenshots for origin, visible stories, selection, review, declaration, fulfillment, and invalidation under `.local/`; inspect fresh `error.log` and classify baseline game errors separately. Record all untested combinations explicitly.
- [ ] **5. Build and inspect the release archive.** Stop the tracked test game, run `pwsh -NoProfile -File tools/package.ps1`, inspect archive entries, and test a fresh manual installation in the disposable playset. Confirm the Workshop upload source is `.build/release/mod/` itself, with no extra parent layer. Preserve any genuine `remote_file_id`; do not invent or publish one. Document license choice as required before a future public release, without assigning a license on the user's behalf.
- [ ] **6. Restore test environment and perform final review.** Restore changed profile/settings/playset state, stop only task-owned processes, inspect Git diff/status, and run `superpowers:verification-before-completion` and the review required by the chosen execution workflow. Record engine validation limits candidly; static checks alone cannot satisfy delivery.
- [ ] **7. Commit and deliver locally.** Commit `Verify Aspirations prototype and release packaging`. Provide repository and package locations, commands, tested CK3 version, evidence summary, and remaining limitations. Do not push, open a PR, or upload to Workshop.

## Author Self-Review

- Spec coverage: Tasks 1 and 7 cover repository/distribution/language; Task 2 covers instances/interface; Tasks 3 and 4 complete vengeance/lifecycle/commitments; Tasks 5 and 6 cover the other approved stories; Task 7 covers natural play and combined acceptance.
- Step scan: every task owns scenarios, a failing verification where functionality is missing, implementation, verification, and a commit. No additional tool dependency or full source implementation is embedded here.
- Interface consistency: family entry effects use character scope; lifecycle/progress/pledge effects use story scope; all terminal paths use `asp_resolve_story_effect`; selected-instance actions use saved event scopes.
- Review focus: the five listed risks have named tests in the tasks that own their implementation.
- Explicit uncertainties: knowledge read-side predicate, reliable construction payer and transfer cause, calendar representation, and event-held story scope lifetime require engine probes. No runtime test has been claimed from source inspection.
- Handoff: implementation has not begun. Review this plan and select native execution or subagent-driven execution. Native execution is recommended because the tasks share lifecycle interfaces and one sequential game-testing environment; use a fresh whole-branch reviewer at the end.

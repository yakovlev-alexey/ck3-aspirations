# Story scope, event context and native localization

Status: measured-native rendering; source-inspected getter/reference patterns; static key controls.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

The visible `asp_core_debug` story cycle rendered its name from `asp_core_debug` and also requested the implicit `asp_core_debug_desc` key in the Situations story card. A separate `visualization.custom_string_key` supplied card body text but did not replace this implicit description; without the key, the card displayed the raw identifier even though `error.log` had no missing-localization line. Dev fixture localization now defines both keys. `tools/game_runner/tests/test_core_fixture_localization.py` checks the static contract; a native card screenshot remains necessary to verify rendering. New family story cycles must define their matching `<type>_desc` key.

Task 3 also validates that `save_scope_value_as` transports numbers and booleans only. Passing a persisted flag variable produces wrong-type errors and wrong terminal descriptions. Encode event-held outcome as small numeric values and accountability as a boolean; keep the persisted core/family flags unchanged. Registered V01-V03 assertions verify the caller-visible terminal codes; custody resolves in a separate on-action chain, so V04 observes its exact memory/rewards and a separate visual callback validates that event description.

The story-cycle info file describes a `STORY` display scope, but actual native localization uses the case-sensitive GUI getter `Story.MakeScope`, confirmed by installed `debug_story_test_event_l_english.yml` and the El Cid story. Uppercase STORY produced visible ERROR expressions and data-factory errors during actual story-card inspection; retain that failure and recapture the corrected native card. Story title and implicit `_desc` keys are both required.

Native scope presence localization uses `Var('name').IsSet`; `MakeScope.HasVariable` is not a data-system function. Dynamic deadline text needs its native story/event context: direct declared descriptions and story-compatible `customizable_localization` follow installed `CompositionTypeAll`/`Story.Custom` patterns. Native event option ownership descriptions use `custom_description` with authored text; hidden internal validation does not grant an action to a stale story. Native creation references must be optional during tooltip description evaluation because `create_story` has not executed there. Preserve and recapture actual render/hover evidence; static identifier validity alone is insufficient.

Native tooltip evaluation can revisit an ended weak story after the effect frame completes. A direct same-frame predicate check does not prove that render path. Story-local conditional guards and a missing-target existence false branch both failed during real later-frame rendering; the validated event-character guard is described below. Dead characters do not support variable writes; capture their supported Prestige/Stress getters on a live character and require both snapshot variables before comparisons.


### Ended Story event rendering (CK3 1.20.0.4)

Native tooltip construction can visit a weak ended Story even through an optional `?=` scope and despite earlier false predicates in the same group. A Story-local `trigger_if` is itself an untyped trigger requiring a valid Story; changing its false branch from `always = no` to an existence test does not protect the tooltip traversal. Validate the event-held link inside `trigger_if` on the live event character before entering any family predicate. Preserve exact ownership checks inside the successful branch. Shared lifecycle P02/P05 test live and ended character-context guards; a later-frame real stale-modal hover and fresh startup/action logs remain required evidence.

Use native `fallback = yes` on an existing Close option to guarantee a harmless way out when queued origin interpretations have all become invalid. It avoids competing existence checks over an expiring Story. Installed reference examples are `events/decisions_events/roman_restoration_events.txt` (`roman_restoration.0002.e`) and `events/secret_events/secrets_events.txt` (`secrets.1001.option_fallback`). The final shared entrypoint/render interval verifies no no-valid-options or weak-scope error. Preserve UTF-8 BOM explicitly when editing native text; a misdecoded BOM can invalidate a top-level trigger definition while static brace balance still passes.

Native tooltip generation does not short-circuit adjacent filter predicates. Enumerating all owned Stories in replacement cause validation can visit invisible bond context Stories without aspiration fields, or compare a recovery Title target against a vengeance Character target despite a false adjacent family condition. Use explicit native trigger_if schema presence, then exact family, with false trigger_else branches before reading aspiration identity/target. Registered combined mixed-cap RED/GREEN and valid/distinct versus duplicate target checks cover that route. This does not replace the live-event-character guards around weak ended Story links.

Personal-bond cards use existing Story.Custom composition in the native Story context to render the selected Friend/Best Friend or Lover/Soulmate condition. Story.MakeScope retains exact target, age and review. Both native mode frames and focused implicit-key/branch checks are required; no gameplay mode or reward changes are implied by this presentation correction.

## Evidence and reproduction

[Core stale/calendar procedures](../../src/core/tests/scenarios.md), [management guards](../../src/core/game/common/scripted_triggers/asp_core.txt), [vengeance guards](../../src/stories/vengeance/game/common/scripted_triggers/asp_vengeance.txt), [family stale render procedures](../../src/stories/personal_bond/tests/scenarios.md#mandatory-rival-target-loss-and-stale-render-procedures), [integrated native fixture](../../src/core/tests/game/common/scripted_effects/asp_integrated_test.txt), [core implicit-key regression](../../tools/game_runner/tests/test_core_fixture_localization.py), [integrated localization checks](../../tools/game_runner/tests/test_integrated_localization.py) and [source-only shared checker](../../tools/check-contracts.ps1). Native getter references include installed `debug_story_test_event_l_english.yml`, El Cid and `CompositionTypeAll` patterns; paths are game-relative and no game asset is tracked.

## Implication

Validate a weak link from live event-character context before Story traversal, then require exact ownership. Branch on aspiration schema and family before reading fields in mixed Story lists. Supply implicit title/description and exact state body keys; transport numbers/booleans rather than persisted flags into event values. Preserve native BOM and render actual later-frame hover/close.

## Limits

Optional ?= and adjacent false predicates did not protect all native tooltip traversal. Story-local guards alone failed. Static keys/brace checks do not prove rendering or callback scope. A missing implicit key may show raw text without any log error. Existing bounded Trigger Localization notices are disclosed in scenarios; other weak-link/DataFactory/parser/no-options errors remain failures, even if resources were unchanged.

[Knowledge index](README.md)

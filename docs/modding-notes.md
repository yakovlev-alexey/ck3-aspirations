# Modding notes

## Local technical evidence

The inspected installation reports CK3 1.20.0.4 (Crozier) in `launcher/launcher-settings.json`. Source inspection establishes available scripting surfaces; runtime acceptance tests establish whether our use of them works.

| Local source, relative to the CK3 installation | Relevant capability |
| --- | --- |
| `game/common/story_cycles/_story_cycles.info` | Story setup, termination, owner death, visibility, icons, target visualization, counters, decisions, interval effects |
| `game/gui/window_situation_list.gui` | Existing story-cycle entries and their visualization |
| `game/common/on_action/_on_actions.info` | Additive child on-actions without overriding an existing effect block |
| `game/common/on_action/death.txt` | Death reason and conditional killer reference; this alone does not establish character knowledge |
| `game/common/on_action/army_on_actions.txt` | Siege and raid hooks |
| `game/common/on_action/province_on_actions.txt` | Construction start and completion hooks; completion may identify the payer |
| `game/common/on_action/relations/relation_on_actions.txt` | Relationship set, removal, and death hooks |
| `game/common/on_action/player_change_on_actions.txt` | Player-character changes |
| `game/common/character_memory_types/_character_memories.info` | Memory participants, descriptions, and duration |

The installed RICE reference uses historical aspiration modifiers, important actions, and events. Its Polabian content includes the sons of Gottschalk avenging their father; its Red Sea content includes the sons of Najah. These illustrate contextual goals but do not prove compatibility of this new system with RICE or every installed mod.
## Outstanding probes

The original capability questions are resolved by the versioned findings below, with these boundaries:

- Known-secret/public-death routes are verified; direct public exposure before a known-secret observation remains unsupported. No omniscient fallback.
- Original player/AI payer callbacks, reservation and exact-token ownership are verified for the explicit recovery construction pool; holder substitution is insufficient.
- Native numeric dates, declaration/review/deadline boundaries and actual shared save/load/switch behavior were measured in Tasks 2/4; combined family procedures remain separately identified.
- Core and family event-held references and later-frame stale rendering have scoped measured/UI coverage; bounded native Trigger Localization notices are disclosed separately.
- Native death, prison, relation, construction and title callbacks are verified through registered fixtures and separate actual actions. Natural-session observations do not certify every siege/raid/war combination.

The initial repository-bootstrap task did not launch CK3 or pass a native gameplay fixture. Later automation findings are documented below; they do not certify unrelated gameplay. Durable findings include game version, game-relative source reference, probe and observed result. Machine paths, saves, backups, logs, screenshots and transient attempts belong in ignored `.local/MODLOG.md`.

## Verified console-file automation — CK3 1.20.0.4 Crozier

A real one-command smoke ran three fresh owned processes from the same disposable baseline, measured its private counter 0→7 once despite replaying request 3, and observed native `current_date` 430243→430244 after `tick_day 1`. These are automation fixture findings; Task 2 core gameplay was accepted separately through the later core-regression and UI/save-load evidence.

Installed `game/_commandline_options.info` documents `-loadsave=<name>`. On this host an absolute baseline path was rejected with `Could not load save game`; placing a uniquely named disposable `.ck3` copy under selected user-data `save games/` and supplying its filename loaded directly into the intended paused campaign. `-suppress_error_log` prevents auto-opening the log and still writes error.log. No menu navigation is needed between repeated launches.

`run asp_automation_request.txt` reads that owned filename from the user-data `run/` directory. Fresh debug.log records `Running console command: run ...`, then native effects. UTF-8 BOM is required for request and authored native TXT/YML bytes on this engine. The current/root scope of the run file was the player character, but debug localization via ROOT getters produced empty fields; `GetPlayer.MakeScope.Var('variable').GetValue|0` emitted measured integer values. Installed effects docs explicitly support localized `debug_log` strings, and vanilla English localization contains this player-variable getter pattern.

Console effect description generation evaluates conditions before setters in the same request execute. Capture/initialize the next request during bootstrap and guard absent variables before comparisons. Documented native `hidden_effect` hides internal descriptions but still evaluates conditions; it alone does not prevent premature reads. Native completion for day advancement is a delayed hidden event with saved session/request identity, and the Python side waits for matching ACK before the bounded `tick_day` command. A requested number alone is never completion evidence.

One tick generated tens of thousands of unrelated native debug lines. Bound the retained partial record and drain complete lines in chunks; rejecting the whole batch for being large loses valid terminal telemetry. Rotation/truncation must fail rather than silently accepting old logs. Console-only fixture use can produce static unused-variable/flag diagnostics; retain and classify those separately from actual namespace Script system errors and baseline vanilla religion-on-action errors.


## Task 2 story and calendar capability probes — CK3 1.20.0.4 Crozier

Generated script docs in the disposable test record show `is_landed` requires a county or barony; `is_ruler` alone also accepts landless title holders. The core reservation guard uses both predicates. Engine acceptance of the complete eligibility path still requires a negative in-game case.

A direct `create_story` saved reference survived an event option and actual native save/load. In the loaded campaign, a one-day tick changed the numeric `current_date` delta by exactly one while retaining the captured target, origin, next review and timed-variable state. Native serialized durations for `months = 24` and `years = 8` were 720 and 2920 days. The core stores origin and next review as numeric date values using these measured initial durations. Full scheduled-review and pledge boundary behavior remains assigned to Task 4.

The scope/calendar probe emitted `ASP_PROBE CORE EVENT_SCOPE PASS`, `CALENDAR_DAY PASS`, and `SAVE_LOAD_STATE PASS` in the recorded fresh intervals. These markers prove the primitive capabilities, not C01–C04 core gameplay. Task 2 later verified UI presentation, terminal callbacks, class caps, stale-action protection and real core-instance reload through the fixtures and evidence listed in the Task 2 report. Full P01 review and pledge boundaries remain Task 4.

Automation safety review found real-profile `game.autosave=YEARLY`; October1→2 smoke does not certify autosave behavior across arbitrary boundaries. The runner now uses a read-only structural preflight requiring `NO_AUTOSAVE` and actual redirected Windows Documents user data before launch. It has no verified alternate-profile flag and does not automatically edit settings. Keep any short-test preference backup/restoration targeted to this field; never probe preservation by overwriting real autosaves.

CK3 1.20.0.4 native Settings → Game → Autosave Interval → No Autosave persists `game.autosave.value="NO_AUTOSAVE"`. `NEVER` is not a valid enum: debug.log reports a fallback to YEARLY. Automation checks the accepted enum before launch, after startup and before input, including retained-session day advancement. Keep the preference disabled until the owned game closes, then restore only the captured original field.

## Task 2 native story-card localization — CK3 1.20.0.4 Crozier

The visible `asp_core_debug` story cycle rendered its name from `asp_core_debug` and also requested the implicit `asp_core_debug_desc` key in the Situations story card. A separate `visualization.custom_string_key` supplied card body text but did not replace this implicit description; without the key, the card displayed the raw identifier even though `error.log` had no missing-localization line. Dev fixture localization now defines both keys. `tools/game_runner/tests/test_core_fixture_localization.py` checks the static contract; a native card screenshot remains necessary to verify rendering. New family story cycles must define their matching `<type>_desc` key.

## Vengeance knowledge and terminal evidence — CK3 1.20.0.4

The native Task 3 four-case probe validates explicit public `death_duel` responsibility and a matched known murder secret. Generated trigger documentation provides `any_known_secret`, `secret_type` and secret-scope `is_known_by`; event targets provide `secret_owner` and `secret_target`. A raw `killer` reference is not a knowledge gate. `common/deathreasons/_death_reasons.info` documents `public_knowledge=yes`; the conservative supported public causes are listed in the family trigger and retain that native property.

Native `secret_murder:on_discover` adds killer knowledge; `reveal_to` makes the matched secret queryable by the owner. Native exposure removes it from `any_known_secret` even though the same-event secret scope still exists and vanilla sets killer public. No generic read-side public-killer predicate or additive disclosure hook was found in generated documentation. Do not override `secret_murder` or guess from a murderer trait/opinion. Retain only post-activation bereavement victim references and check matched known secrets later; direct exposure before observation remains an explicit prototype gap.

The native death child receives the dying character and `scope:killer`; the fixture observed both while processing the scripted death request. Responsibility is recorded only for the exact existing target and exact story owner, then personal fulfillment is checked before unrelated-death closure. Native `on_imprison` receives the new prisoner in ROOT and `scope:imprisoner`; the callback and a refreshed custody predicate agree. Player action stress belongs to vanilla: Task 3 measures the installed execution effect separately before applying only the aspiration -20.

Native `NOT` negates each enclosed trigger: `NOT = { exists = scope:killer scope:killer = this }` wrongly rejects every supplied killer. Use `NOT = { AND = { exists = scope:killer scope:killer = this } }` to exclude only owner culpability. Guard diagnostics and the registered V01/V05 regressions validated the distinction. Do not infer asynchronous delivery merely from an incomplete active log read; inspect the entire fresh interval before changing transport sequencing.

Task 3 also validates that `save_scope_value_as` transports numbers and booleans only. Passing a persisted flag variable produces wrong-type errors and wrong terminal descriptions. Encode event-held outcome as small numeric values and accountability as a boolean; keep the persisted core/family flags unchanged. Registered V01-V03 assertions verify the caller-visible terminal codes; custody resolves in a separate on-action chain, so V04 observes its exact memory/rewards and a separate visual callback validates that event description.

The story-cycle info file describes a `STORY` display scope, but actual native localization uses the case-sensitive GUI getter `Story.MakeScope`, confirmed by installed `debug_story_test_event_l_english.yml` and the El Cid story. Uppercase STORY produced visible ERROR expressions and data-factory errors during actual story-card inspection; retain that failure and recapture the corrected native card. Story title and implicit `_desc` keys are both required.

## Task 4 verified timing and lifecycle presentation

The actual native Save Game boundary fixture serializes `months=12` as tick360, `years=3` as tick1095 and `years=5` as tick1825 in CK3 1.20.0.4. Together with Task 2’s720/2920 probes, these establish the numeric declaration/repeat/pledge defaults without assumptions about date-unit conversion. The shared boundary runner advances an actual native day and observes current_date+1, two due review latches, declaration eligibility and exact expiry at equality.

Core progress may destroy the current story. A later `if` or even a scope switch still requires a valid current object and produced invalid-story errors after `end_story`. Query the family’s terminal predicate first and make terminal dispatch the final effect; retain suspension through that branch so returning completed goals cannot receive rewards. Native friendship is removed by death: replacement preserves the qualifying bond captured by the original death hook and revalidates the remaining consumed cause, rather than re-querying that dead relation.

Native scope presence localization uses `Var('name').IsSet`; `MakeScope.HasVariable` is not a data-system function. Dynamic deadline text needs its native story/event context: direct declared descriptions and story-compatible `customizable_localization` follow installed `CompositionTypeAll`/`Story.Custom` patterns. Native event option ownership descriptions use `custom_description` with authored text; hidden internal validation does not grant an action to a stale story. Native creation references must be optional during tooltip description evaluation because `create_story` has not executed there. Preserve and recapture actual render/hover evidence; static identifier validity alone is insufficient.

Native tooltip evaluation can revisit an ended weak story after the effect frame completes. A direct same-frame predicate check does not prove that render path. Story-local conditional guards and a missing-target existence false branch both failed during real later-frame rendering; the validated event-character guard is described below. Dead characters do not support variable writes; capture their supported Prestige/Stress getters on a live character and require both snapshot variables before comparisons.


### Ended Story event rendering (CK3 1.20.0.4)

Native tooltip construction can visit a weak ended Story even through an optional `?=` scope and despite earlier false predicates in the same group. A Story-local `trigger_if` is itself an untyped trigger requiring a valid Story; changing its false branch from `always = no` to an existence test does not protect the tooltip traversal. Validate the event-held link inside `trigger_if` on the live event character before entering any family predicate. Preserve exact ownership checks inside the successful branch. Shared lifecycle P02/P05 test live and ended character-context guards; a later-frame real stale-modal hover and fresh startup/action logs remain required evidence.

Use native `fallback = yes` on an existing Close option to guarantee a harmless way out when queued origin interpretations have all become invalid. It avoids competing existence checks over an expiring Story. Installed reference examples are `events/decisions_events/roman_restoration_events.txt` (`roman_restoration.0002.e`) and `events/secret_events/secrets_events.txt` (`secrets.1001.option_fallback`). The final shared entrypoint/render interval verifies no no-valid-options or weak-scope error. Preserve UTF-8 BOM explicitly when editing native text; a misdecoded BOM can invalidate a top-level trigger definition while static brace balance still passes.


## Recovery attribution and reservation — CK3 1.20.0.4

Installed construction on_actions expose the original payer in `scope:character`; native fallback may substitute the holding owner afterward. An additive child retains the original scope: actual player and AI purchases supplied the payer, while script-created construction supplied none despite the fallback. Capture and verify original identity; never infer payment from holder. The dedicated AI probe omitted `-disable_ai`, prepared a legal vacancy/funds and required both a real engine start callback and resource decrease. The deterministic runner retains `-disable_ai`.

Start/cancel/complete callbacks do not supply a stable construction transaction identifier. Allocate a monotonic Province start serial, snapshot supported category levels and legal prerequisites, and clear old tokens on every start/cancellation/title loss. Completion requires the same Province/serial/payer plus an eligible level increase. An actual GUI cancel/restart confirmed fresh callbacks; no reimbursement is needed.

Native generated trigger documentation states that `free_building_slots` counts ongoing construction. Actual GUI start reported slots0/ongoing1/payer-owner1 after reservation; strict origin legality was false and originally prevented tracking. Origin still requires a slot for new categories. Native start tracking skips that already-consumed slot check while retaining holding/government/terrain/innovation/category predicates. Registered native child-on_action slot0 RED/GREEN and an actual paid GUI retest verify this distinction.

Native title-loss `scope:transfer_type = flag:granted` was observed during actual GUI Grant. Only that exact cause is voluntary; conquest, other and missing causes conservatively close impossible/free. Typed registered transfers exercise enum policy and reacquisition invalidation; they are not a real lost-war playthrough. Siege/raid child hooks use `on_siege_completion` and `on_raid_action_completion` without replacing vanilla hooks.

The prototype mirrors only Tribal Markets/Palisades1–2 and Pastures/Cereal Fields/Hill Farms1 prerequisites from installed native building definitions. Legal availability excludes treasury sufficiency: this long-term ambition can precede saving funds. Native costs/discounts remain authoritative. Actual paid start/finish used bounded `instabuild` acceleration; ordinary construction duration was not certified. Later-frame management retains Task4's bounded ten Trigger Localization(database/dynamic) notices with harmless dismissal and no other aspiration runtime/parser/data errors.


## Personal bonds and native pursuit — CK3 1.20.0.4

Native Befriend eligibility is evaluated in owner character scope with the exact target: `can_use_befriend_scheme_trigger` plus `can_start_scheme`. The registered control rejects a locked Befriend route and accepts it after a test-only perk unlock. Seduce uses mutual `is_attracted_to_gender_of` and native `can_start_scheme`, preserving scheme capacity, target and romantic restrictions. Native source references are `common/scripted_triggers/00_scheme_triggers.txt`, `common/schemes/scheme_types/befriend_scheme.txt`, `common/schemes/scheme_types/seduce_scheme.txt` and their character interactions; source inspection alone is not actual player-action proof.

Current court/guest and positive relation contexts can be observed truthfully without an invented encounter. An invisible owner-private context Story retains a signature, serial and consumed serial, separately from core aspiration slots. Repeated observation of an unchanged signature does not renew it; actual court join/leave callbacks mark the signature stale. The registered routine fixture verifies unchanged observation and consumption, exact occupancy chances and cooldown, not natural emergence statistics.

The real Task 6 native Befriend action was chosen and confirmed through its ordinary interaction against the exact prepared acquaintance. Dev acceleration first required that matching existing scheme, then added100 native progress units per call. Four calls advanced the accepted11-month scheme; two actual native days later, the vanilla Kindred Minds outcome produced Friend and ended the scheme. Aspiration closure measured−10 Stress/+50 Diplomacy XP with the exact target memory. Generated contact, Potential Friend and perk were setup; progress and day advancement were acceleration, not ordinary scheme duration or a naturally occurring acquaintance. A scripted relationship setter is insufficient for this action acceptance.

Origin/rival release tooltips require their event-held context. Reusing management's `asp_selected_story` getter in an origin produced DataFactory errors. Own origin/rival text now previews native-modified base5 Stress and states the24-month free-release rule without reading that absent management Story. Registered localization checks reproduce the wrong-getter boundary, while actual render/hover establishes English presentation (base5 versus measured native6 in the control).

Native `fallback=yes` Close guarantees valid dismissal after origin/rival regular choices become stale; this UI also rendered Return alongside valid choices. The Return itself keeps the existing desire and grants no reward. A later-frame exact retired-origin hover/close had zero fresh errors. Exact retired-management Release input changed no resources; its fresh interval contained only the previously bounded ten Trigger Localization notices, with no DataFactory, argument, weak-Story/link or no-valid-options error. Those actual errors must fail regression acceptance even when state stayed unchanged.

Task6 confirms the implicit visible Story title/description requirement in native Situations: `asp_personal_bond_story` and `asp_personal_bond_story_desc` plus the `Story.MakeScope` body render the exact contact and age/review. Missing implicit keys can show raw identifiers without an error-log line; an exact-key regression and actual render are both required.

## Combined native presentation and mixed targets — CK3 1.20.0.4

Native tooltip generation does not short-circuit adjacent filter predicates. Enumerating all owned Stories in replacement cause validation can visit invisible bond context Stories without aspiration fields, or compare a recovery Title target against a vengeance Character target despite a false adjacent family condition. Use explicit native trigger_if schema presence, then exact family, with false trigger_else branches before reading aspiration identity/target. Registered combined mixed-cap RED/GREEN and valid/distinct versus duplicate target checks cover that route. This does not replace the live-event-character guards around weak ended Story links.

Suspended public fulfillment retains persisted fulfilled state and zero Prestige economics, but transports numeric event result5 for the withheld-reward narrative. Character and county settlements both explicitly state no retrospective rewards; ordinary result1 still grants100 Prestige. Actual mixed-family return screenshots and measured zero-resource/memory checks establish the presentation separately from scripted transport.

Personal-bond cards use existing Story.Custom composition in the native Story context to render the selected Friend/Best Friend or Lover/Soulmate condition. Story.MakeScope retains exact target, age and review. Both native mode frames and focused implicit-key/branch checks are required; no gameplay mode or reward changes are implied by this presentation correction.

## Release-only ordinary campaign — CK3 1.20.0.4

A fresh character-of-the-week campaign began on 1 October 1178 with only the packaged release mod, AI and ordinary selection enabled. By 19 September 1182, native Situations showed three active Stories: romantic desires concerning Ina and Salimata and a custody-oriented vengeance ambition concerning the player's brother Bello and known battle killer Sakoura. An initial Ina offer appeared 6 October 1178; a Fadima offer on 6 October 1179 was declined and produced its memory event; Salimata was kept on 6 October 1180. Bello's battle death on 21 April 1180 added 25 native Stress and opened the vengeance interpretation the next day. Ina's scheduled reviews appeared in September 1180, 1181 and 1182, with the player retaining the desire. Final Stress was 31/300. No debug fixture, forced goal, accelerated scheme or cadence change was used in this campaign.

This is one observed ruler and roughly four game years, not a frequency estimate or proof that every eligible context fires. The release launch mounted the manual mod and loaded the native event namespaces. Its error log contains 32 startup unused-variable/event-target warnings with `asp_` names at 16:12:39–40 and no later `asp_` lines; numerous unrelated vanilla/DLC script errors remain in the aggregate log. Do not treat the aggregate log as error-free or the startup warnings as runtime failures of the observed aspirations.

# Personal-bond context, native pursuit and relationship evidence

Status: measured-native scripted controls and actual accelerated Befriend; source-inspected Seduce route.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

Native Befriend eligibility is evaluated in owner character scope with the exact target: `can_use_befriend_scheme_trigger` plus `can_start_scheme`. The registered control rejects a locked Befriend route and accepts it after a test-only perk unlock. Seduce uses mutual `is_attracted_to_gender_of` and native `can_start_scheme`, preserving scheme capacity, target and romantic restrictions. Native source references are `common/scripted_triggers/00_scheme_triggers.txt`, `common/schemes/scheme_types/befriend_scheme.txt`, `common/schemes/scheme_types/seduce_scheme.txt` and their character interactions; source inspection alone is not actual player-action proof.

Current court/guest and positive relation contexts can be observed truthfully without an invented encounter. An invisible owner-private context Story retains a signature, serial and consumed serial, separately from core aspiration slots. Repeated observation of an unchanged signature does not renew it; actual court join/leave callbacks mark the signature stale. The registered routine fixture verifies unchanged observation and consumption, exact occupancy chances and cooldown, not natural emergence statistics.

The real Task 6 native Befriend action was chosen and confirmed through its ordinary interaction against the exact prepared acquaintance. Dev acceleration first required that matching existing scheme, then added100 native progress units per call. Four calls advanced the accepted11-month scheme; two actual native days later, the vanilla Kindred Minds outcome produced Friend and ended the scheme. Aspiration closure measured−10 Stress/+50 Diplomacy XP with the exact target memory. Generated contact, Potential Friend and perk were setup; progress and day advancement were acceleration, not ordinary scheme duration or a naturally occurring acquaintance. A scripted relationship setter is insufficient for this action acceptance.

Origin/rival release tooltips require their event-held context. Reusing management's `asp_selected_story` getter in an origin produced DataFactory errors. Own origin/rival text now previews native-modified base5 Stress and states the24-month free-release rule without reading that absent management Story. Registered localization checks reproduce the wrong-getter boundary, while actual render/hover establishes English presentation (base5 versus measured native6 in the control).

Native `fallback=yes` Close guarantees valid dismissal after origin/rival regular choices become stale; this UI also rendered Return alongside valid choices. The Return itself keeps the existing desire and grants no reward. A later-frame exact retired-origin hover/close had zero fresh errors. Exact retired-management Release input changed no resources; its fresh interval contained only the previously bounded ten Trigger Localization notices, with no DataFactory, argument, weak-Story/link or no-valid-options error. Those actual errors must fail regression acceptance even when state stayed unchanged.

Task6 confirms the implicit visible Story title/description requirement in native Situations: `asp_personal_bond_story` and `asp_personal_bond_story_desc` plus the `Story.MakeScope` body render the exact contact and age/review. Missing implicit keys can show raw identifiers without an error-log line; an exact-key regression and actual render are both required.

## Evidence and reproduction

[Bond contract](../../src/stories/personal_bond/SPEC.md#implemented-contextual-selection-and-limited-pursuit-routes), [B01-B07 and mandatory actual Befriend](../../src/stories/personal_bond/tests/scenarios.md), [context/pursuit predicates](../../src/stories/personal_bond/game/common/scripted_triggers/asp_personal_bond.txt), [native context/relationship hooks](../../src/stories/personal_bond/game/common/on_action/asp_personal_bond.txt), [fixture and matching-scheme acceleration](../../src/stories/personal_bond/tests/game/common/scripted_effects/asp_personal_bond_test.txt), [render/action setup](../../src/stories/personal_bond/tests/game/events/asp_personal_bond_debug_events.txt) and [localization boundaries](../../tools/game_runner/tests/test_bond_localization.py). Run registered `bond-regression`; then perform the actual Befriend and later-frame procedures. Successful two-way reinterpretation is registered B07 with identity/consumption/resource delta controls.

## Implication

Check native pursuit against the exact target without granting access. Keep context signatures/serials owner-private and consume unchanged contexts once. Preserve target/origin/instance through reinterpretation. Actual relationship-action acceptance needs a confirmed exact native scheme before progress acceleration; setting a relation directly is insufficient.

## Limits

Contact/perk/Potential Friend were controlled setup; the actual accepted scheme was accelerated and needed two subsequent native days. This does not prove ordinary duration, natural emergence statistics or a natural acquaintance. Seduce predicates/source inspection do not certify a played Seduce. Scripted reinterpretation is not actual reinterpretation input or elapsed review time. Bond-specific actual save/load and real player-switch coverage remain separately bounded.

[Knowledge index](README.md)

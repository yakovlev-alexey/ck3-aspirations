# Culprit knowledge, native death responsibility and disclosure limits

Status: measured-native (supported public/known-secret routes); unsupported (direct exposure before observation).

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

The native Task 3 four-case probe validates explicit public `death_duel` responsibility and a matched known murder secret. Generated trigger documentation provides `any_known_secret`, `secret_type` and secret-scope `is_known_by`; event targets provide `secret_owner` and `secret_target`. A raw `killer` reference is not a knowledge gate. `common/deathreasons/_death_reasons.info` documents `public_knowledge=yes`; the conservative supported public causes are listed in the family trigger and retain that native property.

Native `secret_murder:on_discover` adds killer knowledge; `reveal_to` makes the matched secret queryable by the owner. Native exposure removes it from `any_known_secret` even though the same-event secret scope still exists and vanilla sets killer public. No generic read-side public-killer predicate or additive disclosure hook was found in generated documentation. Do not override `secret_murder` or guess from a murderer trait/opinion. Retain only post-activation bereavement victim references and check matched known secrets later; direct exposure before observation remains an explicit prototype gap.

The native death child receives the dying character and `scope:killer`; the fixture observed both while processing the scripted death request. Responsibility is recorded only for the exact existing target and exact story owner, then personal fulfillment is checked before unrelated-death closure. Native `on_imprison` receives the new prisoner in ROOT and `scope:imprisoner`; the callback and a refreshed custody predicate agree. Player action stress belongs to vanilla: Task 3 measures the installed execution effect separately before applying only the aspiration -20.

Native `NOT` negates each enclosed trigger: `NOT = { exists = scope:killer scope:killer = this }` wrongly rejects every supplied killer. Use `NOT = { AND = { exists = scope:killer scope:killer = this } }` to exclude only owner culpability. Guard diagnostics and the registered V01/V05 regressions validated the distinction. Do not infer asynchronous delivery merely from an incomplete active log read; inspect the entire fresh interval before changing transport sequencing.

## Evidence and reproduction

[Vengeance contract](../../src/stories/vengeance/SPEC.md#task-3-stable-event-allocations), [V01-V08 scenarios and actual Execute](../../src/stories/vengeance/tests/scenarios.md), [knowledge/eligibility triggers](../../src/stories/vengeance/game/common/scripted_triggers/asp_vengeance.txt), [native callback hooks](../../src/stories/vengeance/game/common/on_action/asp_vengeance.txt), [four-case knowledge probe](../../src/stories/vengeance/tests/game/events/asp_vengeance_debug_events.txt), [registered V01-V06 effects](../../src/stories/vengeance/tests/game/common/scripted_effects/asp_vengeance_test.txt) and [reporter negative controls](../../tools/game_runner/tests/test_vengeance_runner.py). Installed references are `common/deathreasons/_death_reasons.info`, native death on-actions and `secret_murder` discover/exposure effects. Run registered `vengeance-regression`; actual Execute/render remains separate.

## Implication

Require the exact victim/known culprit connection and owner responsibility; keep pending records limited to post-activation observed victims. Evaluate owner-attributed fulfillment before generic target death. Gate public recognition separately from private knowledge. Negate the conjunction when excluding only owner culpability.

## Limits

A raw killer scope is not character knowledge. Source documentation exposed no general public-killer read predicate/additive disclosure hook for this version. Exposure before a known-secret observation can be missed; do not invent omniscient fallback, infer guilt from traits/opinion or override vanilla secret_murder. Scripted execute logic preserves vanilla costs but actual UI acceptance has its own procedure.

[Knowledge index](README.md)

# Release-only ordinary campaign observation

Status: measured-native single campaign observation.

CK3 version: 1.20.0.4 (Crozier). Findings migrated from the existing validated project notes; this migration performed no new live probe.

## Observation

A fresh character-of-the-week campaign began on 1 October 1178 with only the packaged release mod, AI and ordinary selection enabled. By 19 September 1182, native Situations showed three active Stories: romantic desires concerning Ina and Salimata and a custody-oriented vengeance ambition concerning the player's brother Bello and known battle killer Sakoura. An initial Ina offer appeared 6 October 1178; a Fadima offer on 6 October 1179 was declined and produced its memory event; Salimata was kept on 6 October 1180. Bello's battle death on 21 April 1180 added 25 native Stress and opened the vengeance interpretation the next day. Ina's scheduled reviews appeared in September 1180, 1181 and 1182, with the player retaining the desire. Final Stress was 31/300. No debug fixture, forced goal, accelerated scheme or cadence change was used in this campaign.

This is one observed ruler and roughly four game years, not a frequency estimate or proof that every eligible context fires. The release launch mounted the manual mod and loaded the native event namespaces. Its error log contains 32 startup unused-variable/event-target warnings with `asp_` names at 16:12:39–40 and no later `asp_` lines; numerous unrelated vanilla/DLC script errors remain in the aggregate log. Do not treat the aggregate log as error-free or the startup warnings as runtime failures of the observed aspirations.

## Evidence and reproduction

[Combined I03 procedure](../../src/core/tests/scenarios.md#task-7-combined-registered-and-actual-acceptance), [design acceptance](../design.md#verification-and-acceptance) and [release packaging rules](../repository.md). Reproduction means a fresh release-only campaign with AI/ordinary selection, recorded game duration/incidents/choices/occupancy/resources and fresh startup-versus-runtime diagnostics; it does not require identical random events.

## Implication

Ordinary campaign observations supplement registered forced-input regressions and show that contextual goals can coexist under normal play. Record selection and rejected offers as well as successes, and classify startup warnings separately from action errors.

## Limits

One ruler and roughly four game years is not a frequency estimate, balance conclusion, all-callback acceptance or multi-mod/DLC compatibility test. Aggregate logs contained unrelated vanilla/DLC errors and 32 startup aspiration unused-state warnings; do not call the aggregate log error-free. Historical runtime artifacts remain ignored; the tracked procedure makes the observation reproducible without preserving a machine path.

[Knowledge index](README.md)

# Engine-aware static validation

Status: source-inspected tooling/contracts; observed xTiger CLI diagnostics. No new
native gameplay or rendering probe was performed for this integration.

CK3 version: installed 1.20.1 (Crozier). Validator: 9mirx0r/xTiger v1.5.9-alpha,
whose release targets CK3 1.20.0.4 and whose CLI tables identify 1.20.0. Both exact
versions are retained in local validation evidence; the patch warning is not hidden.

## Observation

The pinned CLI can return exit 0 while its JSON includes diagnostics. The project's
quality command must parse diagnostic severity independently of native process success.
Fatal/Error fail by default; Warning fails with `-FailOnWarning`. Invalid/empty JSON
and native execution failure never mean that the mod is clean. Regression fixtures
exercise these outcomes independently of xTiger's own validation rules.

Real profile validation reported a scope deduction conflict for `var:asp_target` in
recovery scripted effects/triggers: xTiger inferred Character while the recovery code
used Landed Title. The project's living contracts intentionally share this persisted
field across unlike family targets: vengeance and bonds use characters; recovery uses
a county title. This diagnostic is a limitation of the inferred shared variable type,
not proof that the persisted field should be renamed or that family checks can be
removed. Native family/lifecycle acceptance remains authoritative.

xTiger also reports missing script UTF-8 BOM as an encoding Warning. The assembly
checker requires BOM for localization and rejects corrupt/duplicate script BOMs, but
does not require BOM on every native script. The general encoding checks therefore
overlap only partially. Preserve the project's authored native encoding conventions.

## Evidence and reproduction

Use the pinned [release metadata](../../tools/xtiger/release.json),
[explicit validator config](../../tools/xtiger/ck3-tiger.conf) and
[real profile commands](../quality.md#install-and-run). Build and check both profiles
against the installed read-only vanilla root; retain raw JSON and stderr. The
[core initialization](../../src/core/game/common/scripted_effects/asp_core.txt),
[recovery effects](../../src/stories/holding_recovery/game/common/scripted_effects/asp_recovery.txt)
and [recovery triggers](../../src/stories/holding_recovery/game/common/scripted_triggers/asp_recovery.txt)
are portable inputs for the shared-target deduction report. The
[core](../../src/core/SPEC.md), [recovery](../../src/stories/holding_recovery/SPEC.md)
and [vengeance](../../src/stories/vengeance/SPEC.md) contracts own target meaning.

[X01-X11 boundary scenarios](../../tools/tests/scenarios.md) and their
[fixtures](../../tools/tests/xtiger.ps1) establish wrapper policy, hash/provenance,
archive and transport behavior. They do not test xTiger's scope inference or certify
native semantics. [The existing assembly checker](../../tools/Aspirations.Build.psm1)
owns the focused BOM/encoding policy; CK3 logs and rendering remain separate evidence.

## Implication

Use xTiger as an additional static check of assembled profiles and vanilla references.
Keep all existing assembly, project acceptance, targeted localization and gameplay
checks. Review shared-target reports with the owning family contract and native
evidence. The project config retains diagnostics without blanket scope overrides or
baseline suppression. A zero-error default-policy pass may still contain warnings.

## Limits

An alpha validator's inferred type is neither a CK3 runtime observation nor proof of
tooltip short-circuit behavior. Static checks cannot establish rewards, actual dates,
save/load identity or later-frame rendering. These observations concern the pinned
release and named source patterns; reevaluate diagnostics after validator/game changes.

[Knowledge index](README.md)

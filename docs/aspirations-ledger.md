# Aspirations ledger

A compact catalog of implemented aspiration families. Story keys are the stable family identifiers used by core and `src/stories/<key>/`. Each key links to its owning specification, which remains authoritative for exact behavior.

| Story key | Short description | Trigger conditions | Land status | Governments |
| --- | --- | --- | --- | --- |
| [vengeance](../src/stories/vengeance/SPEC.md) | Avenge a loved one or hold the culprit accountable. | Observed killing of a parent, child, sibling, spouse, friend or best friend; victim was not a rival/nemesis. Owner did not cause the killing. Known culprit is alive, distinct from the owner and within diplomatic range. | `landed` | `all` |
| [holding_recovery](../src/stories/holding_recovery/SPEC.md) | Restore a personally held county after enemy damage. | Observed enemy siege/raid in a personally held county; Control below 70; at least one legal supported construction/upgrade in a personally held holding, with no ongoing work there. Affordability is not required. | `landed` | `all` |
| [personal_bond](../src/stories/personal_bond/SPEC.md) | Seek friendship or romantic closeness with a known person. | Quarterly selection of a reachable living adult courtier/guest or existing positive relation; fresh unconsumed connection context; desired relationship absent; native Befriend or mutually attracted Seduce route available; routine cooldown elapsed. | `landed` | `all` |

## Filter notation

- **Land status:** `landed`, `landless`, or `all`. This is separate from government type.
- **Governments:** `all`, or comma-separated tags such as `feudal`, `clan`, `tribal`, `admin` (administrative) and `nomadic`. Add other government tags when a story needs them.
- Multiple tags in one cell mean **any listed value**. The two filter columns and trigger conditions must **all** match. Use `all` alone when that column has no restriction.
- For example, Land status `all` with Governments `feudal, tribal` matches either listed government without a land-status restriction. Land status `landless` with Governments `all` matches landless characters of any government.

These are documentation filters, not executable CK3 predicates. `all` does not bypass shared eligibility or native action/building prerequisites, and it does not certify compatibility. Recovery still checks the supported buildings' government, holding, terrain and innovation requirements.

## Shared eligibility and selection

All current families require a living adult landed current player ruler; landless emergence is excluded by the implementation. Government-specific compatibility beyond the documented prototype coverage remains unverified. See the [core contract](../src/core/SPEC.md) and [coverage limits](../README.md#prototype-coverage-and-limits).

Trigger conditions describe eligibility for an offer, not guaranteed creation. Capacity, duplicate family/target prevention, consumed incident/context guards, cooldowns and weighted selection still apply. Major incidents at full ambition capacity can offer explicit replacement; routine bond selection cannot.

## Maintenance

Keep one row per family and update it alongside changes to that family's eligibility or origin. Keep descriptions and triggers short; detailed interpretations, objectives, lifecycle and regression coverage belong in the linked SPEC and acceptance scenarios. Add a new row when a family is implemented; keep proposals explicitly labeled separately from this implemented catalog.

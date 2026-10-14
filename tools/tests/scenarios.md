# Tooling acceptance scenarios

Run `pwsh -NoProfile -File tools/tests/run.ps1`. No additional test framework is needed.
T01-T24 cover deterministic assembly, metadata, profile separation, path/reparse safety,
local registration, archives and rebuild ownership. K01-K17 cover shared acceptance
references, portable knowledge links and visible Story localization keys.

## xTiger integration

The suite runs [xTiger boundary fixtures](xtiger.ps1) in disposable repository roots.
It substitutes only the external validator for report-policy cases; X10 uses real
PowerShell subprocesses. These tests do not certify the third-party validation engine
or gameplay. The separately installed pinned xTiger must also check actual dev/release
output using [the documented commands](../../docs/quality.md).

| ID | Boundary | Required result |
| --- | --- | --- |
| X01 | Integration entry point | Module imports successfully |
| X02 | Empty diagnostics and dev/release selection | Pass; exact descriptor/game/config arguments, unsuppressed JSON, game version and manifest provenance retained |
| X03 | Native exit 0 with Error/Fatal diagnostics | Fail quality policy and count reports |
| X04 | Warning/Tips/Untidy diagnostics | Warnings fail only with strict policy; advice remains nonblocking |
| X05 | Empty/malformed JSON, wrong envelope or unknown severity | Fail closed, never count as a clean validation |
| X06 | Nonzero native exit with an empty array | Fail execution |
| X07 | Source changed since build | Stop before any validator invocation |
| X08 | Untrusted archive | Reject bad SHA-256 or traversal before extraction; verified archive installs only the validator |
| X09 | Junction beneath local output | Reject before writing outside the repository |
| X10 | Native transport and timeout | Preserve separate stdout/stderr and exit status; stop the owned timed-out process |
| X11 | Validator/config changes during analysis | Reject replacement input hashes rather than claim valid provenance |

Real validation is static evidence only. Native scenarios, measured resource deltas,
fresh game logs, actual save/load and screenshots remain necessary for gameplay.

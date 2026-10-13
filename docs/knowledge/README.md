# CK3 knowledge index

Read the relevant topic before implementing or testing against a CK3 capability. These notes preserve versioned discoveries from the original modding notes; [design](../design.md), [core SPEC](../../src/core/SPEC.md) and family SPECs own gameplay. [Story acceptance](../story-authoring.md) owns the shared review checklist.

| Topic | Read when | Status and boundary |
| --- | --- | --- |
| [Native sources](sources.md) | Selecting engine hooks or reference content | Source-inspected; capability presence is not runtime correctness |
| [Construction attribution and tokens](construction.md) | Recovery starts, cancellation, completion or title loss | Measured native callbacks/UI plus scripted reservation/token controls; explicit construction pool only |
| [Story scopes and localization](scopes-localization.md) | Event-held references, card text, weak Story links or mixed targets | Measured rendering and source/regression controls; later-frame evidence remains necessary |
| [Calendar and lifecycle](calendar-lifecycle.md) | Dates, review, expiry, suspension, return or terminal ordering | Measured numeric durations and registered/native procedures; artificial timestamps remain disclosed |
| [Murder knowledge](murder-knowledge.md) | Culprit eligibility, disclosure or owner responsibility | Supported public/known-secret routes measured; exposure before observation remains unsupported |
| [Personal bonds](personal-bonds.md) | Context consumption, pursuit availability or actual Befriend | Measured scripted/native action boundaries; no natural frequency or ordinary-duration guarantee |
| [Automation, profiles and DPI](automation-profile.md) | Launching, log transport, ownership, profile changes or coordinates | Measured launch/profile behavior; Windows/DPI source inspection is labeled separately |
| [Ordinary campaign](ordinary-campaign.md) | Interpreting natural emergence evidence | One measured release-only campaign; no statistical or compatibility certification |

## Evidence and update rules

Each topic records **Status**, **CK3 version**, **Observation**, **Evidence and reproduction**, **Implication** and **Limits**. Use `measured-native` for observed engine state/actions, `source-inspected` for inspected definitions/tooling, and `unsupported` or `unverified` for gaps; mixed notes label the different parts. Preserve earlier version results when a new engine version differs. Do not promote hypotheses to facts or silently broaden a scripted test into actual-input evidence.

Link tracked scenarios, fixtures, runtime implementation or precise installed-game-relative sources so another agent can reproduce the claim. Ignored historical logs/reports/screenshots may supplement the observation but cannot be its only portable reference. Keep raw runtime artifacts, saves, profiles, local paths and transient attempts in `.local/`; never copy them into this directory.

Update the relevant topic in the same change when a reusable discovery is validated. Add an index row only for a real new topic and reconcile conflicting earlier evidence explicitly. If a change produces no durable finding, state **No new durable finding** in its change/report; do not invent an entry. Search by symbol, hook or symptom with `rg` before adding another note. Example: `rg -n 'free_building_slots|scope:character|weak|NO_AUTOSAVE' docs/knowledge`.

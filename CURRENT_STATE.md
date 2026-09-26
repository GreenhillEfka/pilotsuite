# Current state — Alpha.37 candidate, 2026-09-27

Baseline main cbf43ccebdfb6244a73ed379335d80eca4c5db3e; live app Alpha.36 confirmed
at resume. RELEASE_STATE.json retains the last completed delivery, not this candidate.

## Implemented

WorldModel returns explicit frame acceptance. Rejected old/equal/duplicate/malformed
updates do not flow into learning; stale removals cannot delete a newer snapshot.
An accepted delayed presence activation can retain its activity evidence under the
existing consent/time rules. Light/lux values are withheld per channel when timestamps
are absent or newer than the event. No extra HA/recorder read, collection or schema.
Existing records are not rewritten; temporal consistency is not causality proof.

Workspace cards now show effective roles consistently, with derived defaults explicitly
labelled rather than silently stored. External comparison temperature is optional and
shown separately. Difference requires good independent readings and the same unit;
missing/disconnected data is unknown, never zero. The primary zone median is unchanged.

## Verification and boundaries

Local full compile/contracts/test-discovery plus 485 Python and 58 JavaScript tests
pass. New synthetic event regression reproduces old contamination and verifies normal,
delayed, missing-time and no-consent paths without HA writes. Existing actual-app
workspace tests now cover role provenance and valid/unavailable comparison readings.
Local browser navigation was administrator-blocked, not bypassed; remote CI pending.
No household edit, role/consent change, helper mutation or presence activation occurred.
No autonomous light, media or adaptive learner is claimed. Deployment is a separate gate.

## Direction

Presence is the common basis, followed by daylight-aware light, intended mood/color,
optional music with TV/manual priority, and bounded learning. Architecture and concrete
acceptance gates are in PRESENCE_FIRST_INTELLIGENCE.md. The user handles entity cleanup;
software tests remain synthetic. Next: one persistent presence kernel integrated with
explanation/replay, not another isolated planning contract. Productive rollout requires
explicit scope and verified no-conflict ownership after realistic fault tests.

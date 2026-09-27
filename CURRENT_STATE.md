# Current state — Alpha.48 live shadow candidate, 2026-09-27

Implements the approved presence-live-comparison and light-need package on the
existing presence kernel, lighting policy, WorldModel and ContextStore. No second
presence algorithm, database or HA execution route.

The initially read installed/source baseline was Alpha.46, main51a86351492b591f64c57a703d06fcb1137edaf7.
Existing PR102's cc9039377824b4702a1c2e2b39fee090f1bdf97e provenance correction and its
tests are preserved. Alpha47 was its reserved development version; the integrated
functional package uses Alpha48. Do not infer installation from candidate code.

## Functional scope

Explicit start/stop in Zonenmodule > Anwesenheit (also visible for lighting), confirmed
raw input modes, grace deadline, source report-age limit, chosen atmosphere, outdoor
lux declaration and bounded brightness parameters. HA status vs computed status,
reasons, source quality, deadline and non-executable light proposals are visible.

A local five-second worker and accepted source events advance the existing kernels.
Only the latest operational checkpoint is stored, without learner/history additions.
HA room status is never its own evidence. Unknown/derived sources cannot establish
vacancy; pulse-high levels cannot endlessly renew grace or prove clear after expiry.
Reconnect/restart preserves deadlines. Changes to bindings, identities or shared
revision suspend the session durably; explicit confirmation is required to resume.
Source timestamps are HA reports, not physical freshness certification. Held helper
and actuator states remain distinct from physical source measurements.

Existing roles, learning consent, evidence and ordinary HA automation ownership are
unchanged. Savepoints exclude operational shadow state. Metadata cleanup, repair
execution and productive control are not enabled by this package. No household
shadow activation, entity rename or test actuation was performed during development.

## Gates

Repository validation, current tests and the new live-shadow HTTP/store integration
suite must pass, plus all existing Chromium suites and the added shadow browser flow.
Local browser navigation was blocked by administrator policy and not bypassed.
Fresh scoped backup before publication; exact CI/source association and native update
follow RELEASE_RUNBOOK.md. RELEASE_STATE.json remains the last completed receipt.

Contract and remaining scope: docs/PRESENCE_SHADOW.md. After delivery, a user explicitly
configures a real-zone session; no runtime or synthetic check is household acceptance.

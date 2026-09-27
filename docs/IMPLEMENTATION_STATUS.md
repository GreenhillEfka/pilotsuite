# PilotSuite capability and acceptance ledger

## Alpha.48 candidate — real presence shadow / light need

| Capability | Scope |
|---|---|
| Live source input | Existing confirmed raw mappings, explicit pulse/continuous semantics |
| Room status comparison | HA status vs same-kernel PilotSuite state; no circular evidence |
| Deadline and explanation | Belegt/Nachlauf/Frei/Unklar with reasons, source age and generation |
| Background evaluation | Explicit start only; accepted events plus local 5-second tick |
| Persistence | Last checkpoint in ContextStore; no new learner, DB or history |
| Changed identity/revision | Durable suspension until explicitly confirmed again |
| Light need | Existing bounded policy, explicit outdoor lux/profile; proposals only |
| Held HA states | Logical helper/actuator values distinct from physical sensor report age |
| Stop / savepoint | Stop affects only shadow state; savepoints cannot activate it |
| Legacy execution / Apply | Remains closed; no household control or authority transfer |
| Existing provenance fix | PR102 functional correction and tests preserved |
| CI / installed acceptance | Candidate; completed receipt only after actual gated delivery |

All previous released functionality is retained. See PRESENCE_SHADOW.md for exact
limits, source assumptions and validation scope. Synthetic data and no-write tests do
not attest real sensors, household UI or broad automation safety. Local browser policy
was not changed. User-led entity cleanup remains independent.

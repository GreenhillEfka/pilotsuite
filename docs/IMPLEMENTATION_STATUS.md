# PilotSuite capability and acceptance ledger

## Installed Alpha.48 — 2026-09-27

Exact source, backup, installation and runtime evidence: RELEASE_STATE.json.
PR103 is delivered; PR102's historical-provenance fix is included and its PR merged.

| Capability | Delivered scope |
|---|---|
| Real shadow input | Confirmed independent raw sources; explicit pulse/continuous modes |
| HA comparison | Existing room status compared, never used as circular presence evidence |
| Presence | Belegt/Nachlauf/Frei/Unklar, reason, report age, generation and deadline |
| Lifecycle | Explicit per-zone start/stop; accepted events and local five-second worker |
| Persistence | Latest-only checkpoint in existing ContextStore; no new history/learner/schema |
| Recovery | Deadlines preserved; identity/revision changes durably suspend until reconfirmed |
| Light need | Chosen atmosphere, declared outdoor lux, bounded proposals and manual holds |
| Device/automation control | Not enabled; general Apply and legacy presence activation remain closed |
| Local validation | 555 Python / 60 JavaScript, 53 API contracts and release-preflight passed |
| Exact candidate/main CI | All four jobs and ten browser suites passed |
| UI evidence | Checksum-verified synthetic desktop/light and phone/dark screenshots reviewed |
| Installation | Alpha48 installed/offered/started, no update pending; options unchanged |
| Runtime | Exact Alpha48 startup, ready/stream/fresh/zone verified |
| Household shadow activation | None during development or deployment |
| Household UI/physical behavior | Not independently accepted; remains the next functional check |

Fresh a7c65d26 scoped backup was verified before publication. One Store refresh and
one update; no extra restart/rebuild, unrelated app, household config or consent change.
The earlier 2eb9a967 backup was also verified: despite its Alpha47 label it contains
Alpha46, not Alpha47. It was superseded for this deployment by fresh a7c65d26.

No automation takeover, technical-ID migration, new music/TV controller or adaptive
preference learner is claimed. Observe a user-confirmed session in Erdkellerbereich and
one unlike zone before extending authority. Documentation closure needs no redeployment.

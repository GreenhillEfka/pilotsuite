# PilotSuite capability and acceptance ledger

## Installed Alpha.28 — 2026-09-26

Exact receipt: RELEASE_STATE.json. PR63 is merged and delivered.

| Capability | Scope |
|---|---|
| Existing zones/roles/history/drafts | Retained; learning stays opt-in |
| Local savepoints/rescue/helper inspection | Alpha.27 behavior retained |
| Bounded helper executor | One current planned presence-delay timer per explicit confirmation |
| Existing matching timer | Exact config may be verified/reused; no inferred ownership |
| Conflicting/pre-existing helper | Stop; never overwrite/delete/adopt by name |
| Lost/timeout create response | Independent read-back; never blind retry |
| Rollback | Only positively confirmed same-transaction creation with absent pre-image |
| PlanStore | Durable helper transaction journal; no cross-system atomicity claim |
| Generic plan apply / automation takeover / actuators | Closed |
| Presence runtime / lighting / media / climate control | Not implemented |
| Candidate/main CI | All four jobs successful; 394 Python / 48 JS candidate tests |
| Runtime | Alpha.28 started, bounded_helper_provisioning, ready/stream/fresh/zone |
| Household helper creation during release | None |
| Authenticated household helper-path acceptance | Pending explicit in-app action |

Next: verify the bounded helper path in authenticated household Ingress without bypass,
then implement presence timing and restart/deadline reconciliation under Issue56.

# PilotSuite capability and acceptance ledger

## Alpha.34 candidate — trigger-ID integrity

- One pure bounded projection reused by inventory and routine details.
- Missing, partially matched, disabled, inactive and unknown ID references distinguished.
- Only structural paths/counts returned; raw private labels/configuration excluded.
- Explicit read-only review, safe text output, preserved local edits, no control/repair.
- Delivery and actual installation remain recorded separately in RELEASE_STATE.json.


## Installed Alpha.33 — 2026-09-26

PR 71, release 46ec340; exact source/CI/backup/runtime receipt: RELEASE_STATE.json.

| Capability | Actual scope |
|---|---|
| Inventory edit recovery | Retain visible choices on uncertain save; explicit read-only reconciliation, no write replay |
| Plan response isolation | Zone/revision/generation bound; delayed/foreign responses withheld |
| Historical previews | Readable; no Apply confirmation after zone revision changes |
| Existing UI continuity | Open role groups and searches survive same-view refresh |
| Global function bindings | Manual, revision-bound, stable-identity-aware; area-less helpers included |
| Automation-first inspection | Nested/static/template-literal/event_data references; explicit unknowns |
| Global scan | Up to eight configurations per explicit batch, not full consumer proof |
| Repair proposals | Fingerprint-bound previews; no automation configuration writes |
| Display-name cleanup | Existing confirmed plan/apply/undo and before-images, unchanged |
| Technical Entity-ID migration | Blocked pending supported consumer migration |
| Canonical persistence | Existing ContextStore/PlanStore; no new store/schema |
| Legacy helper/presence activation | Withheld; no new household control |
| Tests | 454 Python  / 56 JS; nine browser suites including six new fault/recovery cases |
| CI | Candidate and exact release-main all four jobs successful, amd64 included |
| Installation | Alpha.33 installed/offered/started; four options and auto_update unchanged |
| Runtime | Ready, connected, snapshot fresh, zone resolved; existing mode unchanged |
| Household acceptance | Ingress UI, app-principal rights, independent image/data checks still open |

Backup1ea31dc2 verified before publication: Alpha.32 app/data/options only, no HA/DB/
folders or failed parts. One Store refresh/update; no additional restart, actor,
name, role, consent or automation change. Existing HA/SQLite and registry CAS limits
remain as documented in ORGANIZATION_AND_MIGRATION.md.

Next: authenticated read-only acceptance of inventory editing/recovery and existing
routine explanation in the already authorized Erdkellerbereich use case.

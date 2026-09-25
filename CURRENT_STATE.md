# PilotSuite current state

## 2026-09-25 — Alpha.24 reconciliation in existing PR #54

Canonical repository GreenhillEfka/pilotsuite; branch feat/zone-daily-brief.
Native GitHub reads AND source-object writes work again, as does HA-MCP.
Do not restart connector setup or create another implementation/repository.

Fresh app metadata: Alpha.23 installed/offered, started, update_available=false,
auto_update=true. No backup, Store refresh, update, restart, options, roles,
learning, actuation or scheduler change was made for this source integration.
Earlier readiness observations are historical, not a new live UI/data check.
Authenticated Ingress and independent persisted-data/image acceptance remain open.

## Source reconciliation, not replacement

Remote head b994fc8b610df9a67669520795c0691950ef46ba already contained R2 and
passed exact CI 36110294548. Artifact 10852638016 matched SHA256
f24c608c0e16b0d2de48c5bd198674c69de177618799eb40722bbc33b91b88a9.
Saved local candidate b9a520ce047610d611efea25be872f766b655375 shared its base
6b1e9cbb4b02c4da86ae751e9772b95b07c1b9bd but contained additional UI/test work.
Only those missing changes are carried forward. The stronger published_source /
--allow-unchanged release gate and its four regressions are preserved unchanged.

Runtime: retain only focus/expanded-state during context reload, never old
candidates; restore presentation only on matching fresh response without stealing
focus. Unsaved selection invalidates the brief immediately. Read-only stays closed.
Tests: ten real-store API cases, six discovery regressions and explicit CI guard,
plus canonical-owner component and full-app browser fixtures. No second collector,
store, API or learner. All five version markers and both changelogs remain Alpha.24.

Local Python 3.13.5 / aiohttp 3.13.3: 308 tests passed. Node 22.16.0: 48 passed.
Playwright is absent in this local environment; no fresh local browser result is
claimed. Prior full-app local navigation was administrator-blocked, not bypassed.
The earlier green remote head does not certify this reconciliation: exact new-head
CI is required. See docs/DAILY_BRIEF_HARDENING.md for scope and acceptance boundaries.

## Exact next step

Verify this reconciliation on PR #54's exact CI. Before publication, complete and
verify a fresh PilotSuite-only Alpha.23 backup using RELEASE_RUNBOOK.md; preserve
auto_update=true. Recheck expected head/base and merge without force, check exact
main CI, then the native Store offer and one matching update only when necessary.
Do not repeat Alpha.23 deployment or create another version for unfinished delivery.

Final candidate/release/backup/runtime receipts belong in PR #54 and RELEASE_STATE.
Source CI, installed runtime, authenticated Ingress, configuration-read capability,
data/image attestation and real comfort benefit remain separate acceptance items.
Previous complete receipts remain in Git; published_source is independent of the
older top-level installation history in docs/RELEASE_STATE.json.

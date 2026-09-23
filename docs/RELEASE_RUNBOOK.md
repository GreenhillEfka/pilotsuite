# PilotSuite release and deployment runbook

Authoritative continuation procedure, adopted 2026-09-23 (ADR-026).
Read this before every release; do not rediscover an alternate deployment path.
Release publication, automated tests, installation and browser acceptance are
four separate outcomes. A successful source check authorizes none of the others.

## 1. Establish the actual baseline

- Read AI_CONTEXT, CURRENT_STATE, DECISIONS, VISION, IMPLEMENTATION_STATUS and ROADMAP.
- Fetch canonical `GreenhillEfka/pilotsuite` main, branches, open PRs, branch rules
  and Actions. Preserve unrelated changes; use a dedicated branch/worktree.
- Read `ha_get_app({slug: "0d79c5e8_pilotsuite"})`. Keep only version,
  version_latest, update_available, state, auto_update and canonical repository
  identity in the receipt. Never publish options, credentials or household data.
- Find the last **published** release commit, not merely the installed version.
  Alpha.14 was first published at `1644c9b170c861e83582ef9503775a8e913818f0`.
  Later UI fixes on main still bore alpha.14; alpha.15 packages them explicitly.
- If the candidate is already installed, do not reinstall or restart it.

## 2. Prepare one identifiable candidate

Increment VERSION, config.yaml, package VERSION, Dockerfile BUILD_VERSION and
the DOCS release marker together. Add matching entries to both changelogs.
Changes to shipped behavior after publication require a new version; prepare
them on a branch until ready. Do not keep adding runtime fixes under a released
number. Documentation-only receipts need no version bump.

Run local contracts, Python and JavaScript tests. Commit the candidate, then:

```sh
python scripts/release_preflight.py --candidate HEAD --published 1644c9b170c861e83582ef9503775a8e913818f0
```

The example baseline applies to alpha.15 only; use the last published commit for
subsequent releases. The read-only command resolves commits once, verifies all
markers/changelogs, increasing alpha version and ancestry, and emits full commit,
repository-tree and app-tree identities. Uncommitted files are deliberately not
certified. It neither talks to HA nor claims CI/backup/deployment success.

Open a small PR; wait for all exact-candidate CI jobs: Python/JS, Chromium and
amd64 container. Record SHA, run URL and job conclusions. Recheck main/open PRs
before merge; if the base changed, reconcile and re-run. Never force-push.
After merge, verify the resulting source identity and exact main CI again.
An old green run or version string alone is insufficient.

## 3. Backup and rollback gate

Auto-update was enabled at the 2026-09-23 check. Do not change that option without
authority. Prepare a fresh completed scoped backup **before publishing** a new
version; auto-update could otherwise install it before the manual update step.
Recheck freshness, installed version and completion immediately before deployment.

Verified HA-MCP route (2026-09-23): first inspect current service fields with
`ha_list_services({domain: "hassio", query: "partial", detail_level: "full"})`.
Then use `ha_call_service` with the following payload:

```json
{
  "domain": "hassio",
  "service": "backup_partial",
  "data": {
    "name": "PilotSuite PREVIOUS before TARGET",
    "apps": ["0d79c5e8_pilotsuite"],
    "homeassistant": false,
    "homeassistant_exclude_database": true,
    "folders": []
  },
  "wait": false
}
```

A successful service response is not completion. Confirm the resulting archive
with `ha_manage_backup({scope: "snapshot", action: "list", limit: 5})`, including
ID, date, nonzero size, protection status, HA/database exclusion. Inspect available
backup details to confirm PilotSuite version, app data/options and no other apps.
Keep the scoped request and completion evidence; distinguish metadata confirmation
from archive inspection or a restore drill. If necessary details/key availability
cannot be confirmed, stop before update. Never use snapshot **create/restore**:
those are full-HA operations, outside the authorization.
Historical detail-read gate (2026-09-23): `ha_call_service` with
`ws_command: "hassio/api"`, `data: {endpoint: "/backups/d454e834/info", method: "get"}`
returned `Unauthorized` even though backup listing works. This is specific to that
gateway; it did not establish a general permission failure. The user subsequently
requested the normal Store/app-backup route. Verified native, admin-authorized
Core read (same credentials, no permission changes):

```json
{"ws_command": "backup/details", "data": {"backup_id": "VERIFIED_BACKUP_ID"}}
```

Use it through ha_call_service. Inspect result.backup.addons for the exact slug and
previous version, failed_addons/failed_agent_ids/failed_folders for empty lists,
agents for size/protection, and HA/database/folder exclusion. This succeeded for
d454e834 and fresh 95bb73d4. It verifies archive metadata, not a restore drill or
byte-level archive inspection. If this native route denies access, stop; do not
change credentials or weaken guards. Prefer this scoped read to compact listing.
The scoped backup can itself stop/start the app. Inspect post-backup startup and
readiness; report this separately from an explicit restart or a version update.

Concrete rollback is `ha_call_service` / `hassio.restore_partial` with:

```json
{"slug": "VERIFIED_BACKUP_ID", "apps": ["0d79c5e8_pilotsuite"], "homeassistant": false, "folders": []}
```

The backup must include the previous app and its matching data/options, not just
a database export or older Git source. Protected archives require an available
key through the approved secret path, never in GitHub. Do not perform a test
restore against the live system. Actual recovery is only for a regression and
only this app; verify restored version/data/health. No HA Core, Supervisor or
host restart; no full restore, other apps or configuration edits.

## 4. Store, source and one update

Use the supported app management/store capability and its current schema. The
documented Supervisor operation is `POST /store/reload`, not a Core/Supervisor
upgrade. Previous Store reload through the HA WebSocket bridge was denied
`Unauthorized`. This is a known limited permission failure, not loss of HA or
GitHub access. Do not retry speculative endpoint/action variants, change tokens,
disable guards or alter permissions. Retry only after a relevant access/state
change; a normal Store refresh through an already authorized session is acceptable.
At the later 2026-09-23 check the Store already offered alpha.16: the stale Store
offer was no longer the blocker, and no reload was attempted. Backup detail access
and independent exact-source mapping remained separate open gates.

Read app metadata again. If offered version still equals installed version, stop
the deployment step without update/restart. Require the offered version and its
canonical source commit/app tree to match the candidate with passing CI. Store
metadata may not expose a commit: a version label alone is not exact-source proof.
If the mapping cannot be established, explicitly leave this gate open.
For the user-requested normal Store workflow on 2026-09-23, alpha.16 was associated
with canonical release 208b5d3 and unchanged app tree 811de10be4d11acab5ee98a41eb5dc3a93b56f46
through current main 33d5676; both exact CI runs passed. This is repository/version
association, not independent Store-checkout or installed-image attestation. Record
that limitation explicitly; never fabricate an exposed SHA or equate a reused
version with immutable source. Post-update metadata and startup must agree.

Only after all gates pass, use the scoped lifecycle operation
`ha_manage_app({slug: "0d79c5e8_pilotsuite", action: "update"})` once.
On timeout/unknown outcome, query durable app state and jobs/logs before retrying;
never blindly replay an update or restart. Existing consents, roles, options,
automations and actors remain untouched. Do not enable learning to test a release.

## 5. Verify and leave a usable handoff

- Read installed/offered version and state; inspect latest startup/logs for errors.
- Verify HA stream connected, snapshot fresh, ready, Golden Zone resolved and
  `hard_read_only`. Runtime evidence is not browser acceptance.
- In an already authenticated real HA Ingress session, check HTML, JS, CSS, API
  requests, navigation and workbench rendering. Read a short history only within
  existing authorization; no import, consent, feedback/role edits or actuator calls.
- A direct/internal HTTP 200 does not prove Ingress. Expected 403 is not a reason
  to spoof headers, expose a port or weaken authentication. If no authorized
  session is available, leave this acceptance explicitly open.
- On regression stop rollout and use the verified scoped rollback when safe.
- Update CURRENT_STATE and IMPLEMENTATION_STATUS with code SHA/PR, exact CI URL,
  backup completion/scope limitations, installed/offered versions, live checks,
  open gates and one concrete next task. Keep historical sections historical.

Official API reference checked 2026-09-23:
[Supervisor endpoints](https://developers.home-assistant.io/docs/api/supervisor/endpoints/).
Current instance service schemas take precedence over copied examples. In particular,
HA services currently expose `apps`; the Supervisor HTTP API documents `addons`.
Do not interchange these payloads without checking their respective schema.

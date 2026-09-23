# PilotSuite release routine

Required entry point for every release/deployment (ADR-026). Read AI_CONTEXT.md,
CURRENT_STATE.md and docs/RELEASE_STATE.json first, then this procedure.
Latest receipts supersede older blockers. Never restart project discovery from chat.
One canonical repository, one app: GreenhillEfka/pilotsuite / 0d79c5e8_pilotsuite.

## 1. Resume, do not repeat

Read live metadata using ha_get_app with slug 0d79c5e8_pilotsuite. Fetch canonical
main, open PRs/branches, rules and Actions. Preserve other work.

| Fresh result | Next action |
|---|---|
| Installed equals target | Do not update, rebuild, restart or create another pre-update backup; perform only pending acceptance |
| Target offered, different installed version | Skip Store refresh; verify source/CI and scoped backup |
| Target not offered | Use documented authorized Store refresh if available; reread metadata, never install an unrelated version |
| Backup request accepted but not yet listed | Check completion; do not replay creation |
| Update outcome unknown | Read durable app state and logs/jobs before doing anything else |
| Endpoint returns Unauthorized | Stop that route; do not infer all HA operations are denied or alter permissions |

Already authorized: PilotSuite update/start/stop/restart, necessary Store refresh,
PilotSuite-only backup and regression recovery. Do not repeatedly ask for the same
authorization. This does not authorize other apps, HA Core/Supervisor/host changes,
config/automation edits, actor calls or enabling learning/autonomy.

## 2. Candidate and exact source evidence

Behavioral changes require a new version across VERSION, config.yaml, package
VERSION, Dockerfile BUILD_VERSION and DOCS release marker; update both changelogs.
Documentation-only receipts do not require another release.

Run repository contracts, Python and JS tests; commit; then run:

```sh
python scripts/release_preflight.py --candidate CANDIDATE_SHA --published PREVIOUS_PUBLISHED_SHA
```

Replace placeholders with resolved commits, not the installed version. This is a
read-only source check, not an installer. Record commit, repository tree and app tree.
Wait for exact PR CI: Python/JS, Chromium and amd64 container. Recheck base/open PRs,
merge without force, then verify exact main CI. An earlier green run is insufficient.

Source association for the normal Store workflow:
- canonical repository identity and offered version must match the tested release;
- resolve the published release commit and compare the app tree through current main;
- do not reuse a version for a changed app tree; ambiguity stops the update;
- if Supervisor exposes a checkout SHA, compare it;
- if it does not, record repository/version/app-tree association explicitly, not an
  independently verified checkout SHA or installed-image attestation.

Store metadata alone is not a cryptographic source proof. Do not invent one.
Alpha.16's concrete association and limitation are in RELEASE_STATE.json.

## 3. Scoped backup: create, then verify through the native API

With auto_update enabled, complete a scoped backup before publishing a new version;
automatic installation could otherwise precede the manual step. Do not change that
option. Immediately before deployment, recheck installed version and backup freshness.

Read current hassio partial-service fields. Through ha_call_service:

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

Find the matching completed backup using ha_manage_backup:
`{"scope":"snapshot","action":"list","limit":5}`.
A successful service response is not completion. Do not use snapshot create/restore,
which are full-HA operations.

**Verified detail read**, through ha_call_service with the same configured credentials:

```json
{"ws_command":"backup/details","data":{"backup_id":"COMPLETED_BACKUP_ID"}}
```

Require result.agent_errors empty and result.backup:
- addons contains exactly PilotSuite's slug and the installed previous version;
- failed_addons, failed_agent_ids and failed_folders are empty;
- homeassistant_included and database_included false; folders empty;
- expected date and nonzero agents size; unprotected, or an available approved key.

Standard app backup covers the app and its data/options. This is metadata
verification, not archive extraction or a live restore drill. Missing confirmation
stops deployment. Never publish options, household data, tokens or backup archives.
A backup may itself stop/start PilotSuite; verify health afterwards.

## 4. Store and update once

If target is already offered, do not refresh the Store. If refresh is needed,
the Supervisor operation is POST /store/reload, using an already authorized supported
capability/session. A denied bridge call is not permission to try variants or weaken
security. If refresh is unavailable, leave installation pending.

After source/CI and backup gates, reread installed/offered versions. If target is
already installed, skip. Otherwise use exactly:

```json
{"slug":"0d79c5e8_pilotsuite","action":"update"}
```

through ha_manage_app. Do not add a speculative restart. On timeout, inspect version,
state and logs before any retry. Preserve all options, roles, consents and automations.

## 5. Runtime acceptance and scoped recovery

Read ha_get_app and ha_get_logs(source=supervisor, slug=0d79c5e8_pilotsuite).
Require target installed/started, target in startup log, hard_read_only, connected
stream, fresh snapshot, readiness and resolved Golden Zone. Allow initial connection
setup to finish; do not misclassify its first not-ready line as a regression.

If a regression requires recovery, restore only the pre-update PilotSuite app/data
using ha_call_service with domain hassio, service restore_partial and:

```json
{"slug":"VERIFIED_BACKUP_ID","apps":["0d79c5e8_pilotsuite"],"homeassistant":false,"folders":[]}
```

This overwrites PilotSuite data since that backup; never do a live test restore.
No full restore, other app, HA/Core/Supervisor/host restart. Verify previous
version/data/health afterwards. If safe recovery cannot be established, stop and report.

## 6. Browser acceptance and durable handoff

In an authenticated real HA Ingress session, verify HTML, JS, CSS and APIs plus
navigation, guide and workbench. No role/consent/feedback edits, imports or actuator
calls for acceptance. An internal HTTP 200 is not browser acceptance. Never spoof
Ingress headers, expose a port or weaken access. With no session, mark UI pending;
do not undo a healthy installation merely because browser access is unavailable.

Update RELEASE_STATE.json, CURRENT_STATE and IMPLEMENTATION_STATUS with source/CI,
backup, installation, runtime and browser results separately. Record one concrete
next task. Keep final PR/main CI receipts in the PR; avoid creating another
documentation PR solely to record a documentation CI run.

## Verified operational facts (2026-09-23)

- Alpha.18 update repeated the working routine: ha_get_app offered alpha.18 while
  alpha.17 ran; fresh hassio.backup_partial with apps [0d79c5e8_pilotsuite]; list
  completion; native backup/details verified b6c90eb0 and alpha.17 app/data/options;
  exact source CI and unchanged app tree checked; one ha_manage_app(action=update);
  ha_get_app and startup/readiness logs confirmed alpha.18, started, hard_read_only,
  connected stream, fresh snapshot and resolved zone. No separate restart needed.
- Store availability and installation permission are different gates. Alpha.18 was
  already offered at the successful deployment check; no Store refresh was needed
  or performed. This success does not prove the previously denied /store/reload
  bridge is authorized. Never describe an unavailable Store offer as a general
  inability to install; resume the working update path as soon as the offer matches.
- Keep the live outcome and exact next action in RELEASE_STATE.json. Do not ask for
  already-granted update/backup authorization or recreate this routine each turn.
- Native backup/details worked for d454e834 and 95bb73d4 with existing credentials.
- The earlier hassio/api backup-info call was denied. That gateway result did not
  establish a general backup permission failure. Do not repeat the old blocker.
- Store already offered alpha.16; no refresh was necessary.
- Fresh scoped backup followed by one ha_manage_app update succeeded.
- No automatic re-enabling of a paused recurring task is part of a release.

References: [HA partial backup](https://www.home-assistant.io/actions/hassio.backup_partial/),
[partial restore](https://www.home-assistant.io/actions/hassio.restore_partial/),
[native backup WebSocket handlers](https://github.com/home-assistant/core/blob/dev/homeassistant/components/backup/websocket.py).
Instance service schemas take precedence over examples; HA services use apps,
while some Supervisor HTTP schemas use addons.

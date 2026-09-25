# Maintenance, existing helpers and recovery — Alpha.27

## Product scope

The user's requested maintenance slice is integrated into the existing app, not a
second management service. The installed-version card links to `/maintenance`.
The last three **bundled package versions** and their release notes are not an
installation history, downloadable old images, or a downgrade selector.

Update status comes from the existing cached HA state/registry snapshot. Only the
hassio update entity with unique ID `0d79c5e8_pilotsuite_version_latest` is trusted;
renames are allowed, duplicates/stale/malformed/version-mismatched data are unknown.
The install link goes to the canonical native HA app page; HA asks for installation
confirmation. PilotSuite does NOT call update/install itself. There is no new
Supervisor privilege, generic service executor, Store reload or background install.
Native cold app backup can stop this very process, so a reliable native backup /
update transaction cannot be hosted by pretending this app survives its own backup.
The existing release runbook remains the deployment mechanism.

## Three different recovery tools

| Tool | Scope | Not covered |
|---|---|---|
| Local configuration savepoint | Zone definitions, decisions, role groups, detector settings | HA objects, evidence/review text, consent, secrets, app binaries |
| Native PilotSuite-only app backup | App version and app data/options under HA's backup contract | Unselected HA/Core/other apps and external data |
| Object-specific HA before-image | A specific future helper/automation change | Not implemented by this release's savepoints |

A local point is under PilotSuite's own `/data/savepoints`, not HA `.storage`.
It has a UUID, UTC timestamp, package version, label, explicit schema and SHA-256
checksum. The checksum detects corruption; it is NOT a signature or protection
against an attacker with write access to the data directory. Points are private
mode-0600 files under a mode-0700 directory. Writes are bounded (4 MiB), flushed,
published without overwrite, and read back. At most 64 points; manual creation
reserves the last slot for before-restore recovery. No automatic deletion and no
upload/import of arbitrary files. Data-directory loss requires an off-device native
backup; a savepoint on the same disk is not disaster recovery.

## Local restore is real, but deliberately narrow

The canonical PlanStore owns savepoints via a mixin and its existing mutation lock.
It uses the existing selection/zone/context SQLite database, schema 8. No second
zone owner or evidence store is created.

1. Explicitly create a named point; GET never writes one.
2. Explicit preview checks its checksum, schema, scope and current configuration.
3. Display affected zones and consequences; require a new confirmation checkbox.
4. Submit exact point hash + current-basis hash + `confirm_paused_restore=true`.
5. Hold the application projection lock and PlanStore lock until the disk worker
   finishes, including client disconnect; SQLite `BEGIN IMMEDIATE` serializes writes.
6. Refuse stale basis without mutation. Before any zone change, write and verify a
   new before-restore point. Disk failure blocks the database operation.
7. Replace saved zones' configuration; preserve newer additional zones. Increment
   revisions, force restored zones paused, clear both learning consents. Existing
   evidence, feedback and authored review text are not restored or deleted.
8. Read back before commit. SQLite rollback handles exceptions. Commit a durable
   idempotency receipt so replaying the same request never repeats the operation.
9. Rebuild projections from the existing world cache; no HA call or old event replay.

Restored old entity IDs remain historical configuration, not a claim that those
entities still exist. Paused zones and fresh explicit learning consent are essential.
Unknown/newer schema, invalid point, hash conflict, symlink/path issue or missing
before-point stops recovery. This path cannot repair a corrupted SQLite database.

## Rescue behavior

Detected database bootstrap failure (SQLite error or unsupported schema RuntimeError)
keeps the ordinary authenticated Ingress page available as a maintenance/rescue view.
It does not replace the file, start HA event processing or expose zone mutations.
Only fixed recovery GET/HEAD paths remain accessible; existing TCP-peer guarding is
unchanged. Full native recovery remains outside PilotSuite so it is available even
when this app cannot boot. No authentication/peer/header/port bypass or automatic
native restore. Native restore overwrites the selected app/data to its saved point;
require a usable backup and key when applicable, and select only PilotSuite.

## Existing helper inspection

A user explicitly selects a configured Habitus zone and requests inspection. The
service resolves its current cached inventory, matches registry metadata and reads
only supported storage collections (`input_boolean/list`, `input_number/list`,
`input_select/list`, `timer/list`). It matches immutable collection `id` to registry
`unique_id`, NOT mutable entity suffix or friendly name. This matters for renamed
helpers. At most 200 zone candidates, 2,000 collection rows, 1 MiB per response and
60 seconds overall; failed collections yield no partial success.

Only safe type-specific fields are shown. For timers a non-true/missing restore
setting is explicit. Flow helpers such as templates/groups remain visible but their
configuration is not claimed read by these storage commands. YAML helpers absent
from storage are not considered missing from HA. All helpers remain existing/not
adopted; no create, rename, role assignment, learning consent or ownership change.
Network reads are outside the projection lock; revision and registry candidates are
rechecked afterward. There is no automatic scan from a GET or page refresh.

## Historical Golden Zone setting

`golden_zone_area_ids` is kept for compatibility but labelled **Startbereiche (nur
Ersteinrichtung)**. `ZoneStore.bootstrap` checks `zone_meta.bootstrapped` and does
nothing after first initialization. Editing the app option later does not add,
remove or redefine existing Habitus zones. Use the app's zone editor instead.
The main status card now says active Habitus zones rather than implying one mutable
special golden zone. No existing options/zone definitions are migrated or reset.

## Acceptance

- Full-source Python tests: real files/SQLite, preview/stale/replay, permission/symlink,
  failure before/after DB mutation, evidence/consent boundaries, future-schema refusal.
- Actual HTTP application tests: methods/content type/Ingress, no GET HA I/O, explicit
  storage reads, renamed identity and revision race, corrupt database rescue.
- Actual disposable-app browser test: last-three display, native-link handoff,
  unsaved editor navigation guard, create/preview/stale/confirmed restore, timer
  inspection, error invalidation, 390/1440 layout and corrupt-file rescue page.
- Local full-browser navigation is blocked by the environment's administrator policy;
  do not bypass it. The new browser step is mandatory in exact remote CI.
- Tests do not constitute authenticated household Ingress or HA storage-command
  capability acceptance of the app's own principal. No household restore drill.

## References checked 2026-09-25

- https://www.home-assistant.io/integrations/update/ — native update entity semantics.
- https://developers.home-assistant.io/docs/apps/configuration/ — app privileges and cold backup.
- https://www.home-assistant.io/common-tasks/os/ — native backups and partial recovery.
- Existing version-matched HA MCP helper-list contract; actual renamed-helper and timer
  metadata were read natively without changing configuration. No household data in this document.

## Remaining work (Issue56)

Safe helper creation/adoption remains separate: exact plan, user scope, no guessed
identity, object snapshots, read-back, restart/timeout recovery in disposable HA.
This maintenance release does not claim that executor or an operating presence /
light / media / climate controller. Avoid adding disconnected contract-only modules.

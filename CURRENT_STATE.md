# Current State

Last updated: 2026-09-22

## alpha.4 capability correction
- Transport readiness is independent of climate sensor availability.
- Per-capability status: available, partial, unavailable, not_present.
- Unknown climate scores are null; buttons and diagnostics do not count as climate failures.
- 28 local regression tests and GitHub CI (including amd64 build) passed.
- alpha.4 installed after confirmed app-only backup; Supervisor reports started.
- Runtime logs confirm ready=True, connected stream, fresh snapshot and resolved zone.
- Real browser Ingress requests to status, moods, suggestions and golden-zone returned 200.
- Visual rendering of the newly delivered alpha.4 frontend remains separately unverified.
- Deployed code: 941831cb74575ac17307b1a725f0120942ddd687. No actuation enabled.
- User screenshot confirmed alpha.3 Ingress UI loads and displays live observations.

## Repository milestone
- Version: `0.1.0-alpha.4`; architecture v21, reviewed modular-monolith target.
- Read-only foundation milestone, NOT a complete habit-learning implementation.
- Existing alpha.3 metadata work retained; no restart or legacy bulk merge.

## Implemented in alpha.3
- Ingress TCP-peer restriction, loopback liveness only, internal repeated-slash routing.
- Celsius normalization from Celsius/Fahrenheit/Kelvin; invalid climate data excluded.
- Missing required climate kinds prevent stable/ready claims.
- Severity separated from unknown statistical confidence; stable rule/scope IDs.
- Stream connection health, resync on subscription/reconnect, backoff on clean close.
- Snapshot/derivation serialization and older-state rejection; disabled entities excluded.
- Scoped derivation and periodic UI reads.
- Review decisions, full vision and capability ledger in the repository.
- Local regression suite covers HTTP paths/security, semantics, projection and reconnect.

## Previously verified on target HA (historical alpha.2 evidence)
- App `0d79c5e8_pilotsuite` installed; HA Core 2026.9.3.
- HA projection resolved Erdkeller with 48 entities; apply rejected with HTTP 409.
- Old Core App Store repository removed. Remaining HACS/config entries/entities
  were NOT comprehensively audited; do not claim complete legacy cleanup.
- User reported Ingress 404. Internal root/health success did not prove browser UI.

## Live deployment — 2026-09-22
- User authorized app-only backup, update and tests. A fresh app-only backup was
  created successfully and confirmed present through the dedicated backup listing.
- Store check_updates discovered alpha.3; app update and start completed.
- Supervisor app metadata confirms alpha.3 and state started. Startup logs confirm
  version alpha.3 and hard_read_only mode. No unrelated apps/configurations changed.
- Deployed code commit: ae971e4072123a0462435f85aa742f1c14b1f86c; CI succeeded.
- HA-MCP proxy request to /health/ready returns 403 Ingress access required:
  the transport peer is not the permitted Ingress proxy. Do not bypass or weaken
  the peer guard. This does not establish failure of actual browser Ingress.
- Dedicated app/backup tools worked; the raw hassio/api backup-info request was
  unauthorized earlier. Do not conflate that with all HA-MCP operations failing.

## Not yet verified live
- Real Ingress browser path/assets and new readiness behavior.
- Current alpha.3 Erdkeller projection and live apply rejection remain unverified
  through the blocked proxy. Historical alpha.2 checks are not alpha.3 acceptance.
- Physical sensor freshness, correct sensor roles, disconnect/load soak.
- No new HA configuration or automation changes are part of this milestone.

## Next
Follow `docs/IMPLEMENTATION_STATUS.md` acceptance gates, then the consented
read-only learning milestone in `docs/ROADMAP.md`.
Do not claim SQLite, habit learning, voice, native entities or rollback are implemented.

# Current State

Last updated: 2026-09-22

## Repository milestone
- Version: `0.1.0-alpha.3`; architecture v21, reviewed modular-monolith target.
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

## Not yet verified live
- alpha.3 installation, real Ingress browser path/assets and new readiness behavior.
- Physical sensor freshness, correct sensor roles, disconnect/load soak.
- No new HA configuration or automation changes are part of this milestone.

## Next
Follow `docs/IMPLEMENTATION_STATUS.md` acceptance gates, then the consented
read-only learning milestone in `docs/ROADMAP.md`.
Do not claim SQLite, habit learning, voice, native entities or rollback are implemented.

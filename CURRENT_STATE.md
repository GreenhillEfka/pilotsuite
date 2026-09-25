# PilotSuite current state

## 2026-09-26 - Alpha.31 installed and runtime-verified

Canonical GreenhillEfka/pilotsuite; app 0d79c5e8_pilotsuite. PR67 release commit
75caa39df10a7eb25a0a3c85c0a526475d18b03b; root
 d651049d4afbae883f642c5786930ac9cb6e7772; app tree
05557cea66e5a9ca99489331f6f39f05839b1bcf (remote and local tree reread).
Candidate e24fa91a70ae840554af2a1374fae2773905f6b8 / CI36201287332 and release-main
CI36201656060 passed all four jobs and eight browser suites. Local full checkout:
405 Python and 53 JavaScript tests passed; application and tests compiled.

Before publication: backup319e9e3b, PilotSuite Alpha.30 before Alpha.31,
2026-09-26T00:17:26.615880+00:00, 54,261,760 bytes. Native snapshot/list and
backup/details confirmed only PilotSuite Alpha30, no HA/database/folders, no failed
components/agents or reported errors; unprotected local agent. No restore drill,
archive extraction or off-device resilience claim.

One native Store refresh and one PilotSuite update completed. Metadata confirms
installed/offered 0.1.0-alpha.31, started, update_available=false, auto_update=true;
all four options unchanged. Exact Alpha31 startup and repeated subsequent logs show
presence_adoption_review, ready, connected stream, fresh snapshot and resolved zone.
Partial sensor capabilities are not a transport failure. No extra restart/rebuild,
unrelated app update, household configuration/role/consent edit or runtime activation.

## Delivered UX

Six workspaces: Cockpit, Zonenmodule, Konfiguration, Verlaeufe, Werkbank and System.
Cockpit has measured zone cards, source counts and zone/status filters. Module views
show presence, lighting, climate and media sources, reference interpretation and
implementation boundaries. Structural graphs are not claimed live controllers.

Configuration reuses the existing zone/entity/role forms. Per-module filters and
source search preserve hidden selections; counters and a before/after preview show
role, learning-consent and detector edits before the original explicit save.
Desktop sidebar and phone bottom navigation share the same destinations. Local
light/dark/system theme, comfortable/compact density and optional technical IDs
store only presentation choices. Dirty drafts block navigation. Existing explicit
history charts/heatmaps and routine/review workbench remain available; #ps-all keeps
the complete view. The existing read-only presence review is reachable on explicit click.

No new execution capability, permission, collector or migration. Original forms,
handlers and canonical state remain authoritative. docs/UX_WORKSPACE.md explains
component boundaries and the validation matrix.

## Verification boundaries

CI artifact10891478892 / run36201287332 SHA256
 d6e282e135d20191a24e63de175d0b3be4f02b7d5e71bdf129de484f411b722f was verified.
Desktop light cockpit, desktop dark modules, mobile dark cockpit, tablet light cockpit
and desktop configuration screenshots were visually reviewed. Browser checks cover
390/768/1440 widths, both themes, forms, save/cancel, dirty guards, stale/error states,
deep links and no new actuator/provisioning/runtime-enable calls.

These are actual-application tests with synthetic data, not authenticated household
Ingress acceptance or a full accessibility audit. Local browser policy was respected;
no workaround or authentication weakening. Source/version/app-tree association is
not independent installed-image attestation. Earlier helper/presence behavior has
not been certified by this presentation-only package. No completed Deep Research
report was available or claimed as the basis of the implementation.

Next: observe real navigation/configuration usability; backend helper/presence safety
remains a separate fault-tested work package before household takeover. Do not repeat
Alpha31 deployment for this documentation-only closure. Final doc CI goes in comments.

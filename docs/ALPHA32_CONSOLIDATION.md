# Alpha.32 consolidation and release candidate


PR69 remains the canonical implementation. The offline Alpha32 candidate is NOT a
replacement for its ContextStore/PlanStore integration or confirmed name cleanup.
Only its compatible presentation module is integrated: maintenance now shares the
workspace's local theme/density tokens. It shows version/update/local points and
explicitly unverified native app-backup status; it never infers a verified backup
from a local configuration point. Rescue exposes only the necessary read-only theme
assets, never the full workspace or organization mutation endpoints.

The global catalogue can now be inspected through explicit batches of at most eight
automations. Progress reports the requested catalogue coverage and unread records,
not whole-house consumer completeness. Each new inventory/render starts a new scan;
results are transient and each current batch replaces the previous display.

The old helper-create/delete executor is also unavailable through provisioning requests
until its transport/identity/recovery behavior has its own accepted implementation.
Confirmed display-name cleanup uses the separate reviewed native registry path already
owned by PlanStore. No household name/value/automation/consent changes occur on update.

The save acknowledgement is displayed after the post-save canonical context read, not
before a renderer can replace it with a stale-revision notice. New regressions cover
that existing assertion, global explicit reads, maintenance themes, native-backup
uncertainty and rescue-route isolation. Local browser navigation remains blocked by
administrator policy and was not bypassed; remote browser CI is the acceptance gate.

Local validation of the consolidated tree: 454 Python and 56 JavaScript tests passed.
Remote exact CI, visual review, scoped native backup and installation remain separate
gates. The older PR69 head d374329 failed the save-acknowledgement browser assertion;
that failure is not an unconfirmed success. Candidate lineage remains on that PR.

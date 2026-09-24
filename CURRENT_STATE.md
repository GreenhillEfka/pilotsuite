# PilotSuite current state

## Alpha.23 published; installation unverified — 2026-09-24

**PR #52 is merged. Do not implement, version or publish the Prüfkompass again.**
The current continuation has GitHub access but no exposed HA-MCP tools, confirmed
by tool discovery. No new HA read, backup, Store refresh or app update was performed
in this handoff. This is a tool-availability limitation, not a denied HA permission.
The current installed version and current Store offer are therefore unverified.

## Verified source and tests

| Evidence | Actual value |
|---|---|
| Release commit | `dfecb464f9f67eb1dd3e393b8ecc99e9ca208814` |
| Candidate | `cf445355868cbe1448f402be19207f66beae5898` |
| Candidate/release repository tree | `3b3125e3643e3fda6a851a2bdc2851693a4dfc0e` |
| Application tree | `38ef81068ff75f135bce6734a43e2caca3c09b8c` |
| Candidate CI | [35990039222](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35990039222), success |
| Release-main CI | [35991187908](https://github.com/GreenhillEfka/pilotsuite/actions/runs/35991187908), success |

CI confirms 247 Python and 48 JavaScript tests, three synthetic browser flows,
repository/source contracts and amd64 build. The release tree was independently
reproduced from its SHA256-verified source-only CI bundle in this continuation.
This does not attest an installed image or an authenticated household browser.

## Prior native preparation, not a new live check

Native backup/details previously verified backup **5c40193c**, Alpha.22 only,
**54,118,400 bytes**, dated **2026-09-24T11:02:07.031215+00:00** (13:02:07 Vienna).
It completed before publication. No HA configuration/database/folders, no failed
components and no key requirement were reported. No archive download or restore.
Its current existence and freshness must be rechecked when live access returns.
The older 33908293 contains Alpha.21 and is not the Alpha.23 recovery point.

The preceding native Store refresh offered Alpha.23 and one app metadata read
confirmed that offer. A later prior metadata response again reported an Alpha.22
offer; the prior results do not establish the current offer. Every prior observed
installed version was Alpha.22/started, with auto_update=true. No assistant
Alpha.23 update call has been made; subsequent automatic installation is unknown.
The refresh affected catalog metadata for other apps too, not their installation.

The previous PR body/final reply copied the backup size/date incorrectly, and the
merge message contains an incorrect application-tree hash. The values above come
from the actual native response and Git tree, not the prose. PR #52 records the
correction without rewriting its immutable Git history.

## One next step

**Resume live Alpha.23 delivery with `ha_get_app(slug="0d79c5e8_pilotsuite")`.**
If already installed, skip backup/update/rebuild/restart and verify runtime. If not,
recheck source/CI, current offer and matching scoped backup under RELEASE_RUNBOOK.md;
refresh Store only when necessary, then at most one matching native app update.
Do not alter options, consents, rights, automations, devices or other installed apps.
Do not use alternative bridges, recovered tokens or direct container access.

RELEASE_STATE.json keeps the completed Alpha.22 receipt intact and records the
actual Alpha.23 publication separately in `pending_release`. Replace the completed
deployment receipt only after real installation/runtime verification. Ingress UI,
app config-read rights, data preservation and installed-image attestation remain
separate acceptance items. No new release is needed for this documentation handoff.

## Product continuation

The Prüfkompass has five derived sections and one basis-checked next step, transient
zone filters/sorting, explicit comparisons and retained authored notes. Existing
PlanStore/context owners, schema 8, hard_read_only and denied Apply are unchanged.
After verified delivery, demonstrate one helpful or reasonably rejected proposal
within the already consented Golden Zone, not more review machinery or actuation.
The resumed autonomous mandate is in DEVELOPMENT_MANDATE.md; no scheduler change
was made here. Previous full handoff remains in Git at `dfecb464f9f67eb1dd3e393b8ecc99e9ca208814`;
older ledgers remain in CURRENT_STATE_HISTORY_2026-09-23.md and
 docs/IMPLEMENTATION_HISTORY_2026-09-23.md.

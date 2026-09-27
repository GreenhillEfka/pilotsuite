# Current state — concept consolidation; app unchanged

## Verified baseline

On 2026-09-28, canonical main was `b86d7e75ea085a4f06ff1fc76e74a88bbead351e`;
there were no open PRs at the start of this review. Fresh HA-MCP metadata confirmed
Alpha.54 installed/offered, started, with auto_update enabled. No update, restart,
backup or household configuration write was performed for this concept-only work.

[docs/RELEASE_STATE.json](docs/RELEASE_STATE.json) retains the actual Alpha.54
source/CI/backup/runtime receipt. The previously observed ready stream and fresh
snapshot are receipt evidence, not newly claimed runtime checks here.

## Current change

The existing vision, architecture, roadmap, workspace design and entry/safety docs
now describe a smaller zone-first product. Current implementation is separated from
the proposed three-entry navigation and later internal consolidation. Historical
learning/shadow contracts remain compatibility references. Duplicate ADR numbers
were disambiguated without changing their decisions.

No app code, schema, version, stored zone or release receipt changes. The existing
local AGENTS.md remains untouched. Earlier release narratives are recoverable in
[CHANGELOG.md](CHANGELOG.md) and the
[previous state document](https://github.com/GreenhillEfka/pilotsuite/blob/b86d7e75ea085a4f06ff1fc76e74a88bbead351e/CURRENT_STATE.md).

Baseline regressions rerun: 568 Python and 70 JavaScript tests passed. The Python
run emitted SQLite ResourceWarnings; passing tests do not establish a leak-free
runtime. This review does not attribute those warnings to a specific owner.

## Next bounded implementation

Simplify the existing workspace around the current zone-presence result, as defined
in [docs/UX_WORKSPACE.md](docs/UX_WORKSPACE.md) and step 1 of
[docs/ROADMAP.md](docs/ROADMAP.md). First extend synthetic browser regressions;
reuse existing views and API contracts. Do not add another status store or frontend
adapter layer. Runtime consolidation follows measurement, not a rewrite.

Authenticated household Ingress acceptance remains separate and open. All four
saved zones have not been independently read back after Alpha.54. When an authorized
browser is available, inspect Erdkellerbereich and one unlike saved zone across
multiple passive refreshes; check focus, reading position, drafts and unknown states.
Do not use Apply, change household metadata or switch devices for this acceptance.

Own-output activation, existing automation takeover, complete technical entity-ID
migration and adaptive comfort learning are not granted by this concept change.

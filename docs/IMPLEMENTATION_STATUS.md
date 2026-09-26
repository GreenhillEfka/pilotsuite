# PilotSuite capability and acceptance ledger

## Alpha.37 candidate

| Capability | Actual scope |
|---|---|
| Event acceptance | Old/equal/duplicate/malformed frames stop before learning |
| Context timestamps | Each light/lux channel must not postdate its activation |
| Delayed activity | Existing explicit consent/time/dedup rules preserved |
| Effective roles | Derived/manual origin visible, no inferred persistence |
| Comparison temperature | Optional independent display, guarded same-unit difference |
| Local validation | 485 Python / 58 JS, compile and repository contracts pass |
| Remote CI/browser/deployment | Pending candidate gates; see final release receipt |
| Household edits / new authority | None |
| New adaptive control | Roadmap only, not an installed learner or controller |

Alpha.36 remains the last verified installation in RELEASE_STATE.json until a completed
Alpha.37 receipt replaces it. Historical cumulative inventory, trigger integrity,
identity checks, name-cleanup/undo and nine browser suites are retained. Prior detailed
ledger: cbf43ccebdfb6244a73ed379335d80eca4c5db3e:docs/IMPLEMENTATION_STATUS.md.

The new event guard does not retroactively repair old evidence. Local timestamps are
not evidence of physical simultaneity or human intent. No active presence takeover,
light/media control or new learning scope follows from visual readiness. The presence-
first architecture and per-stage acceptance: PRESENCE_FIRST_INTELLIGENCE.md.

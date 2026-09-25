# PilotSuite Workspace — Alpha.31

## Goal and information architecture

Replace the technically accumulated long page with task-oriented workspaces, while
preserving the existing state and permission owners. Desktop navigation sits in a
persistent sidebar; phones use the same six destinations in a bottom navigation bar.

| Workspace | Primary task | Detailed evidence |
|---|---|---|
| Cockpit | Find a zone, understand measured state and the next task | Live-projection connection, selected/unreviewed counts, existing brief |
| Zonenmodule | Understand presence, lighting, climate and media inputs | Sources → virtual reference → implementation boundary; explicit read-only review |
| Konfiguration | Compose zones, confirm entities and assign sensor roles | Searchable existing forms, module filters, before/after diff, original explicit save |
| Verläufe | Examine a selected interval | Existing recorder/statistics graph, table and activity heatmap |
| Werkbank | Evaluate evidence and author a routine | Existing learning configuration links, draft and review-note editors |
| System | Adjust local presentation; inspect app state | Theme, density, technical IDs; existing maintenance/recovery link |

`#ps-all` retains the complete page as a supported advanced view. Existing section
anchors resolve to their owning workspace. Navigation refuses to hide an active
configuration, selection, routine or review-note draft; saving/cancelling is explicit.
No automatically executed reconciliation is associated with navigation.

## Visual language and component boundaries

Use local system fonts, restrained slate/teal colors, 18px cards, 12–24px spacing,
44px minimum standard controls, clear text labels and visible keyboard focus. Dark
and light themes have independent semantic surface/text/border/accent/warning tokens.
System-theme changes are reflected without touching HA. Compact mode alters spacing,
not what data is relevant. Motion is removed when reduced-motion is requested.

Small presentation components: workspace nav; connection/stat cards; searchable zone
cards; module cards; source chips; structural source/reference/output diagram;
state-model sequence; source selector/search/count; config diff; explicit review
outcome. No remotely loaded fonts, icon libraries, UI dependencies or build toolchain.

`workspace-model.js`: pure, tested presentation model, defensively formatted measurements,
revision/zone consistency, local preference allowlist and configuration diff.
`workspace.js`: progressive adapter around existing renderers; moves original elements
and preserves IDs, listeners, forms and canonical data. It is not a second application
state owner. `workspace_api.py` injects assets into the single canonical HTML document;
it adds only explicit static asset routes. Rescue retains the existing minimal document.
`workspace.css`: tokens, components, responsive layout and print/reduced-motion rules.

## Configuration interaction

One role assignment remains authoritative for all modules. Module filters hide other
role fieldsets without changing their checkbox values. Text search never deselects
hidden sources. Counts show selected versus visible candidates. Existing unavailable
assigned entries remain visible when not filtered, allowing conscious removal.

The preview compares current effective roles, both learning switches and the detector's
threshold/day/timezone settings. It describes only an unsaved local edit. The existing
server revision checks, source-change warnings and learning confirmations remain in
force. The preview does not create consent, and browser preferences contain only view,
theme, density and ID-display choice—not source identities, states or draft content.

## Visualization truth boundaries

No global health percentage, person count or simulated activity curve. Unknown/nonfinite
measurements show an em dash, not zero. Zone cards suppress measurements when disconnected
or paused. Source usability is not execution approval. State sequence and dependency
views are labelled structural models, not a verified running presence controller.

The user explicitly starts a structural presence-automation read; navigating never scans
all configurations. The result warns that missing references do not establish conflict
freedom. Zone/revision changes and failed reads invalidate old diagrams/results. No
runtime activation or automation takeover control is introduced in this package.

## Validation matrix

Keep all existing Python, JavaScript and seven browser regressions. Existing actual-app
full-page regressions explicitly use supported #ps-all; the additional actual-app test
starts the default workspace and covers cockpit filters, four module views, focus,
source search with retained checks, diff, dirty navigation guard, cancel, explicit save,
unchanged unrelated roles/consent, explicit structural review, failed reads, HTML-like
names, no automatic recorder requests, theme/density reload, deep links, reduced motion,
390/768/1440 widths, both themes and zero actuator/provision/runtime-activation calls.

Python tests verify the one document, static allowlist, original form identities,
Ingress enforcement, content-security policy and rescue boundary. Unit tests cover
preference allowlisting, unknown values, revision consistency and deterministic diffs.

The local browser denied navigation with administrator policy. No policy was altered
or bypassed. CI performs the normal isolated browser checks and produces synthetic
screenshots. These tests are not authenticated household browser acceptance, assistive
technology user testing or proof of real comfort gains.

## Reference basis and limits

This implementation is based on actual repository inspection and these primary
references, not a claimed completed Deep Research report:

- Home Assistant sections: grouping related cards and explicit layouts.
  https://www.home-assistant.io/dashboards/sections/
- WAI patterns: explicit navigation/selection semantics and keyboard focus.
  https://www.w3.org/WAI/ARIA/apg/patterns/tabs/
  Workspace destinations use links, while the existing zone switcher retains its tabs.
- WCAG status messages: expose outcomes without unnecessary focus movement.
  https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html

No blanket WCAG-conformance claim. Later work: user-observed task timings, screen-reader
acceptance, a separately validated live timer/runtime view, and progressive replacement
of the legacy renderer adapters as behavior is fault-tested. Do not display a control as
available merely because its input cards look complete.

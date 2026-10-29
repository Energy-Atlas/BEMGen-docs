# ADR-029: Thin opt-in Grasshopper reference-program adapters

Status: Accepted implementation on a feature branch; not merged or released

Date: 2026-10-28

Decision: D-178. Continues ADR-028 without changing source-program physics, source representability or production validation.

## Decision

Expose the authenticated source catalog through a new *DOE Reference Program* component, separate from the atlas *Program JSON* component because the packet formats and provenance contracts differ. Reuse Program Preset Goo and the existing catalog/CreatePreset APIs. A small native-free selection/presentation service makes discovery and explicit input requirements testable without Rhino.

Blank source-zone selection returns catalog information without a preset. Selecting a program requires an exact source zone, explicit WWR and independent geometry and daylight-saving departure acknowledgements. Unknown source identities have no illustrative fallback. The component exposes provenance, exact zone names, use/multiplier details, representability and source-coverage/calendar notices. It supplies neither a weather choice nor complete DOE geometry/HVAC.

Append *Require Floor Research Eligibility* to *Convert2IDF*, default false, using its existing appended-input deserialization guard. Preserve all existing indices/GUIDs/defaults. Pass the option to the existing backend writer gate, which a production override cannot bypass.

Keep comparison reporting as a backend API. Grasshopper currently has no parsed SimulationResult parameter, result-reader or runner path. Creating that workflow would be a separate architecture decision, not a thin adapter.

## Verification and limits

Native-free selector tests cover discovery, exact versions/zone names, explicit WWR, separate acknowledgements and visible provenance/omissions. The real Grasshopper component-instance path is tested in a fresh task-owned Rhino process using public constructors and GH_Document solutions, with actual assembly location verified. That narrower check is not normal component-server registration, archive restoration or viewport certification.

The laptop discovers both an installed BEMGen 1.1.0 and the task build 1.4.0 under the same GHA filename. Renaming only a task-owned artifact removes the filename prompt but still loads the installed library, so it is not an established registration fix. No installed files, global search paths, trust/security settings or persistent choice were changed. The full registration/current-and-previous-input-shape archive smoke remains open; a synthesized previous-shape archive is not proof against a historical file.

All spatial-control, source-local-clock/DST, shared-service, design-day, geometry and scientific-accuracy limits of ADR-028 remain. An accepted floor gate is not a per-source spatial gain/property identity certificate or whole-building thermal equivalence. New office/courtyard composition requires separate executable topology/exposure/program/vertical contracts before any broader claim.

# Report input contract (schema version 1)

The full, valid input is [examples/shipping/design.json](../examples/shipping/design.json). Start from it, replace fictional content with the actual change, and keep stable IDs. All content strings are plain text; HTML is escaped. The Markdown export uses these strings literally, so repository documentation may contain normal Markdown prose. Unknown keys are rejected to catch silently ignored content.

## Root

Required keys: `schema_version: 1`, `title`, `status`, `baseline`, `summary`, `problem`, `goals`, `non_goals`, `evidence`, `invariants`, `decisions`, `views`, `flows`, `pseudocode`, `acceptance`, `rollout`, `risks`, `questions`, `omitted_views`.

`status` and decision statuses: `proposed`, `accepted`, `rejected`, `superseded`. The JSON report schema uses this vocabulary; write a standalone ADR in the repository's format if its lifecycle differs. `baseline` is `{label, revision}`; revision can be a commit SHA, a dated observation, or explicitly unknown. `goals` and `non_goals` are text arrays. At least one goal is required.

Use arrays for peer records. IDs begin with a letter and use letters, digits, `_`, or `-`; keep IDs unique within each collection. Scenario IDs are unique across flows. IDs are for linking, not display order. Reference arrays contain valid IDs from their target collection. Empty arrays are valid for inapplicable content, subject to `omitted_views` below.

## Evidence, invariants, decisions

- `evidence[]`: `{id, status, source, claim}`. Status: `observed`, `assumption`, `unknown`, `illustrative`. Observed claims require a nonempty source; other sources may be an empty string. Source is an exact path/URL or a clear provenance description. Illustrative examples trigger a warning. Proposed behavior goes in the design, not into a fabricated observed source.
- `invariants[]`: `{id, text, evidence: [evidence IDs]}`.
- `decisions[]`: `{id, title, status, context, options, choice, consequences, evidence}`; optional `supersedes` is the earlier ADR's identifier/path. Each option is `{name, tradeoffs: [text]}`. Compare at least two distinct options; `choice` is an option name. `consequences` is a text array, including meaningful drawbacks.

## Static views

`views[]`: `{id, title, kind, note, evidence, before, after}`. Kind: `context`, `services`, `entities`. A `services` view describes static responsibilities and connections; only a nonempty runtime flow satisfies `service-interactions`. `note` states abstraction level, scope, and important interpretation limits. Evidence references support baseline/contract claims; not every proposed node needs separate empirical evidence.

Each snapshot is `{nodes: [...], edges: [...]}`:

```json
{
  "nodes": [
    {"id": "order", "name": "Order", "kind": "entity", "owner": "Orders", "fields": {"id": "UUID", "state": "ready | shipped"}},
    {"id": "customer", "name": "Customer", "kind": "entity", "owner": "Identity", "fields": {"id": "UUID"}}
  ],
  "edges": [
    {"id": "places", "from": "customer", "to": "order", "label": "places", "cardinality": "1 Customer : 0..n Orders"}
  ]
}
```

Node kind: `actor`, `system`, `service`, `store`, `entity`, `external`. `fields` maps field/responsibility names to nonempty text. Same IDs across snapshots mean the same logical object, including a rename; a split needs new IDs and an explanation. Both snapshots have at least one node. Edges refer to nodes in their own snapshot; cardinality is required for entity relationships and otherwise can be `""`. Relationship labels name communication or domain meaning. The entity diagram is a directed schematic with explicit counts; it is not crow's-foot ER notation and does not encode identifying/non-identifying relationships. Mermaid exports use flowcharts with cardinality text, avoiding any reuse of ER's solid/dashed identification convention as change markers.

The builder compares the actual records. It reports added/changed/removed/unchanged nodes and edges, including fields, ownership, endpoints, and cardinality. Changes renders both paths when an edge changes. Stable union layout is preserved across comparison modes. Empty locations in Before/After are intentional memory anchors. A large model should be split into separate focused views; the renderer is a review aid, not an automatic architecture-discovery tool.

## Runtime flows

`flows[]`: `{id, title, kind, contract, evidence, participants, scenarios}`. Kind: `internal` or `third-party`. `contract` names transaction scope, ownership, data/trust, retry/idempotency/reconciliation assumptions where relevant. Participants are `{id, name, role}`. Use the same names as the static views; structural validation cannot verify that architectural correspondence.

Each scenario is `{id, title, steps, acceptance: [acceptance IDs]}`. It contains at least one step. A step is `{"from": "participant-id", "to": "participant-id", "label": "short visible message", "mode": "sync", "detail": "state and outcome"}`. Modes: `sync`, `async`, `reply`, `local`. A local step uses the same sender and receiver. Keep labels short; longer rationale belongs in `detail`. Full step details remain visible even when another step is selected. Give materially different outcomes distinct scenarios rather than hiding exceptions in a success label.

## Pseudocode, acceptance, evolution

- `pseudocode[]`: `{id, title, code, invariants: [invariant IDs], acceptance: [acceptance IDs]}`. `code` is multiline explanatory pseudocode. Each atomic local scope and external effect should be explicit.
- `acceptance[]`: `{id, title, given, when, then: [observable outcome text], status, invariants}`. At least one Then outcome. Execution status: `specified`, `not-run`, `passed`, `failed`. Passed/failed require actual test evidence in the surrounding report; the builder cannot verify execution.
- `rollout[]`: `{stage, entry, change, exit, recovery}`. Each text describes the intermediate state and check/recovery. Sequence in the array is rollout order.
- `risks[]`: `{risk, mitigation, acceptance: [acceptance IDs]}`.
- `questions[]`: `{question, affects}`. Name the decision or readiness condition it affects.
- `omitted_views[]`: `{view, reason}`. View: `big-picture`, `entities`, `service-interactions`, `third-party`, `pseudocode`, `acceptance`. Every one of these six is either present or omitted with a reason. A context view satisfies big-picture; a nonempty flow satisfies service-interactions; a third-party flow satisfies both service-interactions and third-party. A section cannot be simultaneously present and omitted.

The builder validates structure, references, and snapshot consistency. It warns about untested invariants, accepted designs retaining assumptions, and single-scenario provider flows. These checks do not establish design correctness, provider guarantees, acceptance execution, or deployment status. Review them with the evidence and current user intent.

## Dependencies and delivery

Python 3.10+ and Graphviz `dot` are required for the complete report. The script uses the standard library and never downloads packages or remote resources. The generated HTML embeds all diagrams, styles, and behavior and works offline. Build from any current directory with absolute input/output paths; the viewer resolves relative to the script's installed skill folder.

```bash
python3 <skill-dir>/scripts/build.py <design.json> --out <report-directory>
python3 <skill-dir>/scripts/build.py <design.json> --out <report-directory> --markdown-only
```

Use an output directory different from the input directory. Rebuilding replaces known generated filenames, so use a dedicated directory per report. `--markdown-only` writes JSON, Markdown, and ADRs; it does not generate an HTML report. The build completes rendering before writing so a rendering failure does not leave partially regenerated files.

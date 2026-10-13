---
name: design-change
description: Write or review an ADR, software design proposal, or architecture change. Ground the current system in evidence, explain decisions and alternatives, and show before/after entities, service interactions, third-party failures, pseudocode, and natural-language acceptance scenarios in a Markdown document and interactive visual report.
---

# Design Change

Make a change easy to understand, decide on, implement, and verify. Lead with the user-visible problem and the proposed result. Preserve enough of the existing system that a reviewer can explain what changes from memory.

## Choose the depth

An **ADR** records one significant decision: context, forces, credible alternatives, choice, consequences, status. A **design** explains how a change behaves, including runtime contracts and migration. A substantial design can link several ADRs. Match the repository's numbering, template, and decision lifecycle; preserve accepted history by writing a superseding decision.

For a narrow ADR, write the record and only the diagrams that help decide. For a design or visual architecture review, use the complete workflow below. Scale each view to the affected area: a local algorithm does not need invented services or third parties. Record why a requested view is inapplicable. Writing a design leaves the implementation proposed unless the user also asks to implement it.

Read [references/design-guide.md](references/design-guide.md) when framing options, invariants, runtime behavior, or migration. Read [references/visual-language.md](references/visual-language.md) before creating diagrams. The [research ledger](references/research.md) explains the primary-source basis and where the conventions are our synthesis.

## 1. Establish the baseline

Inspect relevant code, schemas, existing ADRs, interface definitions, tests, deployment boundaries, and third-party documentation. Name the baseline revision or observation date. Build a small evidence ledger with IDs, source paths/URLs, and what each establishes. Distinguish observed facts, assumptions, and proposed behavior; missing code remains unknown.

For new feature designs, especially substantial changes, search relevant engineer-authored technology blogs, published designs/RFCs, and official documentation. Cite exact source URLs and capture the relevant lesson, its applicability limits, and how it changes the option comparison. Scale research to the decision rather than imposing a fixed source count. If useful prior art cannot be found, record the search boundary honestly. External examples inform the proposal; current repository behavior still comes from code/docs, and provider guarantees from current official API/version documentation.

State the concrete problem, goals, non-goals, constraints, and invariants. Ask only for missing facts that materially affect the design; keep progressing on independent parts. Budget, latency, owner, delivery guarantee, and acceptance are not facts to invent.

**Done:** every claim about existing behavior has a source or is explicitly unknown; the success criteria and design constraints are visible; feature-design prior art is cited with its relevance and limits, or the research boundary is explicit.

## 2. Make the decision reviewable

Compare the status quo and credible alternatives against the same relevant forces. Explain the chosen direction, what it costs, what it simplifies, and what would make you reconsider it. Give decisions stable IDs. Keep decision status separate from implementation and test status: a proposed ADR can describe a complete design; an accepted ADR is not evidence of deployment.

**Done:** a reviewer can see why the preferred option wins, what it gives up, and which unanswered questions could change the choice. Mark acceptance only with evidence of the user's/team's decision.

## 3. Tell the design through six views

| View | Question it answers | Include |
|---|---|---|
| Big picture | Where does this change fit? | Actors, system boundary, external systems, ownership, responsibility; separate zoom levels. |
| Entity changes | What existed, and what changes? | Stable IDs in Before / Changes / After, fields, cardinality, ownership, added/changed/removed relationships, previous values. Logical entities and physical tables are named as such. |
| Service interactions | Who talks to whom? | The important runtime scenario: request/event, initiator, sync/async, payload, state transitions, transaction boundary, response and error. |
| Third-party flow | What happens across our boundary? | External authority, credentials/trust, identifiers, webhook/polling, timeout, retry budget, deduplication, unknown outcome, reconciliation. |
| Pseudocode | Which behavior must implementation preserve? | Guards, reads/writes, atomic scope, external effects, concurrency, errors; reference invariant and acceptance IDs. |
| Acceptance scenarios | How would we know it works? | Given / When / Then in domain language, observable outcomes, no-change regressions, applicable failure and race cases, measurable quality conditions. |

Start with the big picture; focus detail on what is changing or risky. Retain unchanged neighbors as landmarks. An entity diagram cannot explain temporal order; use a sequence for it. Walk the same scenario through the diagrams, pseudocode, and tests so their claims agree.

**Done:** every affected entity/relationship is accounted for, every important interaction has a defined outcome, and the same identifiers and contracts appear across views. Unresolved behavior is explicit rather than quietly completed by the diagram.

## 4. Explain getting there

Specify compatible intermediate states, rollout order, data migration/backfill, verification, ownership, observability, and retirement of the old path. State the rollback boundary: code rollback, data repair, or forward recovery. Tie each material risk to mitigation and an acceptance or quality scenario. Keep open questions actionable with the decision they affect.

**Done:** each stage has an entry condition, an observable exit condition, and a recovery path; irreversible external effects and lossy data changes are accounted for.

## 5. Build the review package

For the visual report, author one JSON source using [references/input-contract.md](references/input-contract.md). The [shipping example](examples/shipping/design.json) demonstrates the exact shape; it is explicitly fictional and is not repository evidence. Keep the schema's plain-text fields plain text. Read `scripts/build.py --help` for build options.

```bash
python3 <skill-dir>/scripts/build.py design.json --out <destination>
```

The builder needs Python 3.10+ and Graphviz `dot`. It derives changes from the two snapshots, computes one union layout, and produces `design.html` (self-contained/offline), `design.md` (including Mermaid), and one `adr-<id>.md` per decision. Report an absent dependency and still write useful Markdown by using `--markdown-only`. Use descriptive filenames/folders if the repository already has a convention. Do not edit generated output; update the JSON and rebuild.

When loaded from a raw GitHub URL, resolve supporting references against the same repository and ref. Materialize `scripts/build.py` and `assets/viewer.html` with their relative folder layout before building; the Python script loads the sibling viewer from the local skill folder. Copy the supplied example too when exercising the renderer. A Git/plugin installation already provides these resources.

Read `assets/viewer.html` only when maintaining this skill's renderer, not when producing an individual design. Rendering fixes belong in the reusable renderer; report-specific content belongs in JSON.

**Done:** the builder succeeds, references resolve, and HTML/Markdown agree. Check Before/Changes/After, scenario stepping, long labels, mobile, light/dark appearance, and reduced motion when a browser is available. Structural validation is not evidence that the design is correct or its acceptance tests have passed.

## 6. Deliver

Show the report when the environment supports opening local HTML. Hand over the Markdown, JSON source, and ADRs with the design's status, main tradeoff, and material open questions. Save in the team's documentation location when known, otherwise in task outputs. Commit, publish, send, or implement only within the user's requested scope. A proposal with open questions is a valid deliverable when those questions are clearly exposed.

# Visual language

## Keep the baseline memorable

Use stable node and relationship IDs across the two snapshots. Compute layout once from their union. Before and After keep that layout, including empty positions where a node did not exist. Changes is the union: unchanged landmarks stay visible; changed objects show old and new values; removed objects remain visible with a dashed stroke and a Removed label. Distinguish additions and changes with both text and color. Apply the same convention to edges, not just boxes.

Keep a short textual change ledger beside/below the graph: before value, proposed value, effect. A visual absence alone cannot explain a removed field or relationship. The builder derives this ledger and the statuses rather than trusting hand-authored labels. An ownership or cardinality change is a real change even if names stay the same.

The stable layout and comparison controls are this skill's synthesis, not an official requirement of C4 or ADRs. They deliberately trade compactness in each snapshot for continuity between snapshots. For a very large redesign, split into named views with shared landmarks rather than drawing the whole repository.

## Each picture answers one question

- **Context:** the actor, the system's purpose and boundary, external systems. A relationship names what moves, not "uses". Use owner/kind to distinguish our system from a provider.
- **Service structure:** runtime responsibilities and calls. Keep logical modules and deployment topology in separately named views.
- **Entities:** meaningful fields and cardinality. State whether this is logical domain or physical persistence. The arrows indicate relationship direction; cardinality labels describe counts, not execution order.
- **Sequence:** participants in stable lanes; messages numbered; explicit synchronous, asynchronous, reply, and local steps. Scenario-specific sequences carry separate success/failure/unknown-outcome paths. Numbers represent ordering in the scenario, not elapsed time.

Tie the third-party flow back to the context diagram by reusing names. State authority/trust in participant roles and the flow contract. A shaded provider lane does not establish a security guarantee.

## Reveal behavior, not decoration

Default to a complete Changes view. Before/Changes/After are deliberate controls, not automatic animation. Sequence Previous/Next controls reveal the active step while the entire scenario remains readable. The active step's durable state and outcome appear as text. Essential design content remains visible without interaction and in print.

Use diagrams with accessible names, a text ledger/step list, keyboard-accessible controls, visible focus, reduced-motion support, and light/dark contrast. Fit surrounding text and controls to narrow widths; allow explicit graph scrolling instead of shrinking node text below readable size. Export Markdown with Mermaid diagrams plus equivalent tables/scenarios so a non-interactive review retains the substance.

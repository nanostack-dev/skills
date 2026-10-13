# Design reasoning

## Decision and evidence

Identify the decision's scope and reversibility. Capture the forcing function: why now, what constraint prevents the status quo from meeting the goal? Compare options against relevant criteria such as correctness, operator load, compatibility, latency, cost, ownership, and simplicity. Quantitative claims need a source, a measurement, or an explicit target/assumption. Do not invent scoring weights to make a favored option win.

Use proposed, accepted, rejected, or superseded status according to the repository convention. A later discovery changes a design proposal; a later decision supersedes an accepted record. Describe favorable and unfavorable consequences. An ADR should still explain the decision after the implementation has changed.

## Domain and interfaces

Describe entity identity, lifecycle, cardinality, ownership, and invariants before schema fields. Distinguish authoritative state from cache/projection and external provider records from local records. A rename retains logical identity; a split/merge names its mapping explicitly. ID stability in a diagram is a presentation aid, not a promise that persistence IDs survive migration.

Expose a small interface that hides the actual complexity. List caller-visible error modes, ordering requirements, configuration, and performance conditions. Name seams where behavior genuinely varies; avoid adding hypothetical abstraction layers merely to make a picture symmetrical. Keep runtime services, logical modules, deployment units, and domain entities at clearly labeled levels.

## Runtime and external effects

For each important step identify input, ownership, sync/async, durable state, transaction scope, external effect, and observable result. A database transaction cannot atomically include a remote provider request. An outbox can couple a local state change to durable intent; delivery and consumption still need retry/deduplication semantics.

A timeout can mean **unknown outcome**, not failed effect. Retry only with the provider's verified idempotency contract, a bounded budget, and defined reconciliation. State the key's scope, payload binding, retention window, and behavior after expiry. Trace duplicate and reordered callbacks, stale workers, lease expiration, concurrent writers, malformed responses, and provider unavailability when applicable. An idempotent API is not by itself an end-to-end exactly-once guarantee.

Keep failure semantics concrete: return/persist a named state, compensate a specific effect, retry with a bound, or escalate an unresolved outcome. Model meaningful failure branches rather than writing an exhaustive catalog unrelated to the change.

## Pseudocode and acceptance

Pseudocode explains contracts rather than reproducing implementation syntax. Show checks and their order, concurrency control, local atomic changes, effect scheduling, and failure handling. Mark the start/end of each transaction. State which calls may repeat and how repeated calls behave.

Acceptance scenarios name business outcomes through Given/When/Then. Keep one behavior per scenario; use examples for meaningful input partitions. Then clauses observe outputs, durable outcomes, or externally meaningful effects. Include preserved behavior and changed behavior. For a technical invariant, use a separate contract/quality scenario instead of pretending a customer can inspect a database lock.

Trace invariant IDs to pseudocode and scenario IDs. An acceptance scenario is a specification until run; keep execution status separate. Avoid unsupported targets such as "fast"; describe conditions and bounds, or label the bound unresolved. Quality scenarios define stimulus, environment, response, and a measurable response measure.

## Evolution

Design the intermediate system, not just the final system. Use expand/migrate/contract when compatibility requires it. Account for old/new binaries, mixed schemas, data backfill, provider versions, and queued work created before the change. Define read/write authority throughout transition and how progress is measured. Remove an old path only after a named observation proves it is safe.

Rollback must account for data and external effects. A feature flag can stop new calls without undoing shipments/payments. State the last reversible stage and the forward repair after it. Pair each risk with detection and a recovery procedure, and tie those claims to acceptance scenarios.

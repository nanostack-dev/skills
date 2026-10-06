---
name: flow-suite-testing
description: Author, edit or diagnose API tests expressed as workflow graphs. Use for dependency and cleanup design, external side effects or events, environment and secret inputs, API status changes, and flow-suite failures.
---

# Flow suite testing

A flow suite tests API behavior through requests, assertions and their dependencies.
Its definitions may live in the repository, a remote service or both. Discover the
actual source of truth: a passing application build may never inspect these tests.

Use the project's documented local and CI gates. For affected-area selection and
an unavailable local runtime, follow [agent-workflow](../agent-workflow/SKILL.md).

## Discover the repository and engine

Read the repository's agent guides, test documentation, scripts, engine version,
schemas and supported management interfaces. Identify:

- Existing suites, their selection rules and the definitions each gate executes.
- The authorized test runtime, organization or tenant, environment and credentials.
- Setup dependencies, execution reports, cleanup ownership and external fixtures.
- Supported graph, assertion, variable, polling and event-collection capabilities.

Engines differ in syntax and execution semantics. Use only capabilities verified
in the current tool's help, schema, documentation or source. When binding an
unfamiliar engine or version, read [capability discovery](references/capability-discovery.md).
Record actual commands in the project guide; this skill supplies no universal CLI.

Confirm the resolved identity, tenant and environment before a mutation. Use
explicit scope selection wherever supported. An unexpected authorization error
or missing resource calls for checking that scope, rather than trying identities
until something succeeds. Work within the task's authorization and use disposable
fixtures; changes to shared variables or imported resources retain their existing
authorization requirements.

## Author and execute

1. **Survey.** Find a suite to extend, reusable request definitions and existing
   variable names. Locate every active copy or deployed revision used by the
   affected gates. Finish with a known source of truth and execution target.
2. **Design.** Sketch setup, independent branches, observations and cleanup before
   adding nodes. Identify each dependency and each owned resource to remove.
3. **Build.** Use the engine's supported editor, CLI, API or import schema. Give
   nodes stable, readable identifiers and names that agree with their assertions.
   Preserve unrelated fields when updating a definition.
4. **Validate.** Use available static validation to check references, dependencies,
   required inputs and unsupported graph shapes. Static success is a prerequisite,
   not execution evidence.
5. **Run.** Execute the affected suite on the intended source and scope, with setup
   enabled. Confirm the actual selected flows and evaluated cases. Read node
   outcomes, skipped dependencies and cleanup results, not just the suite summary.
6. **Diagnose.** Separate product assertions from setup, provider and runner failures.
   Repair the demonstrated cause and rerun the affected selection without weakening
   its assertions or hiding the failing case.
7. **Repeat.** Run consecutively to expose collisions and stale fixtures, and verify
   cleanup independently. For a new or reshaped concurrent graph, use additional
   runs to exercise ordering variation. Repeated passes sample races; they do not
   prove their absence.
8. **Connect the gate.** Register the flow through the project's supported suite
   selection and synchronize authorized copies where needed. Verify that current
   CI actually selects the changed definitions.

Completion records the tested source, engine version, resolved scope, selection,
expected and actual outcomes, repeat runs, cleanup and remaining boundaries.
Separate passed, failed, skipped and unevaluated cases. Discovery, validation and
an accepted launch are distinct from a completed execution.

## Dependencies describe reality

A chain claims that a later step needs an earlier result. Ask: does the later
step read that output or observe state the earlier step changed? If so, order
them. Otherwise, attach both to their shared prerequisite when the engine
supports independent branches.

```text
                         +-- read -> update -> verify
setup and baseline ------+-- duplicate-case assertion
                         +-- permission-case assertion
                         +-- other independent cases
all finished branches --------> observations -> cleanup -> verify removal
```

This is a dependency sketch, not an engine definition. Discover whether failed
ancestors skip only their descendants, abort unrelated branches, or cancel the
entire run. Verify the actual scheduling in execution reports; drawing branches
alone does not establish concurrency.

- Keep setup short and ordered where identity or resource creation requires it.
- Give independent mutations separate fixtures. Two branches editing the same
  record need explicit ordering or separate records.
- Make all other input valid in a negative case, so its assertion identifies one
  cause. A duplicate case must reach the duplicate rule, not fail body validation.
- Check baseline totals or empty lists **before every write in their scope**.
  Adding an unrelated writer later can invalidate that ordering. Post-write totals
  depend on all relevant writes; isolate the scope or assert a verified delta.
- Poll asynchronous projections with a bounded deadline and a precise condition
  tied to this run's resource. Search indexes and usage views may lag a committed
  write. Once the projection is ready, dependent assertions can share that result.

## Cleanup survives failure

Track owned resources as soon as creation yields an identifier, including when a
subsequent assertion fails. Cleanup waits for all relevant branches and uses the
engine's verified always/finally behavior. Confirm how it behaves after setup
failure, cancellation and skipped dependencies; an ordinary success edge is not
a guarantee that cleanup runs.

If the engine cannot provide reliable cleanup for those outcomes, use the
project's owned external teardown or resource ledger. Remove only this run's
resources. Withdraw public projections or independently surviving artifacts
before deleting their owner when the application's lifecycle requires that order.
Accept already-removed states only where the API contract makes them safe.

Verify removal through supported read-back or listing APIs and report cleanup
failure even when assertions passed. Reusing one generated idempotency key across
a request and its replay should leave the expected single effect; generating a
different key for each request tests two creations instead.

## Variables, generators and secrets

Survey existing configuration before introducing literals or new names. Base URLs,
standing accounts and environment-dependent settings belong in the project's
configuration scopes. Discover precedence between shared, flow, environment and
launch inputs; verify how unresolved values fail before sending requests.

A generator produces data that varies per run. Use it for disposable names,
addresses and correlation identifiers. Generate once and pass the resulting value
when several nodes need the same identity. Re-evaluating a generator in a child
flow or another node may produce a different value. Bind parent outputs explicitly
when the engine supports modules or subflows.

Credentials belong in supported secret storage or secure launch inputs. Verify
storage, access and redaction behavior rather than assuming every engine encrypts
values or masks results. Inspect request URLs, headers, bodies, progress events,
errors, traces and exports for leakage before sharing evidence. Survey names and
metadata without revealing values. Keep credentials out of command arguments,
definitions, commits, PR text and chat; use authorized secure provisioning paths.

If a credential was already retained in plain execution data, protecting future
inputs does not remove those copies. Record the exposure and use the project's
authorized removal and rotation procedure. Discover interpolation and escaping
rules when a payload itself contains template syntax; a variable value is not
universally exempt from another expansion pass.

## Verify external effects and emitted events

An accepted API response proves acceptance. When the feature writes elsewhere,
read back the affected record through the external system's supported interface
and assert the resource identity and fields the feature wrote. Use a bounded wait
for asynchronous effects. Reuse existing request definitions or import a schema
through the project's authorized workflow when supported. Test the integration's
effect, rather than unrelated behavior of the external system.

If the effect cannot be observed with available authorized access, state the exact
coverage boundary. A local send record does not prove delivery to the recipient.

For emitted events, arrange an isolated capture endpoint or equivalent collector
during setup. Fan in from every triggering branch to a final bounded observation
before cleanup. Use a verified always/finally path where supported so one failed
branch does not conceal unrelated event outcomes.

- Correlate each expectation with this run's resource and action, not event type
  alone. Check important payload fields and relevant authentication metadata.
- Ensure one event cannot satisfy two distinct required occurrences. Verify the
  matcher's consumption rules or implement a supported explicit matching check.
- Assert required, forbidden and duplicate events according to the actual delivery
  contract. Account for retries and event identifiers when deduplication matters.
- Use a documented observation/settling window for absence or extra-event checks.
  Seeing the first expected event does not establish that no later event arrives.
- Keep pending, missing and unevaluated expectations distinguishable from passes.
  Inspect individual matches and mismatches in the final result.
- Verify payload and diagnostics redaction before publishing captured events.

Use a single final collector for a set of independent emitted events when the
engine supports it. An intermediate callback that is a prerequisite for the next
action is a genuine dependency and may need its own wait.

## Keep contract assertions current

When a status, error code or response contract changes, locate its assertions in
all selected definitions and authorized tenant/environment copies. Update the
assertion and any display name that embeds the expected outcome in the same
change. Re-execute the affected suites on each required target and verify CI
coverage. The API contract determines the correct status; this skill keeps its
consumers aligned.

Read the earliest causal failure and its expected/actual evidence. A long skipped
tail may expose false dependencies, but setup failure or the engine's cancellation
policy can produce the same symptom. Fix the demonstrated graph or product issue.
Keep a reproduced defect and its assertion visible; use the project's documented
known-failure policy if one exists, rather than silently removing it from the gate.

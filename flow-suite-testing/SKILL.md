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
- The application revision the target serves. Compare its reported version with
  the merged change before authoring coverage; a target behind its main branch
  means a stalled deploy, which is a failure to report and leaves the change
  untestable until it ships.
- The engine version each gate executes on. A runner embedded in a CLI can lag the
  server's hosted runner; test new engine semantics on the runner that ships them.
- The client configuration each gate launches with. Keep at least one gate on the
  released client in its default configuration (no optional selection set); a gate
  that pins every option misses what most users run ([blank header](https://github.com/nanostack-dev/echopoint-cli/blob/main/docs/postmortems/2026-10-22-blank-workspace-header.md)).
- The credential each scheduled run signs in with, and when it expires. An unattended
  run signs in with an organization API key and checks it before launching; a
  person's browser session expires between runs and leaves the suite blind until
  someone signs in again ([expired session](../docs/postmortems/2026-10-26-suite-cli-session-expired.md)).
  A renewed session only moves the expiry 7 days out: the run stays at risk until an
  API key is stored, and an expiry warning goes to a human by push, not only into the
  run report ([expired again](../docs/postmortems/2026-11-05-suite-cli-session-expired-again.md)).

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
   A flow whose writes take a lock or limit scoped to a tenant (a folder tree lock,
   a per-organization quota) creates its own tenant each run: in a shared tenant every
   other run of it (the gate, a monitor, a soak) contends for the same lock, and its
   totals can only be lower bounds. In its own tenant the totals are exact
   ([suite overlapped gate](../docs/postmortems/2026-11-07-suite-overlapped-deploy-gate.md)).
   Name the scope of each lock a write takes: when it is wider than the tenant the
   flow owns (a per-product licensing lock above throwaway orgs), grep the suite for
   siblings writing in that scope, and send the write through a poll that repeats it
   while it answers the documented conflict (409 "in progress"). The gate runs flows
   in parallel; serial soaks never show the race
   ([licensing lock race](../docs/postmortems/2026-11-08-gate-licensing-lock-race.md)).
3. **Build.** Use the engine's supported editor, CLI, API or import schema. Give
   nodes stable, readable identifiers and names that agree with their assertions.
   Preserve unrelated fields when updating a definition.
4. **Validate.** Use available static validation to check references, dependencies,
   required inputs and unsupported graph shapes. Static success is a prerequisite,
   not execution evidence.
5. **Run.** Execute the affected suite on the intended source and scope, with setup
   enabled. Confirm the actual selected flows and evaluated cases. Read node
   outcomes, skipped dependencies and cleanup results, not just the suite summary.
6. **Diagnose.** Separate product assertions from setup, provider, runner and
   shared-quota failures. A rejection by a limit other callers also spend (a rolling
   launch budget, a rate limit) is a platform cause: read its scope from the error,
   count the quota's other consumers in the window (scheduled monitors and probes
   included; one whose own cadence exceeds the quota keeps it full), and fix the
   contention.
   A runner on a host that can sleep or drop its network (a laptop, a runner embedded
   in a CLI) produces host causes, not product ones: a lease-expired or job-token
   rejection, and a transport failure before any response (connection reset or
   refused, TLS, DNS; inside a loop the message carries an iteration prefix, so match
   it anywhere in the error), which fails the node because the runner replays nothing. Keep
   the host awake for the whole run, read its sleep log for the run window, and rerun
   only the interrupted flows, once; a repeat on the rerun is an outage to diagnose
   ([sleep](../docs/postmortems/2026-10-17-suite-run-host-sleep.md),
   [reset](../docs/postmortems/2026-10-21-suite-transport-reset.md)).
   Before launching, prove the host reaches the target with the suite's own client:
   a probe on another TLS stack (system curl) can pass while the client's handshakes
   go unanswered, and a launch that selects no flows is a blind run, not a result
   ([TLS blackhole](../docs/postmortems/2026-10-30-suite-host-network-tls.md)).
   Launch each tag in the workspace that holds its flows, named per tag in every
   caller (script, gate, schedule): an omitted workspace resolves to a server default
   that moves when someone adds or reorganizes workspaces, and a tag matching no flows
   means its flows moved
   ([workspace split](https://github.com/nanostack-dev/infra/blob/main/docs/postmortems/2026-11-02-ci-workspace-split.md)).
   Before the rerun, read the interrupted execution's cleanup nodes and delete what
   each one that did not complete still owns: the rerun creates its own data, so its
   green result says nothing about the first run's leftovers
   ([leaked cleanup](../docs/postmortems/2026-10-23-suite-transport-reset-leaked-cleanup.md)).
   A write reset after it was sent may still have been applied, and its cleanup
   cannot read an id from a response that never came: find what the flow created
   by a unique key it chose (an email or name with the run id) in the cleanup itself.
   Put the rerun and the leak report in every caller of the suite, the deploy gate
   first: a fix in one script leaves the gate that holds prod without it
   ([gate resets](https://github.com/nanostack-dev/ci-workflows/blob/main/docs/postmortems/2026-11-05-gate-transport-resets.md)).
   Keep one list of sample transport messages (a reset SSE stream of a child-run wait
   included) and test every caller's classifier against it; a class added to one
   caller goes into the others and the list the same day
   ([SSE reset](https://github.com/nanostack-dev/ci-workflows/blob/main/docs/postmortems/2026-11-13-gate-sse-reset-not-transport.md)).
   The callers are the local CLI script, the deploy gate and the scheduled monitors;
   a monitor reruns nothing, so read each failed scheduled run's node results for a
   transport error and uncompleted cleanups
   ([monitor transport failure](https://github.com/nanostack-dev/echopoint/blob/main/docs/postmortems/2026-11-08-monitor-transport-failure.md)).
   A flow that fails on some deploys of unchanged code and passes on others carries
   state drawn per process: a restart re-rolls it, so each replica can run a different
   order. Treat a pass after such failures as a coin flip and read the server's
   errors for every failed deploy
   ([observer order](https://github.com/nanostack-dev/anchor/blob/main/docs/postmortems/2026-10-31-tx-observer-order-deadlock.md)).
   Repair the demonstrated cause and rerun the affected selection without weakening
   its assertions or hiding the failing case.
7. **Repeat.** Run consecutively to expose collisions and stale fixtures, and verify
   cleanup independently. For a new or reshaped concurrent graph, use additional
   runs to exercise ordering variation. Repeated passes sample races; they do not
   prove their absence. Serial runs also keep the same replica placement, so run
   a new flow twice inside the full concurrent selection before a gate selects it.
   Count the selection first: a runner that caps how many flows one selection may
   launch (the Echopoint CLI refuses a tag above `--max-flows`, default 50) stops
   the whole gate at the cap: set the cap explicitly in every caller (script,
   gate) and split the selection before it fills
   ([gate tag flow cap](../docs/postmortems/2026-11-04-gate-tag-flow-cap.md)).
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
- Send each create operation's **minimum contract body** once: only the schema's
  required properties, and assert every field the server defaults against the
  contract's values. Fixtures that fill every optional field hide a server that
  requires one the contract marks optional, or defaults it to a value outside
  the enum ([status enum](https://github.com/nanostack-dev/anchor/blob/main/docs/postmortems/2026-11-04-product-user-status-enum.md)).
- Test a search filter on a fixture you own that holds a **near-miss** value (a
  name containing the searched name), so exact and substring filters answer
  differently. A lookup by name in a shared catalog breaks when another
  pipeline adds a lookalike: narrow it by every discriminator the search offers
  ([role names](https://github.com/nanostack-dev/anchor/pull/316)).
- Repeat each delete or remove the contract calls **idempotent** and assert its
  documented status on the repeat. A strict upstream behind the API can answer
  `404` there ([workspace role remove](https://github.com/nanostack-dev/echopoint/blob/main/docs/postmortems/2026-11-01-workspace-role-remove-404.md)).
- Check baseline totals or empty lists **before every write in their scope**.
  Adding an unrelated writer later can invalidate that ordering. Post-write totals
  depend on all relevant writes; isolate the scope or assert a verified delta.
  Before adding a write to an existing flow, list that flow's counts in the
  write's scope and update each one in the same edit.
- Assert each new list field's empty state on the wire: an isolated tenant with
  no data returns an empty array. Generated clients decode null and an empty array
  alike, so only the raw response tells them apart; confirm the engine's emptiness
  operator does too (an `empty` check may also pass on null).
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
failure even when assertions passed. Order each removal check before the delete
of any credential it authenticates with (the run's organization or its key):
started beside that delete, the check can lose the race and answer 401 on one
runner while passing on another
([teardown race](../docs/postmortems/2026-11-14-teardown-check-raced-org-delete.md)).
Reusing one generated idempotency key across
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

Test email addresses go to a mailbox the project owns, because invitation and
email flows deliver for real. At Nanostack every address is
`garbage+<tag>@nanostack.dev`, with a per-run tag such as `{{$runId}}`. Do not
use fake-data email generators, `example.com`, `.test` or `.invalid` domains.

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
for asynchronous effects, sized to fit the shortest run timeout among the flow's
callers (the gate and every scheduled monitor that selects its tags). An engine
that caps waits at the run timeout refuses the flow at launch; that refusal makes
no execution, so the suite runner reads it from the monitor run's launch failures
([monitor launch refusal](../docs/postmortems/2026-11-14-monitor-target-refused-at-launch.md)).
Reuse existing request definitions or import a schema
through the project's authorized workflow when supported. Test the integration's
effect, rather than unrelated behavior of the external system.

If the effect cannot be observed with available authorized access, state the exact
coverage boundary. A local send record does not prove delivery to the recipient.

For emitted events, arrange an isolated capture endpoint or equivalent collector
during setup. Fan in from every triggering branch to a final bounded observation
before cleanup. Use a verified always/finally path where supported so one failed
branch does not conceal unrelated event outcomes.

- A read served through a **per-replica cache** in front of another service lags
  a write that bypasses that service (a license patched on the provider, read
  through a client cache with a 30 s TTL). Make the poll the final check: one
  fresh replica does not make the next read fresh
  ([license cache](../docs/postmortems/2026-11-03-license-cache-gate-flake.md)).
- Correlate each expectation with this run's resource and action, not event type
  alone. Check important payload fields and relevant authentication metadata.
- A **shared collector** receives every run's events: a vendor webhook registered
  once per account or connection (Stripe, GitHub, Clerk, Resend, any integration
  capture webhook), or any endpoint that outlives one run. Concurrent runs then
  deliver the same event type to the same wait. Put the correlation check in the
  selector, the condition that decides which delivery the wait takes, so another
  run's event is skipped. Correlate on a value this run created and read from an
  upstream node's output (`$.data.object.id equals {{customer.id}}`), a loop
  variable or a flow input. A literal or an environment value matches every run's
  event. A check that runs only after the claim fails the wait on another run's
  event ([Echopoint ADR-0029](https://github.com/nanostack-dev/echopoint/blob/main/docs/adr/0029-an-integration-events-checks-select-this-runs-delivery.md)).
  Treat a compiler or build warning about an uncorrelated event as a defect.
- Write counts that hold under any claim order. Express N occurrences of one event
  as one expectation with an exact count (min N, max N), and bound a catch-all
  ("no other X") by the total the specific expectations require. A matcher may
  count an event against every expectation it satisfies, so overlapping
  expectations that relied on one-event-one-claim break when the engine changes
  that rule ([2026-10-14 postmortem](https://github.com/nanostack-dev/echopoint/blob/main/docs/postmortems/2026-10-14-webhook-wait-max-semantics.md)).
- Assert required, forbidden and duplicate events according to the actual delivery
  contract. Account for retries and event identifiers when deduplication matters.
- Use a documented observation/settling window for absence or extra-event checks.
  Seeing the first expected event does not establish that no later event arrives.
- Before a step that stops the producer (clears its endpoint, deletes it), wait for
  every event the run expects, not the first one: a delivery retried after a reset
  lands seconds later, and the producer drops it once the endpoint is gone
  ([2026-11-12 postmortem](https://github.com/nanostack-dev/skills/blob/main/docs/postmortems/2026-11-12-event-delivery-retry-after-clear.md)).
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
consumers aligned. Do this before the change merges: a post-deploy gate that
still asserts the old outcome holds every later change of that product off prod
([gate flows pinned old behaviour](https://github.com/nanostack-dev/infra/blob/main/docs/postmortems/2026-11-03-gate-flows-pinned-old-behaviour.md)).
When a check turns out to contradict the contract, search every flow for other
checks that assert the same behaviour and move them to the known-failure policy
with it; a check that pins a contract bug as correct later blocks its fix.

When the engine keeps published versions beside the editable definition, learn
which one each caller runs: an ad-hoc or gate run can take the draft while a
scheduled monitor takes the latest published version. After you update a flow
that has a published version, publish the update too, and have the suite runner
report every flow whose draft differs from its latest published version. Without
that, the gate passes on the fix and the monitor keeps failing on the old
assertion ([monitor ran a stale published flow](../docs/postmortems/2026-11-05-monitor-ran-stale-published-flow.md)).

When a request contract tightens (a new required header, parameter or field),
migrate every request the suite sends: the modules and subflows a tagged run
reaches through its callers, request definitions stored inside bodies that the
application executes, and each node's tenancy, so a value scoped to an
organization comes from the same organization as that node's credential. Prove
the migration on a build that enforces the new rule; a run against the lenient
build passes every miss ([2026-10-19 postmortem](https://github.com/nanostack-dev/infra/blob/main/docs/postmortems/2026-10-19-workspace-header-suite-migration.md)).

Read the earliest causal failure and its expected/actual evidence. A long skipped
tail may expose false dependencies, but setup failure or the engine's cancellation
policy can produce the same symptom. Fix the demonstrated graph or product issue.
Keep a reproduced defect and its assertion visible; use the project's documented
known-failure policy if one exists, rather than silently removing it from the gate.

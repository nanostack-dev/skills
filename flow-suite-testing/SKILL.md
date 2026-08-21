---
name: flow-suite-testing
description: End-to-end API testing with echopoint flows — the authoring loop, designing a flow as a branching graph rather than a chain, reusing organization and flow variables instead of hardcoding, verifying side effects at the third party, and running suites by tag on the ephemeral runner. Use this whenever you author, edit, or debug an echopoint flow that tests an API, whenever you add a test touching an external service or needing a URL, account, or key, whenever you change an HTTP status or error code in an API that flows assert on, and whenever a flow suite fails in CI. A flow written as a straight line, and a literal that should have been a variable, are the two most common defects in these suites.
---

# Flow suite testing

An echopoint flow is a graph of HTTP request nodes with assertions. A suite of them is a black-box
end-to-end test of an API: it runs against a deployed environment, over the real network, using the
same interface a customer would.

The flows are stored in echopoint, not in the repository of the service they test. That is the fact
everything else here follows from. Nothing in the service's build sees them, so no compiler, linter,
or unit test will tell you that a change broke one.

## Run a suite

```
echopoint flows run --tag <tag> --environment <env>
```

`flows run` uses the **ephemeral runner**: no cloud runner, no CI job, no deploy. Run it whenever you
want the answer, including before you push.

- `--tag` selects by tag, repeats, and takes `--match-mode any|all`. Tag flows by the service or
  feature they cover so a suite is one command.
- `--environment` names the environment overlay to apply.
- `--verbose` prints each node's name, status, and duration — the fastest way to see whether a
  fan-out is actually running concurrently.
- `--parallel N` runs N flows at once. Leave it at 1 while diagnosing.
- One flow: `echopoint flows run <flow-id> --environment <env>`.
- `echopoint flows validate <id>` is the static check — dangling edges, unreachable `{{node.x}}`
  references, cycles. It needs no environment.
- `flows list` has **no** `--tag` flag. Only `run` and `tag` take tags.
- `--profile <name>` picks which stored credential and organization to use. See **Organizations**.

In CI, the `nanostack-dev/echopoint-cli` action runs the same thing. A workflow that takes a tag as
an input lets anyone run a suite on demand without a deploy.

## The authoring loop

Work this loop for any new or changed flow. Steps 1 and 4 are the ones people skip, and both are
cheap.

**1. Survey what already exists.** Before writing a single node:

```
echopoint flows list                  # is there already a flow for this feature?
echopoint org env get                 # which environments and variables exist
echopoint flows env get <flow-id>
echopoint collections list            # third-party specs already imported
```

You are looking for a flow to extend rather than duplicate, variable names to reuse rather than
invent, and a collection that already describes the third party. See **Variables** — this step is
what stops literals from being baked in.

**2. Design the graph before building it.** Decide the setup chain, the branches, and the fan-in.
Write it down, even as three lines of text. Moving an edge on paper is far cheaper than after twelve
nodes exist. See **Design the flow as a graph**.

**3. Build the nodes.** Logical ids, `--after` pointed at the fan-out node, and an assertion and a
display name that agree with each other.

**4. Validate statically.** `echopoint flows validate <id>` catches dangling edges, unreachable
`{{node.x}}` references, and cycles without touching an environment. Run it before the first real
run — it turns a slow failed run into an instant message.

**5. Run it.** `echopoint flows run <id> --environment <env> --verbose`. The verbose start order is
how you confirm the fan-out runs concurrently rather than in the order you happened to add nodes.

**6. Read the failures and go back to step 3.** The node line, not the flow line. A long `Skipped`
list means the shape is wrong, not the node — fix the shape first.

**7. Run it twice in a row.** A flow that passes once and fails the second time did not clean up
after itself, and it will fail for the next person instead. This is the check that catches a fixed
literal where a generated value belonged.

**8. Tag it, and mirror it wherever the suite lives.** A flow nothing selects is a flow nobody runs.

## Design the flow as a graph, not a line

This is where flow tests are usually got wrong, so spend your thinking here rather than on node
count. The instinct when adding a case is to hang it off the last node you added. Do that a few
times and you have `setup → case 1 → case 2 → case 3 → cleanup`: a chain that *claims* case 2
depends on case 1. It almost never does.

**A chain is a claim about dependency. Make it only when the claim is true.**

The engine runs every node whose predecessors have finished, concurrently. So the shape you draw is
the parallelism you get, and drawing a line throws it away. But speed is the smaller loss. The real
cost is diagnosis:

> **A failed node marks everything downstream `Skipped`.**

One real failure in a chain of eight hides the other seven. From a real run of a products flow:

```
Node Create 1-char Name (400) failed: assertion 0 failed: statusCode equals expected=400 actual=409
Node Search Products      failed: Skipped because step "Create 1-char Name (400)" failed earlier
Node Update Empty Name    failed: Skipped ...
Node Update Product       failed: Skipped ...
Node Create Duplicate     failed: Skipped ...
Node Get Product          failed: Skipped ...
Node Delete Product       failed: Skipped ...
Node Verify Gone (404)    failed: Skipped ...
```

Eight nodes, one genuine result, seven unknowns — and the cleanup never ran, so the run leaked its
fixtures. Those seven cases are independent: none reads an output of `Create 1-char Name`. Hung off
`setup` instead, that run would have reported all eight verdicts at once and still cleaned up.

Chains turn each run into one bit of information. Branches give you the whole feature per run.

### The shape to reach for

```
                  ┌── happy path: get → update → delete → verify-gone (404)
                  ├── duplicate name (409)
   setup ─────────┼── empty name (400)                                    ──────► cleanup
   (log in,       ├── name too long (400)                                  (run-when always)
    create the    ├── unauthorized (401)
    fixtures)     └── missing permission (403)
```

- **Setup is a genuine chain.** Log in, create the parent resource, mint a key — each really does
  need the one before. Keep it linear and as short as it can be.
- **Every case is a branch off setup.** Independent cases are siblings, never a queue.
- **A branch may itself be a short chain** when the steps are truly ordered:
  `get → update → delete → verify-gone` is a real sequence, because each reads the last one's
  effect. That is one branch, not four.
- **Cleanup fans in.** Give it `--run-when always` and an edge from every branch, so it runs even
  when a branch fails and the run does not leak fixtures.

### The test for "chain or branch?"

Ask of any two nodes: **does B read an output of A, or observe state that A changed?**

- Yes → chain them. `verify-gone` must follow `delete`.
- No → they are siblings. Hang both off the common ancestor.

Negative cases are the easiest call: they assert a 4xx and change nothing, so they can essentially
always be siblings. Five validation cases in a row are five branches.

### Where chains creep in

`flows node add --after <node>` wires a success edge for you, which is a real convenience — and it
is also how a chain forms without anyone deciding to build one, because the node you just added is
the one nearest to hand. **Point `--after` at the fan-out node, not at your previous node**, unless
you actually mean "after that specific step". Naming the fan-out node something obvious (`setup`)
makes the right target easy to reach for.

### When a branch genuinely cannot be parallel

Two branches that mutate the same row must be ordered, or they race. Prefer giving each branch its
own fixture — create two resources rather than sequencing two renames of one. Separate fixtures
scale to any number of cases; sequencing does not, and it re-introduces the chain you were avoiding.

### One flow per feature

Prefer one flow covering a whole feature through many branches over many small single-case flows. A
feature flow pays for its setup once, reports every case in a single run, and cleans up in one
place. Split only when a case needs a genuinely different setup.

## Variables: look before you hardcode

A `{{name}}` that is not a node output is a **variable**, and the runner resolves it from three
places. Knowing which one to use is most of the skill here.

| Scope | Command | Use it for |
|---|---|---|
| Organization environment | `echopoint org env get` / `set` | anything every flow in the organization shares — base URLs, a CI credential, a standing test account |
| Flow environment | `echopoint flows env get/set <flow-id>` | a value only this flow needs, or one that must differ from the organization default |
| Flow input | none — it is inferred | any `{{name}}` still unresolved at launch |

Both environments carry **named overlays**, which is what `--environment` selects, plus an unnamed
base. A flow-level value wins over the organization's for the same name. Anything left unresolved
becomes a required input and the launch fails with `unknown initial variable`, rather than sending a
request with an empty string — an unresolved reference is loud, not silent.

**Survey before you invent.** If the organization already defines a base URL, a test account, or an
API key, use that name. Writing `https://api.example.com` into a node is not wrong today; it is
invisible on the day the host changes, and it makes the flow unrunnable against any other
environment. Run `org env get` first and reuse what is there.

**Reuse silently, create with permission.** If the value you need already has a name, use it — no
need to ask, and asking about an existing base-URL variable is noise. If you are about to bake in a
literal that clearly *should* be a variable — a host, an account, a key, anything
environment-shaped — say so and offer to add it, naming the scope you would put it in and why. An
organization variable is shared state that outlives your flow and affects everyone else's, so
creating one is the user's call, not a side effect of writing a test.

**A value that varies per run is not a variable — it is a generator.** `{{$email}}`, `{{$slug:3}}`,
`{{$int:1:100}}`, `{{$uuid}}` come from the runner's own namespace and differ every execution. Reach
for these for anything a test creates. A fixed name in a create request is the leading cause of a
flow that passes once and collides forever after.

**Environment values can be secrets.** `env get` shows names only; `--show-values` reveals them, and
is worth typing out deliberately rather than by habit. Surveying never needs it. Whatever you do
reveal, do not paste it into a pull request, an issue, a commit, or a chat message.

## One assertion, one cause

An assertion that can pass for two different reasons tests neither. Two real examples, both green
for a long time, both exposed only when an API split one 400 into 400 and 409:

- a duplicate-create node sent a **truncated payload**, so validation refused it before the
  duplicate check ran — it asserted "duplicate → 400" while measuring "invalid body → 400";
- a node asserted a minimum-name-length rule that did not exist, and passed only because a leftover
  fixture made every run collide instead.

When you write a negative node, make everything except the one condition under test valid, and give
it a fixture the run creates itself. If a node's premise depends on data a previous run left behind,
it is not a test. The `{{$...}}` generators exist for exactly this.

## Verify the effect at the third party

When the feature under test writes to a third party — a payment provider, an identity provider, a
mail relay, a repository host — your API answering `201` proves only that it accepted the request.
It does not prove anything arrived. If the feature's whole job is to put data somewhere else, a test
that stops at your own response is testing the handler, not the feature.

So add a node that reads the record back **from the third party** and asserts on it. That node is a
branch off the one that caused the side effect, and it is usually the most valuable node in the
flow: it is the only one that would catch a silently dropped field, a wrong id mapping, or a
provider that accepted the call and did nothing.

**Import the third party's OpenAPI spec so you have real requests to send.** Echopoint turns a spec
into a collection of request definitions a flow can call:

```
echopoint collections import --file <spec.yaml> --name "<API name>"
```

Check `echopoint collections list` first — a shared organization often already has the common ones.

**Offer this when the situation calls for it.** If you are authoring or extending a flow for a
feature that talks to a third party, and no collection for that API exists yet, say so and ask
whether to import it, pointing at the vendor's published spec. Most vendors publish one, and it is a
minute of work that upgrades every future test of that integration. Do not import silently — it adds
a shared resource to the organization, so it is the user's call.

Three things to keep in mind:

- **Credentials belong in an environment**, never in a node body — see **Variables**. A vendor key
  is organization-scoped if several flows call that vendor, flow-scoped if only one does.
- **Confirm the effect; do not test the vendor.** One read-back assertion on the fields you wrote is
  the goal. Exercising the third party's own behaviour makes the suite slow and flaky for no return.
- **Some effects are not readable, and that is a legitimate skip.** Delivery of an actual email is
  the standing example — confirming it needs a live relay and a mailbox. Prefer asserting the record
  you control (the send record, the webhook event row) and say plainly in the flow what is not
  covered.

## Organizations

Flows belong to an organization. Teams commonly keep a separate organization for CI so that a broken
hand-run cannot affect the pipeline, which means **the same flow exists more than once, with a
different id in each**. Fixing one copy does not reach the other.

`echopoint profile list` shows the stored profiles; `echopoint auth status --profile <p>` prints the
organization one resolves to. A flow id that answers 404 under one profile is not missing — try the
other. Apply every change everywhere the flow lives, and re-run each.

## Before you change a status, a code, or a contract

These assertions are the only consumer of your API's error statuses with **no compile-time check**.
A status change passes the build, the linter, and every unit and integration test, then fails the
flow suite — often after the service is already deployed.

In the same change that moves a status:

1. Find the `statusCode` assertions on the affected route, in every organization the suite lives in.
2. Update the assertion **and** the node's display name — names carry the status, so a node reading
   `Duplicate Slug (400)` becomes `Duplicate Slug (409)`.
3. Re-run the tag everywhere.

Which status is *correct* is your API's own convention. This skill covers only keeping the suites in
step with it.

## Authoring mechanics

Build flows through the CLI (`flows node add`, `flows edge add`, `--after`), not by hand-writing
JSON. `flows update --file` takes an `UpdateFlowRequest` and merges field by field, so sending only
`flow_definition` leaves name, tags, and folder untouched — the safe way to script an edit.

- **Node ids are logical**, not UUIDs: `create-product`, `dup-create`, `login-badpass`. Templates
  read `{{create-product.productId}}`, and runner errors name the failing node.
- **Display names carry the expected status** in parentheses. Keep them true; a name disagreeing
  with its assertion is how a stale suite hides.
- Any node can read any upstream node's output — `{{nodeId.key}}` reaches across branches, so a
  fan-out costs nothing in wiring.
- Modules are reusable sub-flows and nest several levels: a child exports with
  `--output name=childNode.key` and the parent reads `{{moduleNode.name}}`. Give a module a name
  that marks it as one, and keep it out of suite runs — it owns no cleanup of its own.
- Run `flows validate <id>` after wiring and before the first real run.

## When a suite fails

Read the node line, not the flow line: a flow reports its first failure and marks everything
downstream `Skipped`, so the real cause is the one node with an `assertion N failed` message.
`expected=X actual=Y` tells you which side moved. Decide which is wrong — the service or the
assertion — and fix that one. Never relax an assertion to make a run green.

If the `Skipped` list is long, that is the flow telling you it is a chain. Fixing the shape is
usually worth more than fixing the one node, because the next failure will hide the same seven cases
again.

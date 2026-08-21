---
name: flow-suite-testing
description: End-to-end API tests written as echopoint flows for anchor and echopoint — the authoring loop, designing a flow as a branching graph rather than a chain, reusing organization and flow variables instead of hardcoding, verifying side effects at the third party, running suites by tag on the ephemeral runner, and keeping assertions in step with a status change. Use this whenever you author, edit, or debug a flow test, whenever you add a test that touches an external API or needs a URL, account, or key, whenever you change an HTTP status or error code in anchor or echopoint, and whenever a post-deploy flow-suite job fails. A flow written as a straight line, and a literal that should have been a variable, are the two most common defects in this suite.
---

# Flow suite testing

Anchor and echopoint are both tested end to end by **echopoint flows**. Each test is a flow held in
the echopoint database, and the graph of request nodes IS the test. Nothing lives in either
service's repository, so nothing in either build sees them.

| Tag | Flows | Covers |
|---|---|---|
| `anchor` | 17 | the anchor API |
| `echopoint` | 8 | the echopoint API — webhooks, flows, collections, schedules, openapi-sync, SSE streams |

For Go tests **inside** the echopoint backend — unit, CT, service, repository — use echopoint's own
`echopoint-testing` skill. This skill is only about the flows.

## Run a suite

```
echopoint flows run --tag anchor --environment dev --profile prod
```

`flows run` uses the **ephemeral runner**: no cloud runner, no CI job, no deploy. Run it whenever
you want the answer, including before you push.

- `--tag` selects by tag, repeats, and takes `--match-mode any|all`.
- `--environment` names the environment to overlay. The flows target `dev` even from the prod org.
- `--verbose` prints each node's name, status, and duration — the fastest way to see your fan-out
  actually running concurrently.
- `--parallel N` runs N flows at once. Leave it at 1 while diagnosing.
- One flow: `echopoint flows run <flow-id> --environment dev --profile prod`.
- `echopoint flows validate <id>` is the static check — dangling edges, unreachable `{{node.x}}`
  refs, cycles. It needs no environment.
- `flows list` has **no** `--tag` flag. Only `run` and `tag` take tags.

CI runs the same command through the `nanostack-dev/echopoint-cli@v1` action. `infra`'s
`anchor-test.yml` is an on-demand workflow taking a tag, so a suite can run from CI without a deploy.

## The authoring loop

Work this loop for any new or changed flow. Steps 1 and 4 are the ones people skip, and both are
cheap.

**1. Survey what already exists.** Before writing a single node:

```
echopoint flows list --profile prod            # is there already a flow for this feature?
echopoint org env get --profile prod           # which environments and variables exist
echopoint flows env get <flow-id> --profile prod
echopoint collections list --profile prod      # third-party specs already imported
```

You are looking for a flow to extend rather than duplicate, variable names to reuse rather than
invent, and a collection that already describes the third party. See **Variables** below — this
step is what stops literals from being baked in.

**2. Design the graph before building it.** Decide the setup chain, the branches, and the fan-in.
Write it down, even as three lines of text. It is far cheaper to move an edge on paper than after
twelve nodes exist. See **Design the flow as a graph**.

**3. Build the nodes.** Logical ids, `--after` pointed at the fan-out node, an assertion and a
display name that agree with each other.

**4. Validate statically.** `echopoint flows validate <id>` catches dangling edges, unreachable
`{{node.x}}` references, and cycles without touching an environment. Run it before the first real
run — it turns a slow failed run into an instant message.

**5. Run it.** `echopoint flows run <id> --environment dev --verbose --profile prod`. `--verbose`
shows the nodes' start order, which is how you confirm the fan-out is actually running concurrently
rather than in the order you happened to add them.

**6. Read the failures and go back to step 3.** The node line, not the flow line. A long `Skipped`
list means the shape is wrong, not the node — fix the shape first.

**7. Run it twice in a row.** A flow that passes once and fails the second time did not clean up
after itself, and it will fail for the next person instead. This is the check that catches a fixed
literal where a `{{$...}}` value belonged.

**8. Tag it, mirror it, run both.** `echopoint flows tag` with the service name, apply the same
change in the other organization, and run the tag against both profiles. A flow is not done until
both orgs are green.

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

One real failure in a chain of eight hides the other seven. From an actual run of `anchor: product`:

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
   (login,        ├── name too long (400)                                  (run-when always)
    product,      ├── unauthorized (401)
    key)          └── missing scope (403)
```

- **Setup is a genuine chain.** Log in, create the product, mint the key — each really does need the
  one before. Keep it linear and make it as short as it can be.
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
always be siblings. If you have five validation cases in a row, that is five branches.

### Where chains creep in

`flows node add --after <node>` wires a success edge for you, which is a real convenience — and it
is also how a chain forms without anyone deciding to build one, because the node you just added is
the one nearest to hand. **Point `--after` at the fan-out node, not at your previous node**, unless
you actually mean "after that specific step". Naming the setup node something obvious (`setup`)
makes the right target easy to reach for.

### When a branch genuinely cannot be parallel

Two branches that mutate the same row must be ordered, or they race. Prefer giving each branch its
own fixture — create two products rather than sequencing two renames of one. Separate fixtures scale
to any number of cases; sequencing does not, and it re-introduces the chain you were avoiding.

### One flow per feature

Prefer one flow that covers a whole feature through many branches over many small single-case
flows. A feature flow pays for its setup once, reports every case in a single run, and cleans up in
one place. Split only when a case needs a genuinely different setup.

## Variables: look before you hardcode

A `{{name}}` that is not a node output is a **variable**, and the runner resolves it from three
places. Knowing which one to use is most of the skill here.

| Scope | Command | Use it for |
|---|---|---|
| Organization environment | `echopoint org env get` / `set` | anything every flow in the org shares — base URLs, the CI credential, a standing test account |
| Flow environment | `echopoint flows env get/set <flow-id>` | a value only this flow needs, or one that must differ from the org default |
| Flow input | none — it is inferred | any `{{name}}` still unresolved at launch |

Both environments carry **named overlays**, which is what `--environment dev` selects, plus an
unnamed base. A flow-level value wins over the organization's for the same name. Anything left
unresolved becomes a required input, and the launch fails with `unknown initial variable` rather
than sending a request with an empty string — which is why an unresolved reference is loud rather
than silent.

**Survey before you invent.** The organization already defines, in its `dev` overlay:
`nanostackBaseUrl`, `echopointUrl`, `echopointApiKey`, `email`, `password`, `githubUrl`. A new
anchor flow writes `{{nanostackBaseUrl}}`, never `https://apidev.echopoint.dev` — not because
literals fail today, but because the literal is invisible on the day the host changes, and it makes
the flow unrunnable against any other environment. Run `org env get` first and reuse what is there.

**Reuse silently, create with permission.** If the value you need already has a name, use it — no
need to ask, and asking about `{{nanostackBaseUrl}}` is noise. If you are about to bake in a literal
that clearly *should* be a variable — a host, an account, a key, anything environment-shaped — say
so and offer to add it, naming the scope you would put it in and why. Organization variables are
shared state that outlive your flow and affect everyone else's, so creating one is the user's call,
not a side effect of writing a test.

**A value that varies per run is not a variable — it is a generator.** `{{$email}}`, `{{$slug:3}}`,
`{{$int:1:100}}`, `{{$uuid}}` come from the runner's own namespace and differ every execution. Reach
for these for anything a test creates. A fixed name in a create request is the leading cause of a
flow that passes once and collides forever after.

**Treat `org env get` output as secret material.** It prints values in cleartext, API keys included.
Never paste it into a pull request, an issue, a commit, or a chat message — read the key *names* and
quote those.

## One assertion, one cause

An assertion that can pass for two different reasons tests neither. Both known cases in this suite
sat green a long time and surfaced only when a 400 split into 400 and 409:

- a duplicate-create node sent a **truncated payload**, so config validation refused it before the
  duplicate check ran — it asserted "duplicate → 400" while measuring "invalid config → 400";
- a node asserted a minimum-name-length rule that does not exist, and passed only because a
  leftover fixture made every run collide instead.

When you write a negative node, make everything except the one condition under test valid, and give
it a fixture the run creates itself. If a node's premise depends on data a previous run left behind,
it is not a test. `{{$email}}`, `{{$slug:3}}`, and friends exist for exactly this.

## Verify the effect at the third party

When the feature under test writes to a third party — a payment provider, an identity provider, a
mail relay, a repository host — our API answering `201` proves only that we accepted the request. It
does not prove anything arrived. If the feature's whole job is to put data somewhere else, a test
that stops at our own response is testing the handler, not the feature.

So add a node that reads the record back **from the third party** and asserts on it. That node is a
branch off the one that caused the side effect, and it is usually the most valuable node in the
flow: it is the only one that would catch a silently dropped field, a wrong id mapping, or a
provider that accepted the call and did nothing.

**Import the third party's OpenAPI spec so you have real requests to send.** Echopoint turns a spec
into a collection of request definitions you can call from a flow:

```
echopoint collections import --file <spec.yaml> --name "Stripe API" --profile prod
```

Check what is already there before importing — `echopoint collections list` — since a shared org
usually has the common ones. The CI organization already carries `Stripe API` and `Github API`
alongside the internal ones.

**Offer this when the situation calls for it.** If you are authoring or extending a flow for a
feature that talks to a third party, and no collection for that API exists yet, say so and ask
whether to import it, pointing at the vendor's published spec. Most vendors publish one, and it is a
minute of work that upgrades every future test of that integration. Do not import silently — it adds
a shared resource to the organization, so it is the user's call.

Three things to keep in mind:

- **Credentials belong in an environment**, never in a node body — see **Variables** above. A
  vendor key is organization-scoped if several flows call that vendor, flow-scoped if only one does.
- **Confirm the effect; do not test the vendor.** One read-back assertion on the fields we wrote is
  the goal. Exercising the third party's own behaviour makes the suite slow and flaky for no return.
- **Some effects are not readable, and that is a legitimate skip.** Delivery of an actual email is
  the standing example — the suite deliberately does not cover `sendEmail`, because confirming it
  would need a live relay and a mailbox. Prefer asserting the record we control (the send record,
  the webhook event row) and say plainly in the flow what is not covered.

## The flows live in two organizations

Every flow exists twice, with a **different id in each org**. Fixing one does not reach the other.

| Profile | Used by |
|---|---|
| `prod` | the deploy pipelines (`ECHOPOINT_CI_ORG_ID`, from 1Password `infra-control-plane`) |
| `dev` | hand runs |

`echopoint profile list` shows the profiles; `echopoint auth status --profile <p>` prints the org one
resolves to. A flow id that answers 404 on `dev` is not missing — retry it on `prod`. Apply every
change to both orgs and re-run both.

## Before you change a status, a code, or a contract

These assertions are the only consumer of the two APIs' error statuses with **no compile-time
check**. A status change passes `go build`, the linter, and every Go test, then fails the
post-deploy flow-suite job with the service already on dev.

In the same change that moves a status:

1. Scan both orgs for `statusCode` assertions on the affected route.
2. Update the assertion **and** the node's display name — names carry the status, so a node reading
   `Duplicate Slug (400)` becomes `Duplicate Slug (409)`.
3. Re-run the tag against both profiles.

Which status is correct is decided by `docs/engineering-best-practices.md` in either repo, section
`HTTP error statuses`. This skill covers only keeping the suites in step with it.

## Authoring mechanics

Build flows through the CLI (`flows node add`, `flows edge add`, `--after`), not by hand-writing
JSON. `flows update --file` takes an `UpdateFlowRequest` and merges field by field, so sending only
`flow_definition` leaves name, tags, and folder untouched — the safe way to script an edit.

- **Node ids are logical**, not UUIDs: `create-product`, `dup-create`, `login-badpass`. Templates
  read `{{create-product.productId}}`, and runner errors name the failing node.
- **Display names carry the expected status** in parentheses. Keep them true; a name disagreeing
  with its assertion is how a stale suite hides.
- Any node can read any upstream node's output — `{{nodeId.key}}` reaches across branches, so a
  fan-out costs you nothing in wiring.
- Modules are reusable sub-flows and nest several levels; a child exports with
  `--output name=childNode.key` and the parent reads `{{moduleNode.name}}`. A flow named `(module)`
  is skipped by suite runs because it owns no cleanup.
- Tag a new flow with its service (`echopoint flows tag`) or the suite will not run it.
- Run `flows validate <id>` after wiring and before the first real run.

## When a suite fails

Read the node line, not the flow line: a flow reports its first failure and marks everything
downstream `Skipped`, so the real cause is the one node with an `assertion N failed` message.
`expected=X actual=Y` tells you which side moved. Decide which is wrong — the service or the
assertion — and fix that one. Never relax an assertion to make a run green.

If the `Skipped` list is long, that is the flow telling you it is a chain. Fixing the shape is
usually worth more than fixing the one node, because the next failure will hide the same seven cases
again.

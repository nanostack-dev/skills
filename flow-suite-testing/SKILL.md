---
name: flow-suite-testing
description: The end-to-end API suites for anchor and echopoint, authored as echopoint flows and run on the ephemeral runner — running them by tag, the two organizations their flows live in, authoring nodes and assertions, and the rule that a status or contract change must be checked against them before merge. Load before changing an HTTP status or error code in anchor or echopoint, before editing or adding a suite flow, and when a post-deploy flow-suite job fails.
---

# Flow suite testing

Anchor and echopoint are both tested end to end by **echopoint flows**. Each test is a flow stored
in the echopoint database, and the graph of request nodes IS the test. Nothing lives in either
service's repository, so nothing in either build sees them.

Two tags, one per service:

| Tag | Flows | Covers |
|---|---|---|
| `anchor` | 17 | the anchor API |
| `echopoint` | 8 | the echopoint API — webhooks, flows, collections, schedules, openapi-sync, SSE streams |

For Go tests **inside** the echopoint backend — unit, CT, service, repository — use echopoint's own
`echopoint-testing` skill instead. This skill is only about the flows.

## Run a suite

```
echopoint flows run --tag anchor --environment dev --profile prod
```

`flows run` uses the **ephemeral runner**: no cloud runner, no CI job, no deploy. Run it whenever
you want the answer, including before you push.

- `--tag` selects by tag, repeats, and takes `--match-mode any|all`.
- `--environment` names the environment to overlay. The flows target `dev` even from the prod org.
- `--verbose` prints each node's name, status, and duration.
- `--parallel N` runs N flows at once. Leave it at 1 while diagnosing.
- One flow: `echopoint flows run <flow-id> --environment dev --profile prod`.
- `echopoint flows validate <id>` is the static check — dangling edges, unreachable `{{node.x}}`
  refs, cycles. It needs no environment.
- `flows list` has **no** `--tag` flag. Only `run` and `tag` take tags.

CI runs the same command through the `nanostack-dev/echopoint-cli@v1` action. `infra`'s
`anchor-test.yml` is an on-demand workflow that takes a tag, so a suite can be run from CI without a
deploy.

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
2. Update the assertion **and** the node's display name — the names carry the status, so a node
   reading `Duplicate Slug (400)` becomes `Duplicate Slug (409)`.
3. Re-run the tag against both profiles.

Which status is correct is decided by `docs/engineering-best-practices.md` in either repo, section
`HTTP error statuses`. This skill covers only how the suites are kept in step with it.

## One assertion, one cause

An assertion that can pass for two different reasons tests neither. Both known cases sat green for
a long time and surfaced only when 400 split into 400 and 409:

- a duplicate-create node sent a **truncated payload**, so config validation refused it before the
  duplicate check ran — it asserted "duplicate → 400" while measuring "invalid config → 400";
- a node asserted a minimum-name-length rule that does not exist, and passed only because a
  leftover fixture made every run collide instead.

When you write a negative node, make everything except the one condition under test valid, and give
it a fixture the run creates itself. If a node's premise depends on data a previous run left behind,
it is not a test.

## Authoring

Build flows through the CLI (`flows node add`, `flows edge add`, `--after`), not by hand-writing
JSON. `flows update --file` takes an `UpdateFlowRequest` and merges field by field, so sending only
`flow_definition` leaves name, tags, and folder untouched — that is the safe way to script an edit.

- **Node ids are logical**, not UUIDs: `create-product`, `dup-create`, `login-badpass`. Templates
  read `{{create-product.productId}}`, and runner errors name the failing node.
- **Display names carry the expected status** in parentheses. Keep them true; a name that disagrees
  with its assertion is how a stale suite hides.
- `--run-when always` makes a cleanup node run even after an upstream failure.
- A negative test is an ordinary node asserting a 4xx.
- Flows are smart DAGs: fan out independent branches off a setup node, fan in at cleanup, and let a
  cascade delete clean up.
- Modules are reusable sub-flows. A flow named `(module)` is skipped by suite runs because it owns
  no cleanup.
- Dynamic values use their own namespace: `{{$email}}`, `{{$slug:3}}`, `{{$int:1:100}}`. Prefer them
  over fixed literals, so a re-run cannot collide with its own leftovers.
- Tag a new flow with its service — `echopoint flows tag` — or the suite will not run it.

## When a suite fails

Read the node line, not the flow line: a flow reports its first failure and marks everything
downstream `Skipped`, so the real cause is the one node with an `assertion N failed` message.
`expected=X actual=Y` tells you which side moved. Then decide which is wrong — the service or the
assertion — and fix that one. Do not relax an assertion to make a run green.

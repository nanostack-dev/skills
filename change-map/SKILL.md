---
name: change-map
description: Turn a pull request or in-progress branch into an interactive, picture-first review page that a human can approve without reading the diff. Shows a system diagram of what is new, the decisions to approve, animated step-by-step scenarios, the lifecycle, an ER schema, the guards per operation, the API, the tests as Given/When/Then, and how much of the diff is noise. Use when asked to visualize, map, or explain a PR or ongoing work, to prepare a change for review, to "make this PR reviewable", or when a diff is too large to read, is mostly generated code, or mixes schema, entity, logic and noise.
---

# Change map

A change map is one page that answers what a reviewer has to decide. The reviewer looks at the pictures, reads the decisions and the risks, and approves or questions each decision. They open code only through the file links on the page.

**Picture first.** A reviewer has already read too much text. Every fact that can be a diagram, a scenario or a table goes there, and prose only carries what a picture cannot: why, and what it costs. One concrete example (Ana at Acme, `ana@acme.io`, token `anchor_inv_7Hk…`) beats a paragraph of abstraction.

The page has two parts, and you write only one of them:

- **The viewer** (`viewer.html`) is a fixed, designed renderer. It owns every pixel: layout, theme, diagrams, animation, the review tally. Never edit it for one change, and never write HTML, CSS or SVG for a change map.
- **The data** (`change.json`) is what you write. A script fills its mechanical half. You fill the judgment half: about 22 KB of JSON for a 12,000-line PR, plus 15 KB of Given/When/Then rows a cheap subagent writes.

That split keeps the page good-looking and cheap: the design is done once, and each change costs only its facts.

## Files

When the skill is installed, the files sit next to this one. On a cloud worker, fetch them:

```
base=https://raw.githubusercontent.com/nanostack-dev/skills/main/change-map
curl -fsSLO $base/scripts/triage.py -fsSLO $base/scripts/build.py -fsSLO $base/viewer.html
```

`examples/anchor-142.json` is a finished map of a real 47-file PR. Read it before your first map. It is the quality bar.

## Steps

### 1. Triage

```
python3 scripts/triage.py --pr <number> [--repo owner/name] -o change.json --diff-out review.diff --tests-out tests.diff
python3 scripts/triage.py --range main...HEAD -o change.json --diff-out review.diff --tests-out tests.diff   # no PR yet
```

The script sorts every file into a bucket (generated, tests, schema, contract, logic, wiring, docs), extracts test names, writes `review.diff` with only the files a human must read, and `tests.diff` with the test files. It prints the split to stderr.

Add `--generated '<glob>'` for any generated path it missed, and rerun. Done when no generated or vendored file sits in a read bucket.

### 2. Read only what matters

Read `review.diff`, the PR body, and the commit messages. Never read generated files. Leave `tests.diff` to step 4.

### 3. Fill the judgment half

Write these keys into `change.json`. Keep strings short and plain. Backticks render as code. Leave out any section that does not apply, and the viewer hides it.

| Key | What it holds | Cap |
|---|---|---|
| `summary` | What the change does for its consumer, 2 sentences | |
| `verdict` | `risk` (low, medium, high), `door` (one-way, two-way), `doorNote`, `ask`: one sentence naming what the reviewer approves | |
| `system` | `{cols: [header], nodes: [{id, label, sub, kind, col, row, status}], edges: [{from, to, label, status}]}` | 12 nodes |
| `decisions` | `{id, tag, title, why, choice, instead, cost, refs, see}` | 7 |
| `watch` | `{id, sev, title, body, ref}`, `sev` is risk, question, nit or note | 6 |
| `scenarios` | `{id, title, caption, actors: [{id, label, sub, kind}], board, steps}` | 4 scenarios, 12 steps |
| `model` | `{entity, hint, states: [{id, label, note, tone, derived}], transitions: [[from, to, label]], ops: {cols, rows, edges, note}}` | 5 states |
| `schema` | `{hint, tables: [{name, new, change, file, note, cols: [[name, type, flags, meaning]], idx: [[name, on, serves]], notes}], refs: [{name, note, cols}]}` | |
| `flows` | `{name, actor, tx: [first, last], steps: [{k, t, err}], result}`, `k` is read, lock, guard, write, emit or call | 5 flows, 8 steps |
| `api` | `{m, p, scope, emits, note}` | 16 |
| `rules` | Given/When/Then, from step 4 | 10 |
| `meta.stack`, `meta.links` | Stack position such as `"1/3"`, and `[{label, url}]` for issue, epic, ADR | |

Details the viewer relies on:

- `refs` and `ref` are `path:line` against the head commit. The viewer links them to GitHub.
- `status` on system nodes and edges is `new`, `changed` or absent. New edges animate. `kind` is person, service, api, db, queue or external. Place nodes on a grid with `col` and `row` so that edges mostly run left to right.
- `see` on a decision names a scenario id and adds a "See it run" button.
- In `model.ops`, a cell is `ok`, an HTTP status, or a short word. `edges[i]` lists the transition indexes (comma-separated) that row `i` fires, lit on hover.
- In `schema`, `flags` is comma-separated: `pk`, `fk → table`, `unique`, `null`, `cascade`. Each `fk → table` draws a line to that entry in `refs`.
- `tx` gives the step indexes, counting from 0, that run inside one transaction.

### Scenarios

A scenario is a sequence diagram the reviewer plays step by step. It is the strongest picture on the page: use it for each decision that is easier to see than to explain (a race, a token that stops working, the full round trip).

- `actors` are columns. Name real people and systems: "Admin A", "Request A", "Postgres".
- A step is `{from, to, k, label, say}`. `k` is `call`, `reply`, `error` or `block`. `label` sits on the arrow (under 40 characters). `say` is the caption for that step, one or two sentences of what is happening and why it matters.
- A `block` step with `until: i` draws a waiting bar on the `from` lifeline until step `i`. Use it for locks and queues.
- `board` is a live table beside the diagram: `{title, cols, rows}` is the state before step 1, and a step with `board: [[...]]` replaces the rows from there on. Changed cells flash. Prefix a value with `~` to strike it through (a killed token).
- Use concrete data everywhere: names, emails, token prefixes, timestamps.

### What makes a decision

A decision is a choice the author made where a reasonable engineer could have chosen otherwise, and the reviewer has to accept it. Name the road not taken (`instead`) and what the choice costs (`cost`). A decision with no cost is a description: cut it.

Good sources, in order: schema shape (what is stored, derived, constrained), concurrency and transaction boundaries, security and trust (what a token or key allows), the API contract (URL shape, status codes, what leaks), reuse or duplication of existing code paths, and anything the PR body or an ADR calls a decision. Not decisions: following the repo's conventions, generated code, test structure, renames.

### What goes in watch

Things a careful reviewer would open: a missing guard, a state an operation accepts that it probably should not, a silent side effect (a cascade with no event), a behaviour that drops caller input, a rollout step outside the diff. Every entry points at a line or names the missing piece. Write a question as a question. At most two style nits, last.

### 4. Tests as Given/When/Then

Hand `tests.diff` to a subagent on a fast model, so the test bodies never enter your context. Give it the rule list you settled in step 3 and this contract:

```json
[{"rule": "One pending invitation per email per organization",
  "how": "Checked in the service under the organization row lock",
  "given": "Acme has a pending invitation for ana@acme.io",
  "examples": [
    {"when": "an admin invites ana@acme.io again", "then": "409 ALREADY_PENDING", "ok": false, "test": "TestCreateInvitation_RefusesSecondPendingForSameEmail"},
    {"when": "eight admins invite bob@acme.io at the same instant", "then": "one 201, seven 409", "ok": true, "race": true, "test": "TestCreateInvitation_HoldsOnePendingPerEmailUnderConcurrentCreates"}]}]
```

Rules for the subagent: every test appears in exactly one row, `test` is the exact function name, `given` is the shared starting scene with concrete data, `when` is one action of 14 words or fewer, `then` is the observable outcome with the status and error code the test asserts, `ok` is false for a refusal. Extra setup for one row goes at the start of its `when`. Tests that fit no rule go in a last rule, "Everyday reads and writes". Ask it to report the row count, and check it against the test count triage printed.

Put the result in `rules`. The viewer flags any example whose `test` is not in the diff, and lists tests no example covers.

Done when every decision has `why`, `instead`, `cost` and at least one ref, every test sits in exactly one example, and the caps hold.

### 5. Build and publish

```
python3 scripts/build.py change.json -o change-map.html
```

It warns on missing fields and broken caps. Fix the warnings, then publish `change-map.html` with the Artifact tool (it needs no doctype). Use `--standalone` for a file to open locally. On a republish for a new head commit, rerun triage and keep your judgment keys.

## The reviewer's side

The first scenario plays itself once when it scrolls into view, and every scenario has Play, step and scrub controls (arrow keys too). Each decision has Agree and Question it. Question opens a note. Watch items can be added to the review. The top bar keeps the tally, and "Copy review" writes the GitHub review body: the questions with their notes, the flagged items, and the agreed decisions. The state stays in the reviewer's browser, per PR and head commit.

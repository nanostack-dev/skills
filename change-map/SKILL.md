---
name: change-map
description: Turn a pull request or in-progress branch into an interactive review page that a human can approve without reading the diff. Shows the decisions to approve, the lifecycle, the schema, the execution flows, the API, which tests pin which rule, and how much of the diff is noise. Use when asked to visualize, map, or explain a PR or ongoing work, to prepare a change for review, to "make this PR reviewable", or when a diff is too large to read, is mostly generated code, or mixes schema, entity, logic and noise.
---

# Change map

A change map is one page that answers what a reviewer has to decide. The reviewer reads the decisions and the risks, checks the pictures, and approves or questions each decision. They open code only through the file links on the page.

The page has two parts, and you write only one of them:

- **The viewer** (`viewer.html`) is a fixed, designed renderer. It owns every pixel: layout, theme, diagrams, the review tally. Never edit it for one change, and never write HTML or CSS for a change map.
- **The data** (`change.json`) is what you write. A script fills its mechanical half. You fill the judgment half, around 10 KB of JSON even for a 12,000-line PR.

That split is what keeps the page good-looking and cheap: the design is done once, and each change costs only its facts.

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
python3 scripts/triage.py --pr <number> [--repo owner/name] -o change.json --diff-out review.diff
python3 scripts/triage.py --range main...HEAD -o change.json --diff-out review.diff   # work with no PR yet
```

The script sorts every file into a bucket (generated, tests, schema, contract, logic, wiring, docs), extracts test names, and writes `review.diff` with only the files a human must read. It prints the split to stderr.

Add `--generated '<glob>'` for any generated path it missed, and rerun. Done when no generated or vendored file sits in a read bucket.

### 2. Read only what matters

Read `review.diff`, the PR body, and the commit messages. Do not read generated files or test bodies: test names in `change.json` already state what the tests prove. Read one test body only when its name leaves the behaviour unclear.

### 3. Fill the judgment half

Write these keys into `change.json`. Keep every string short and plain. Put identifiers in backticks and they render as code. Leave out any section that does not apply, and the viewer hides it.

| Key | What it holds | Cap |
|---|---|---|
| `summary` | What the change does for its consumer, 2 or 3 sentences | |
| `verdict` | `risk` (low, medium, high), `door` (one-way, two-way), `doorNote`, `ask`: one sentence naming what the reviewer is approving | |
| `decisions` | `{id, tag, title, choice, why, instead, cost, refs}` | 7 |
| `watch` | `{id, sev, title, body, ref}` where `sev` is risk, question, nit or note | 6 |
| `model` | `{entity, states: [{id, label, note, tone, derived}], transitions: [[from, to, label]], ops: {cols, rows, note}}` | 5 states |
| `schema` | `{hint, tables: [{name, new, change, file, note, cols: [[name, type, flags, meaning]], idx: [[name, on, serves]], notes}]}` | |
| `flows` | `{name, actor, tx: [first, last], steps: [{k, t, err}], result}` where `k` is read, lock, guard, write, emit or call | 5 flows, 8 steps |
| `api` | `{m, p, scope, emits, note}` | 16 |
| `rules` | `{rule, how, tests: [substring, ...]}`, each substring matching test names | 10 |
| `meta.stack`, `meta.links` | Stack position such as `"1/3"`, and `[{label, url}]` for issue, epic, ADR | |

`refs` and `ref` are `path:line` against the head commit, and the viewer links them to GitHub. `tx` gives the step indexes, counting from 0, that run inside one transaction. In `ops`, a cell is `ok`, an HTTP status, or a short word. `flags` is comma-separated: `pk`, `fk → table`, `unique`, `null`.

### What makes a decision

A decision is a choice the author made where a reasonable engineer could have chosen otherwise, and the reviewer has to accept it. For each one you name the road not taken (`instead`) and what the choice costs (`cost`). A decision with no cost is a description: cut it.

Good sources, in order: schema shape (what is stored, derived, constrained), concurrency and transaction boundaries, security and trust (what a token or key allows), the API contract (URL shape, status codes, what leaks), reuse or duplication of existing code paths, and anything the PR body or an ADR calls a decision.

Not decisions: following the repo's conventions, generated code, test structure, renames.

### What goes in watch

Things a careful reviewer would open: a missing guard, a state an operation accepts that it probably should not, a silent side effect (a cascade with no event), a behaviour that drops caller input, a rollout step outside the diff. Every entry points at a line or names the missing piece. Write a question as a question. Style nits go last, and at most two of them.

### Proof

`rules` map each business rule to the tests that pin it. A rule with no matching test shows as untested, which is the point. Tests that match no rule gather under "Other tests". Many other tests means your rules miss something.

Done when every decision has `why`, `instead` and `cost` and at least one ref, every rule matches at least one test (or is truly untested), and the caps hold.

### 4. Build and publish

```
python3 scripts/build.py change.json -o change-map.html
```

It warns on missing fields and broken caps. Fix the warnings, then publish `change-map.html` with the Artifact tool (it needs no doctype). Use `--standalone` for a file to open locally. On a republish for a new head commit, rerun triage and keep your judgment keys.

## The reviewer's side

Each decision has Agree and Question it. Question opens a note. Watch items can be added to the review. The rail keeps the tally, and "Copy review comment" writes the GitHub review body: the questions with their notes, the flagged items, and the agreed decisions. The state stays in the reviewer's browser, per PR and head commit.

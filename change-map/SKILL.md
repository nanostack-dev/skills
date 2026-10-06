---
name: change-map
description: Turn a pull request or in-progress branch into an interactive, picture-first review page that a human can approve without reading the diff, with a swipe deck to approve, comment on or reject each point. Shows a system diagram of what is new, the decisions to approve with concrete request and payload examples, animated step-by-step scenarios, the lifecycle, an ER schema, the guards per operation, the API, the tests as Given/When/Then, and how much of the diff is noise. Use when asked to visualize, map, or explain a PR or ongoing work, to prepare a change for review, to "make this PR reviewable", or when a diff is too large to read, is mostly generated code, or mixes schema, entity, logic and noise.
---

# Change map

A change map is one page that answers what a reviewer has to decide. The reviewer looks at the pictures, reads the decisions and the risks, and approves or questions each decision. They open code only through the file links on the page.

**Picture first.** The reviewer has already read too much text. Every fact that can be a diagram, a scenario or a table goes there. Prose only carries why and what it costs. One concrete example (Ana at Acme, `ana@example.invalid`, token `invite_7Hk…`) beats a paragraph.

The work splits three ways, and you write only the middle part:

| File | Written by | Holds |
|---|---|---|
| `change.json` | `triage.py` | meta, noise buckets, test names, schema parsed from `CREATE TABLE`, routes parsed from OpenAPI |
| `judgment.json` | you | the decisions, risks, pictures and meanings, about 25 KB |
| `gwt.json` | a subagent | the tests as Given/When/Then |

`build.py` merges them into the fixed viewer (`viewer.html`), which draws every diagram and animation. Never edit the viewer for one change, and never write HTML, CSS or SVG.

## Files

Use `scripts/triage.py`, `scripts/build.py`, `viewer.html`, `template.json` and `prompts/given-when-then.md` bundled with this skill. If they are unavailable, resolve the package directory and ref from its installation metadata or the URL/repository location used to load `SKILL.md`. Retrieve those assets from the same directory and ref.

## Steps

### 1. Triage

```
python3 scripts/triage.py --pr <number> [--repo owner/name] -o change.json
python3 scripts/triage.py --range main...HEAD -o change.json   # no PR yet
```

It writes `change.json`, `review.diff` (only the files a human reads), `review.index` (`path:line` of every symbol the change adds or touches) and `tests.diff` (the test files). On stderr it prints the noise split and the order to read files in. On a flaky network, save `gh pr diff` once and pass `--diff-file`.

If a generated or vendored file shows up in the reading order, add `--generated '<glob>'` and rerun.

### 2. Start the Given/When/Then subagent now

Fill `prompts/given-when-then.md` (the test count is on stderr, `RULE_HINTS` can stay empty) and run it as a background subagent on a fast model. It reads `tests.diff` so you never do, and it runs while you work on step 3.

### 3. Read

Read `review.diff` in the printed order. Take every `refs` line number from `review.index`, never by counting. Skim the contract file: the routes are already in `change.json`, so read it only for status codes and what leaks. Skip generated files entirely.

### 4. Write judgment.json

Read `template.json` (4 KB). It shows every key in its exact shape. Do not open the full example unless a shape is unclear: `examples/invitation-review/judgment.json` shows a complete anonymized invitation review. Its identifiers, links, counts and findings are illustrative; derive the actual review from the current change.

Write the whole file in one go. Caps: 7 decisions, 6 watch, 4 scenarios of at most 12 steps, 12 system nodes, 5 flows of at most 8 steps.

- `schema` and `api` are objects that enrich what triage parsed. `schema.tables.<name>.cols` maps each column to its meaning, `idx` maps an index name (or its suffix) to what it serves, `refs` maps a referenced table to a note, and `api` maps `"METHOD /path"` to `{scope, emits, note}`. Give a column `null` to hide it.
- `system` is laid out by the viewer. `col` is the swimlane a node belongs to (the `cols` headings: browser, API, services, a third party) and `row` only orders nodes inside a lane. Inside a lane, a node that fans out gets its callees one layer to the right, a one-to-one step between neighbouring rows stays stacked, long calls get their own track, and an edge back to an earlier lane (a reply, an email to the user) runs under the diagram. So write the real call graph, one edge per call from caller to callee, and never arrange boxes to dodge lines. `status` is `new` or `changed`, and new edges animate. `kind` is person, service, api, db, queue or external.
- `decisions[].see` names a scenario and adds a "See it run" button.
- `example` on any decision or watch item is a list of panels `{label, lang, code}`. See Examples below.
- `model.ops.edges[i]` lists the transition indexes row `i` fires, lit on hover.
- `flows[].tx` gives the step indexes, from 0, that run in one transaction.

**A decision** is a choice a reasonable engineer could have made differently that the reviewer has to accept. It always names `instead` and `cost`: a decision with no cost is a description, so cut it. Look in this order: what the schema stores, derives or constrains, concurrency and transaction boundaries, what a token or key allows, the API contract (URL shape, status codes, what leaks), reuse or duplication of existing code, and anything the PR body or an ADR calls a decision. Following conventions, generated code and renames are not decisions.

**Watch** holds what a careful reviewer would open: a missing guard, a state an operation accepts that it probably should not, a silent side effect, dropped caller input, a rollout step outside the diff. Point at a line, write questions as questions, and put at most two nits last.

**Examples.** Every decision and watch item carries an `example` when one exists, because a reviewer judges a real request faster than a sentence about it. Show the one case that makes the point: the 409 a second create gets, the `expired` status a GET returns, the row Postgres keeps, the event payload, the SQL that locks. Rules:

- One or two panels, 3 to 15 lines each. `lang` is `http`, `json`, `sql`, `go`, `diff` or `text`, and drives the highlighting. `label` says what the panel shows ("Two creates at the same instant", not "Example").
- In `http`, write the request line, the body, a blank line, then the status and response body. Several steps in one panel are fine ("request A → 201", "request B → 409").
- Copy field names, status codes and the error envelope from the contract in the diff. Never invent a shape. Ids may be readable stand-ins (`org_acme`, `oinv_2Kx9`, `pu_ana`) used the same way across the page.
- A watch item's example shows the questionable case happening. For a nit, show the code.

`build.py` reports review points with no example. Leave one out only when nothing concrete exists.

**A scenario** is a sequence diagram the reviewer plays. Write one for each decision that is easier to see than to explain: a race, a token that stops working, the full round trip. Actors are real people and systems ("Admin A", "Request A", "Postgres"). A step is `{from, to, k, label, say}`, with `k` one of call, reply, error or block. `label` stays under 44 characters and `say` is one or two sentences. A `block` step with `until: i` draws a waiting bar until step `i`. `board` is the live table beside the diagram: `rows` is the state before step 1, and a step with `board` replaces it. Prefix a value with `~` to strike it through.

### 5. Build

When the subagent reports, save its output as `gwt.json`, then:

```
python3 scripts/build.py change.json judgment.json gwt.json -o change-map.html
```

It prints every problem (a missing field, a broken cap, a test with no Given/When/Then row, a column with no meaning, a dangling scenario or node id) and a one-line summary of the page. Fix and rerun until there is no warning, then publish `change-map.html` with the Artifact tool. Use `--standalone` for a local file.

The viewer is already checked at desktop and phone widths in both themes. Do not screenshot-loop it: a clean build is the check. Look once only if you changed the viewer itself.

For a new head commit, rerun triage and the build, and keep `judgment.json` and `gwt.json`.

## The reviewer's side

Every decision and watch item is a review point with three answers: Approve, Comment or Reject. Comment and Reject ask for a note.

**The review deck** ("Start the review" in the overview, "Review" in the top bar, or the page URL with `#review`) shows one point at a time on a full-height card with its examples expanded. Swipe right to approve and left to reject, or use the buttons. The keys are → approve, ← reject, ↑ comment, ↓ skip, Z undo and Esc close. The last card sums up the verdict (Request changes, Approve with comments, or Approve) and copies the GitHub review body: must-change items with notes, then comments, then the count approved.

On the page, the same three answers sit on each card, and examples fold behind a toggle to keep the grid scannable. The first scenario plays once when it scrolls into view, and every scenario has Play, step and scrub controls. The state stays in the reviewer's browser, per PR and head commit.

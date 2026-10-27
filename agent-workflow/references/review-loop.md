# Review loop

Use for every non-trivial change: new behavior, a migration, a contract or an
endpoint/consumer replacement. Skip for typo, formatting and mechanical edits. The
project's own review rules win over this file.

Evidence behind the loop (cursor-search standard shipped across three repositories,
2026-10-15): 11 external review passes found 21 defects in small batches (6, 5, 2, 0
in one repository; 4, 1 in another; 4, 3, 0 in a third; 1 in a follow-up PR), each
round costing 10-20 minutes of review plus a full gate rerun. 19 of 21 findings fell
in the classes below. The causes were no design review, 120-200 file diffs where
reviewers report only their top findings, review that started after the full gates,
fixes that repaired the instance instead of the class, and improvised reviewer
prompts.

## Defect classes

Name the class on every finding, in specs, prompts and commits.

| Class | Check |
| --- | --- |
| A. Migration and rollout safety | Works while the previous application version still runs (expand, then contract). No write-blocking DDL on a populated table: index built concurrently (or per-chunk on a hypertable), no single large `UPDATE` backfill, no table rewrite, no new constraint that scans the table under lock. Append-only once on the main branch. Down migration and deploy order stated. |
| B. Behavior parity | Replacing an endpoint or consumer: write the parity matrix of old behavior (limit cap and read-everything callers, matching semantics such as case and wildcards, default order, fields in items, totals, error statuses, permissions and tenant scope) and pin each row with a test. Every consumer (UI, SDK, CLI, MCP, IaC provider) moved or kept on purpose. |
| C. Input validation | Every enum, sort field, filter value and cursor is validated. An unknown value answers 400, never a silent fallback. Validation runs before any early return (empty scope, cache hit, zero rows), so one request answers the same status whatever data the caller has. |
| D. Untrusted decoding and round-trip fidelity | A decoded cursor or token is hostile input: malformed, truncated, oversized, bound to another sort or filter, wrong types. A value survives encode, decode and query unchanged: timestamp precision and zone, floats, 64-bit integers through JSON, NULL, Unicode, ties on the sort key. |
| E. Frontend async state | A stale or out-of-order response never overwrites newer state: cancel or ignore superseded requests. Double submit, unmount during flight, per-request loading and error flags, paging state reset when filter or sort changes, debounced input against submit. |
| F. Project coding standards | When the repository has `CODING_STANDARDS.md`, every changed hunk follows each of its rules. These are the maintainer's recurring review corrections (for example comment density, unrequested scope, names); report them like defects. |

## 1. Design review gate

Before fanning implementation out to agents or branches, write the design or spec
and have one external reviewer review that spec, not code.

The spec holds the behavior and acceptance criteria, the contract change, every
consumer, the rollout order, and one line per class A-E: `applies: <how handled and
which test pins it>` or `n/a: <why>`. A class left blank is incomplete.

Run the reviewer with the spec prompt in [Reviewer prompts](#3-reviewer-prompts).
Complete when the verdict is CLEAN, or every defect is resolved in the spec and
the reviewer re-checked those edits. Fan out only then.

## 2. Review on first push

Push once the affected-area local checks pass (the normal pre-push gate); a draft PR
counts. Launch the reviewers at that push, in parallel with CI and any complete-suite
run, so review and gates finish together. A gate failure that changes code becomes a
later commit for the next re-review.

Review a detached worktree at the pushed head, and record the head SHA with every
verdict. Over about 40 changed files, slice by area (for example: migrations and
store, service and API, clients and consumers, frontend, tests and docs) and run
one reviewer per slice with that slice's file list:

```bash
git diff --name-only origin/main...HEAD
git diff origin/main...HEAD -- <slice paths>
```

Leave generated files out of the slices; review their generator input instead.
Add one seam slice when a contract spans slices (spec against each consumer).

## 3. Reviewer prompts

Write the prompt to a file from this template; fill every `<...>` and keep the rest
verbatim. Never improvise it.

```text
You are reviewing code. Do not edit, create or delete any file; do not commit.
Repository: <path>. Head: <sha>. Base: origin/main.
Scope: <whole diff | slice name: paths>. See it with:
  git diff origin/main...HEAD -- <paths>
Intent of the change: <2-3 sentences and the spec path>.
Previously reported and fixed (do not re-report; verify the fix and its class
sweep): <list, or "none">.

Check every changed hunk against these classes:
A. Migration and rollout safety (works with the previous app version running; no
   write-blocking DDL or large single-statement backfill; append-only).
B. Behavior parity when an endpoint or consumer is replaced (limits, matching
   semantics, order, fields, totals, errors, permissions, every consumer).
C. Enum, sort, filter and cursor validation, including validation before early
   returns.
D. Untrusted cursor or value decoding, and value round-trip fidelity.
E. Frontend async state races.
F. Every rule in <repo>/CODING_STANDARDS.md, when that file exists.

Report every concrete defect, not only the top few, each as:
  [class A-F or other] file:line | failing scenario | minimal fix
Report defects that produce wrong behavior, data loss, a security hole or an
unsafe rollout, and every class F violation tagged [standards]. No refactors or
style nits outside CODING_STANDARDS.md, no speculative hardening.
Finish with exactly one line: VERDICT: CLEAN  or  VERDICT: <n> DEFECTS
```

Spec review: replace the diff lines with the spec path and say "Review this spec,
not code. Report every class A-E gap, missing consumer or unstated rollout step."

Grok variant: append "Do not over-engineer. Report only real issues. If you are
unsure a finding is real, leave it out." This is the user-preferred form for Grok.

Re-review: set Scope to `git diff <last-reviewed-sha>..HEAD`, list the previous
findings, and name the class sweep that fixed each (section 4).

## 4. Fix the class, not the instance

For each finding, in order:

1. Name its class and the pattern behind it.
2. Audit the whole diff and its consumers for that pattern (`grep -rn`, a
   per-endpoint checklist, or each migration file). List every occurrence.
3. Fix all occurrences in one commit, with a test per distinct occurrence (a table
   test covers a shared helper).
4. Put the class, the audit command and the occurrence count in the commit body.
   Hand the same to the reviewer in the re-review prompt.

Complete when the audit lists zero unfixed occurrences.

## 5. Stop condition

Ready means all of:

- Two independent reviewers (different tools or models, for example Codex and
  Grok) each returned `VERDICT: CLEAN` on the final head.
- CI is green on that same head.

A pass is clean on a head when the reviewer's last full pass was clean and every
commit since was re-reviewed clean (section 3, Re-review). Re-review only those
commits, not the whole diff. Any defect restarts that reviewer's loop from section 4.
Record reviewers, head SHA and verdicts in the PR.

## 6. Reviewer CLIs

Versions checked: codex-cli 0.160.1, grok 1.0.41. Run the preflight before every
launch (a 10-second check that fails when a flag is renamed):

```bash
codex exec --help 2>&1 | grep -q -- '--output-last-message' && \
grok --help 2>&1 | grep -q -- '--prompt-file' && echo preflight-ok
```

On failure, read `codex exec --help` or `grok --help` and adapt before launching.

Codex (read-only sandbox, final message written to a file):

```bash
codex exec -s read-only -C <dir> -o <out.md> "$(cat <prompt.md>)"
# or: codex exec -s read-only -C <dir> -o <out.md> - < <prompt.md>
```

`codex review --base <branch> "<prompt>"` fails with `--base cannot be used with
[PROMPT]`. Use `exec` with the template instead.

Grok (detached throwaway worktree; `bypassPermissions` allows writes, so the prompt carries
the no-edit rule and `git status` verifies it):

```bash
WT=$(mktemp -d)
git worktree add --detach "$WT" <sha>
grok --permission-mode bypassPermissions --cwd "$WT" --max-turns 200 \
  --prompt-file <prompt.md> > <out.md>
git -C "$WT" status --short          # must print nothing
git worktree remove --force "$WT"
```

`grok -p ... --permission-mode plan` only plans and reviews nothing. A non-empty
`status` means the reviewer edited files: discard the worktree and rerun with the
no-edit line first in the prompt.

Run reviewers in the background, one output file each, and launch all slices and both
tools together. Codex needs `-C` to point at a worktree of the head being reviewed.

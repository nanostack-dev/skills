# Routine tag run overlapped the echopoint deploy gate: flow folders 409 FLOW_TREE_CONFLICT

| | |
|---|---|
| **Date** | 2026-11-07 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint dogfood suites (prod CI org) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | 7m 03s (trigger to resolution) |
| **Time to detect** | 57s |
| **Time to mitigate** | 1m 52s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

At 18:34Z the routine's second ad-hoc soak of the `echopoint` tag ran while Deploy Router run 42401825800 (echopoint#779) was running the same tag as its post-deploy gate. Both runs use the prod CI org and its `echopointOrgId`. The flow-tree lock (`pglock.TryAdvisoryXactLock` on `echopoint.flow_tree:<org>`) rejects a second writer at once instead of waiting, so the routine's `flow folders` flow got **409 FLOW_TREE_CONFLICT** on `cleanup-sibling`. The gate stayed green and promoted prod at 18:37Z, but only because its own `flow folders` won the lock. `run_suites.sh` now waits for any active Deploy Router run before each tag and flags any overlap.

## Impact

No customer impact and no held deploy. One routine soak run read 56/57 instead of 57/57. Had the gate's `flow folders` lost the lock instead, the gate would have gone red and held echopoint#779 off prod until a human reran it.

- **1 / 57** routine flows failed (409)
- **0** gate flows failed (by luck)
- **2.5 min** overlap of routine run and gate suite

## Trigger

An ad-hoc `echopoint` tag run (soak of a newly tagged flow) started at 18:35Z without checking for an active Deploy Router run; the gate's suite for echopoint#779 had started at 18:33:37Z.

## Detection

The routine read its own tag result (56/57) and matched the failing execution's start time against the gate's job times. Detection was good enough for this side; the new `GATE-OVERLAP` line in `run_suites.sh` now names the overlap directly.

## Resolution

The routine reran the tag once the gate finished (57/57) and added `gate_wait` and `gate_overlap` to `run_suites.sh`, so scheduled runs never start a tag while a Deploy Router run is queued or in progress.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| 18:29:13 | T−5m 02s | **Routine tag soak 1 starts (new flow tagged)** runs/2026-11-07T1808/tag1 |
| 18:32:08 | T−2m 07s | **echopoint#779 merged** ([link](https://github.com/nanostack-dev/echopoint/pull/779)) |
| 18:32:50 | T−1m 25s | **Deploy Router 42401825800 created** ([link](https://github.com/nanostack-dev/infra/actions/runs/42401825800)) |
| 18:33:37 | T−38s | **Gate echopoint suite starts on dev** ([link](https://github.com/nanostack-dev/infra/actions/runs/42401825800)) |
| 18:34:15 | T+0s | **Routine `flow folders` runs during the gate** execution 01a1b74a-332e-7b74-bf01-279defac1f85; soak 1's tail and soak 2 overlap the gate |
| 18:34:17 | T+2s | **cleanup-sibling: 409 FLOW_TREE_CONFLICT** the gate held the org's tree lock |
| 18:35:12 | T+57s | **Soak 1 ends 56/57; routine reads the 409** |
| 18:36:07 | T+1m 52s | **Gate suite ends green (57/57)** ([link](https://github.com/nanostack-dev/infra/actions/runs/42401825800)) |
| 18:37:43 | T+3m 28s | **Gate promotes echopoint to prod** |
| 18:41:18 | T+7m 03s | **Soak 2 ends 57/57** |
| ~19:00 | T+25m 45s | **gate_wait and gate_overlap added to run_suites.sh** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["A routine suite run failed with 409, and the echopoint deploy gate ran with a real chance of a false red that would hold prod."]
  W1["`flow folders` got 409 FLOW_TREE_CONFLICT deleting a folder while the gate's suite ran in the same org."]
  W2["The flow-tree lock rejects a second writer at once instead of waiting."]
  R2["R2 · The tree lock was designed for one writer per org; concurrent automated writers in one org were not a design case."]
  W3["The routine started a tag run while a Deploy Router run was in progress."]
  W4["The soak ran by hand with `flows run --tag`, not through `run_suites.sh`."]
  R1["R1 · The 'never during a gate' rule lived only in SKILL.md; no script checked for an active Deploy Router run."]
  W5["The overlap could have turned the gate red, not only the routine run."]
  W6["The gate and the dogfood suites share the prod CI org and its `echopointOrgId`, so either side can lose the lock."]
  R3["R3 · Flows that write the folder tree run in the shared CI org instead of a per-run throwaway org."]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| R2
  W1 -->|why?| W3
  W3 -->|why?| W4
  W4 -->|why?| R1
  P -.->|why so bad?| W5
  W5 -->|why?| W6
  W6 -->|why?| R3
  class P problem
  class R2,R1,R3 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** A routine suite run failed with 409, and the echopoint deploy gate ran with a real chance of a false red that would hold prod.
  - **Why?** `flow folders` got 409 FLOW_TREE_CONFLICT deleting a folder while the gate's suite ran in the same org. _Evidence: execution 01a1b74a… at 18:34:17Z; gate suite 18:33:37–18:36:07Z_
    - **Why?** The flow-tree lock rejects a second writer at once instead of waiting. _Evidence: echopoint internal/feature/flows/treelock.go: pglock.TryAdvisoryXactLock on echopoint.flow_tree:<org>_
      - **Why?** The tree lock was designed for one writer per org; concurrent automated writers in one org were not a design case. → **Root cause R2** (fixed by A4)
    - **Why?** The routine started a tag run while a Deploy Router run was in progress. _Evidence: soak runs 18:29–18:41Z; Deploy Router 42401825800 18:32:50–18:37:43Z_
      - **Why?** The soak ran by hand with `flows run --tag`, not through `run_suites.sh`.
        - **Why?** The 'never during a gate' rule lived only in SKILL.md; no script checked for an active Deploy Router run. _Evidence: run_suites.sh before this run had no gate check_ → **Root cause R1** (fixed by A1, A2, A3)
  - **Why so bad?** The overlap could have turned the gate red, not only the routine run.
    - **Why?** The gate and the dogfood suites share the prod CI org and its `echopointOrgId`, so either side can lose the lock. _Evidence: both runs use org_3AbVP9cGsWfmaWVfChGHmAmdSAY_
      - **Why?** Flows that write the folder tree run in the shared CI org instead of a per-run throwaway org. → **Root cause R3** (fixed by A5)

## Root causes

- **R2** The tree lock was designed for one writer per org; concurrent automated writers in one org were not a design case.
- **R1** The 'never during a gate' rule lived only in SKILL.md; no script checked for an active Deploy Router run.
- **R3** Flows that write the folder tree run in the shared CI org instead of a per-run throwaway org.

## Contributing factors

- SKILL.md says not to run tags during a gate, but nothing enforced it.
- Soaks after tagging were run by hand with `flows run --tag`, outside `run_suites.sh`.
- The tree lock fails fast; any two writers to the folder tree in one org conflict.
- The dogfood suites and the post-deploy gate share one CI org and one `echopointOrgId`.

## Lessons learned

### What went well

- The failing execution's timestamps matched the gate's job window within minutes, so the cause was clear without guessing.

### What went wrong

- A documented rule with no check in the script was skipped by a hand-run soak.

### Where we got lucky

- The gate's own `flow folders` won the lock; the other order would have held echopoint#779 off prod with a false red.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | run_suites.sh waits for queued or in-progress Deploy Router runs before each tag (`gate_wait`) | prevent | Nanostack routine (echopoint-investigation) | 2026-11-07 | done |  | R1 |
| A2 | run_suites.sh prints `GATE-OVERLAP` when a Deploy Router run started during a tag | detect | Nanostack routine (echopoint-investigation) | 2026-11-07 | done |  | R1 |
| A3 | Run every soak through run_suites.sh (or after gate_wait), never a bare `flows run --tag`; noted in SKILL.md | process | Nanostack routine (echopoint-investigation) | 2026-11-07 | done |  | R1 |
| A4 | Tree lock: wait briefly or retry on contention instead of failing at once (TryAdvisoryXactLock → bounded wait) | prevent | echopoint maintainers | 2026-11-21 | open |  | R2 |
| A5 | Move `echopoint: flow folders` to a per-run throwaway org so its tree writes never share a lock with the gate | mitigate | Nanostack routine (echopoint-investigation) | 2026-11-14 | open |  | R3 |

## Responders

- **Detection and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

The routine's tag soak overlapped the echopoint gate and its `flow folders` hit a 409 FLOW_TREE_CONFLICT. The gate was green by luck. `run_suites.sh` now waits for Deploy Router runs. Open: echopoint should queue or retry on the tree lock, or the folders flow should use a throwaway org.

### Customers

None: no impact.

## Supporting information

- [Deploy Router 42401825800](https://github.com/nanostack-dev/infra/actions/runs/42401825800)
- [echopoint#779](https://github.com/nanostack-dev/echopoint/pull/779)

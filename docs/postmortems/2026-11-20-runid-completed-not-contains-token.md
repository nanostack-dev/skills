# Gate flow `Flow save history and restore` failed when the run id completed a not_contains token

| | |
|---|---|
| **Date** | 2026-11-20 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint prod CI org flow suite (echopoint gate tag) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~15m 15s (trigger to resolution) |
| **Time to detect** | ~45s |
| **Time to mitigate** | 14m 05s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

The routine's third tag soak failed `Flow save history and restore` (af928132): node `get-restored` asserted the body does not contain `hist-c`, and the flow's own name `ep-hist-{{$runId}}` rendered as `ep-hist-ce16…`. Any run id starting with `c` failed it: one run in sixteen, in the echopoint gate tag since 2026-11-20T06:08Z. The routine replaced the body checks with JSONPath checks on the node display name, renamed the flow prefix, and added `audit_runid_collision.py` to every suite run; it found no other flow in the class.

## Impact

No customer impact. One soak failed. Each gate run had a 1 in 16 chance to fail and hold a prod deploy.

- **1/16** chance per run (two nodes)
- **~13 h** in the gate tag before the fix
- **0** gate failures from it

## Trigger

Run id `ce16d4bb…` made the flow name contain `hist-c`.

## Detection

The routine's third soak at 18:52 UTC printed `FAILED … body not_contains expected=hist-c` and the routine read the full body.

## Resolution

Flow updated at 19:06 UTC (JSONPath on `display_name`, prefix `ep-history-`), green 3x; audit wired into run_suites.sh.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| ~06:10 | T−12h 42m | **Routine adds the flow to the echopoint tag** Generator `gen_flow_history.py`, 3 serial greens and 2 tag soaks. |
| 18:52:45 | T+0s | **Run id ce16… makes the name contain hist-c** |
| ~18:53 | T+45s | **Soak 3 prints FAILED on get-restored** |
| 19:06:50 | T+14m 05s | **Flow updated: JSONPath checks, ep-history- prefix** |
| ~19:08 | T+15m 15s | **Green 3x; audit finds no other flow** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["A gate-tag flow failed with no product change"]
  W1["`get-restored` asserted the body does not contain `hist-c`, and the body held `ep-hist-ce16…`"]
  W2["The flow name carries `{{$runId}}` (hex), and the token's tail `c` is a hex digit"]
  W3["Absence was asserted on the whole body instead of on the field that holds the marker"]
  R1["R1 · No rule or check stops a body `not_contains` token that a per-run id in the same flow can complete"]
  W4["Three serial greens and two soaks did not show it: 15 of 16 run ids pass"]
  W5["The author's checks for a new flow were runs only: 3 serial greens and 2 tag soaks, no static review of assertions"]
  R2["R2 · Probabilistic false failures need a static check; repeated runs only sample them"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| R1
  P -.->|why so bad?| W4
  W4 -->|why?| W5
  W5 -->|why?| R2
  class P problem
  class R1,R2 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** A gate-tag flow failed with no product change
  - **Why?** `get-restored` asserted the body does not contain `hist-c`, and the body held `ep-hist-ce16…` _Evidence: Node error: `body not_contains expected=hist-c actual={… "name":"ep-hist-ce16d4bb83f1" …}`_
    - **Why?** The flow name carries `{{$runId}}` (hex), and the token's tail `c` is a hex digit _Evidence: `gen_flow_history.py` line 71 `ep-hist-{{$runId}}`_
      - **Why?** Absence was asserted on the whole body instead of on the field that holds the marker
        - **Why?** No rule or check stops a body `not_contains` token that a per-run id in the same flow can complete → **Root cause R1** (fixed by A1, A2, A3)
  - **Why so bad?** Three serial greens and two soaks did not show it: 15 of 16 run ids pass
    - **Why?** The author's checks for a new flow were runs only: 3 serial greens and 2 tag soaks, no static review of assertions
      - **Why?** Probabilistic false failures need a static check; repeated runs only sample them → **Root cause R2** (fixed by A2)

## Root causes

- **R1** No rule or check stops a body `not_contains` token that a per-run id in the same flow can complete
- **R2** Probabilistic false failures need a static check; repeated runs only sample them

## Lessons learned

### What went well

- The runner printed the actual body, so the cause was clear in one read.

### What went wrong

- A check written to prove the restored state was weaker than the JSONPath check beside it.

### Where we got lucky

- It failed in a soak, not in a gate holding a prod deploy.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Assert on `display_name` by JSONPath; prefix `ep-history-` (flow af928132, generator) | prevent | Nanostack routine (echopoint-investigation) | 2026-11-20 | done |  | R1 |
| A2 | `audit_runid_collision.py` runs on every tagged flow in run_suites.sh and prints RUNID-COLLISION | detect | Nanostack routine (echopoint-investigation) | 2026-11-20 | done |  | R2, R1 |
| A3 | flow-suite-testing skill: assert absence on the field, not a body token | process | Nanostack routine (echopoint-investigation) | 2026-11-20 | done |  | R1 |

## Responders

- **Investigation and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Flow save history and restore could fail 1 run in 16 (run id completed a not_contains token); fixed and audited.

### Customers

None.

## Supporting information

- [skills PR](https://github.com/nanostack-dev/skills/pulls)

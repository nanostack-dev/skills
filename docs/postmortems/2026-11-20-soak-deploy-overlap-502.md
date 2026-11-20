# Routine tag soak failed on a dev deploy 502 and printed an empty FAILED line

| | |
|---|---|
| **Date** | 2026-11-20 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint-investigation routine (run_suites.sh), dev echopoint deploy |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~15m 26s (trigger to resolution) |
| **Time to detect** | ~5m 26s |
| **Time to mitigate** | ~10m 26s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

An echopoint deploy (Deploy Router 44793938980) started five minutes into the routine's first tag soak. Dev Traefik answered 502 while a task stopped, and `Integration steps need the plan` failed on `update-ok`. run_suites.sh then read the flow's newest execution, which the gate had created two minutes later and passed, and printed `FAILED` with no message; its leak check would have read the same wrong run. This regresses the 2026-11-07 overlap row: `gate_wait` covers gates that start before a tag, not deploys that start during one. run_suites.sh now reads the execution it launched (`exec_of`) and reruns a 50x in an overlapped tag after its leak check.

## Impact

No customer impact. One soak flow failed; no resource leaked. Prod showed no 5xx during its own deploy.

- **3** dev Traefik 502s in 11 s
- **1** soak flow failed
- **0** leaked resources

## Trigger

Deploy Router 44793938980 replaced dev echopoint tasks at 18:34 UTC during the soak.

## Detection

run_suites.sh printed `GATE-OVERLAP` and an empty `FAILED` line at ~18:40 UTC; the routine read the tag log.

## Resolution

Soak 2 passed 101/101 on the new build. run_suites.sh changed the same run.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| ~18:28 | T−6m 14s | **Soak 1 starts after gate_wait finds no run** |
| 18:33:48 | T−46s | **Deploy Router 44793938980 starts** ([link](https://github.com/nanostack-dev/infra/actions/runs/44793938980)) |
| 18:34:34 | T+0s | **update-ok gets 502 from dev Traefik** Traefik `DownstreamStatus 502`, `OriginStatus 502` at 18:34:27, :34, :38 on tasks 10.30.0.143/.144. |
| 18:36:27 | T+1m 53s | **Gate runs the same flow; its run is the newest** |
| ~18:40 | T+5m 26s | **run_suites.sh prints GATE-OVERLAP and an empty FAILED** |
| ~18:45 | T+10m 26s | **exec_of and DEPLOY-OVERLAP-RERUN staged** |
| ~18:50 | T+15m 26s | **Soak 2 passes 101/101 on the new build** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["A routine soak reported a failure that was not a product regression, with no error message"]
  W1["`update-ok` got 502 while Swarm replaced a dev echopoint task"]
  W2["The deploy started after gate_wait returned; no wait before a tag prevents a later deploy"]
  R1["R1 · run_suites.sh reran only transport and lease failures, so a deploy-window 5xx failed the soak"]
  W3["Dev Traefik still routed to a stopping task during a start-first rollout; prod showed none"]
  W4["The FAILED line was empty and the leak check pointed at the wrong run"]
  W5["`fail_err` and `leaks` took `execution list` items[0]; the gate ran the flow 2 min later in the same org"]
  R2["R2 · run_suites.sh identified a failed run as the flow's newest execution, which breaks whenever the gate runs the same flow"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| R1
  W1 -->|why?| W3
  P -.->|why so bad?| W4
  W4 -->|why?| W5
  W5 -->|why?| R2
  class P problem
  class R1,R2 root
  class W3 open
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** A routine soak reported a failure that was not a product regression, with no error message
  - **Why?** `update-ok` got 502 while Swarm replaced a dev echopoint task _Evidence: Traefik access log 18:34:34 `/flows/5a3b…` 502; router `Deploy echopoint to dev` 18:33:51-18:34:45_
    - **Why?** The deploy started after gate_wait returned; no wait before a tag prevents a later deploy
      - **Why?** run_suites.sh reran only transport and lease failures, so a deploy-window 5xx failed the soak → **Root cause R1** (fixed by A2, A3)
    - **Why?** Dev Traefik still routed to a stopping task during a start-first rollout; prod showed none → _open, still investigating_
  - **Why so bad?** The FAILED line was empty and the leak check pointed at the wrong run _Evidence: `flows execution list` items[0] = 01a1fa3e… completed (gate, 18:36:27); failed run 01a1fa3c…_
    - **Why?** `fail_err` and `leaks` took `execution list` items[0]; the gate ran the flow 2 min later in the same org _Evidence: run_suites.sh before 2026-11-20T18:45Z_
      - **Why?** run_suites.sh identified a failed run as the flow's newest execution, which breaks whenever the gate runs the same flow → **Root cause R2** (fixed by A1)

## Root causes

- **R1** run_suites.sh reran only transport and lease failures, so a deploy-window 5xx failed the soak
- **R2** run_suites.sh identified a failed run as the flow's newest execution, which breaks whenever the gate runs the same flow

## Lessons learned

### What went well

- GATE-OVERLAP flagged the overlap, so the cause was found from one log line.

### What went wrong

- The empty FAILED line looked like the 2026-11-11 launch-timeout case and pointed the wrong way.

### Where we got lucky

- The failed run's cleanups completed; a leak there would have been checked against the gate's green run and missed.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | `exec_of`: fail_err and leaks read the execution the script launched | prevent | Nanostack routine (echopoint-investigation) | 2026-11-20 | done |  | R2 |
| A2 | `DEPLOY-OVERLAP-RERUN`: rerun once a 502/503/504 in a tag a deploy overlapped, after the leak check | mitigate | Nanostack routine (echopoint-investigation) | 2026-11-20 | done |  | R1 |
| A3 | Find why dev Traefik routes to a stopping echopoint task in start-first rollouts (prod clean) | detect | infra maintainers | 2026-12-04 | open |  | R1 |

## Responders

- **Investigation and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Soak false failure from a deploy overlap; run_suites.sh now reads its own execution and reruns deploy-window 5xx.

### Customers

None.

## Supporting information

- [Previous overlap postmortem](2026-11-07-suite-overlapped-deploy-gate.md)

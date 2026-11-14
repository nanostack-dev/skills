# Monitor run red: a removal check raced the delete of the org whose key it used

| | |
|---|---|
| **Date** | 2026-11-14 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint flow suite (prod CI org, dev APIs) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~3h 35m (trigger to resolution) |
| **Time to detect** | ~3h 31m |
| **Time to mitigate** | 3h 33m |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

The first run of a new self-hosted monitor failed `Workspace isolation` on node `cleanup-flow-gone`: it expected 404 and got 401. The node reads flow A with the run's throwaway org key, and it started in the same second as `cleanup-org`, which deletes that org and its keys. No edge ordered the two, so the delete won and Echopoint's per-request access decision refused the key. The race had passed 97 earlier runs on the CLI and Cloud runners. The flow now runs the check before the org delete, and the routine audits every flow for a node that reads with a credential a parallel node deletes.

## Impact

No customer impact. One scheduled run of the dogfood suite went red on dev; the product behaved as its contract says. Every cleanup completed, so nothing leaked.

- **1** red monitor run (of 97 earlier green runs)
- **0** leaked resources
- **1** flow with the race (of 123 audited)

## Trigger

At 02:47:37Z the self-hosted runner started `cleanup-flow-gone` and `cleanup-org` together; the org delete finished first and the check's org key answered 401.

## Detection

The routine's suite script lists failed monitor runs of the last 24 h and printed `MONITOR-FAILED` at its 06:08Z run. Monitors rerun nothing and alert nobody in this org, so the 3.5 h delay is the routine's cadence.

## Resolution

An edge `cleanup-flow-gone → cleanup-org` orders the check before the delete (live flow and generator). Three serial runs and two echopoint tag runs passed. `run_suites.sh` now runs `audit_teardown_race.py` on every flow and prints `TEARDOWN-RACE`.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| ~18:00 | T−12d 08h | **Isolation flow created; check and org delete are siblings** `gen_workspace_isolation.py`: `chain(cleanup-flow-a, cleanup-flow-gone)` and the owned cleanups → `cleanup-org`, with no edge between the check and the delete. |
| 02:34:50 | T−12m 47s | **Monitor 7e46c872 created (self_hosted, tag echopoint)** `Daily echopoint, all suites (self-hosted)`, cron `42 2 * * *`, tags echopoint/integration/license-limits; created by another session. |
| 02:42:04 | T−5m 33s | **First monitor run starts (execution 01a1d7ee)** |
| 02:47:37 | T+0s | **cleanup-org and cleanup-flow-gone start together; check gets 401** `cleanup-org` 339 ms, `cleanup-flow-gone` 383 ms, both started 02:47:37Z; assertion `status_code equals 404`, actual 401. |
| ~06:19 | T+3h 31m | **run_suites.sh prints MONITOR-FAILED for 174cb56e** |
| 06:21:27 | T+3h 33m | **Edge cleanup-flow-gone → cleanup-org added to the live flow** |
| ~06:23 | T+3h 35m | **Three serial runs green** |
| ~06:40 | T+3h 52m | **Teardown audit in run_suites.sh; skill lesson** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["A scheduled run of the echopoint dogfood suite went red on `Workspace isolation`"]
  W1["`cleanup-flow-gone` got 401 instead of 404 on `GET /flows/{A}`"]
  W2["The org whose key the check sends was already deleted, so Anchor's per-request decision refused the key"]
  W3["The flow has no edge between the check and the org delete: both wait only on the owned cleanups"]
  R1["R1 · Cleanup order is hand-written per flow, and nothing checks that a node reading with a run credential precedes the delete of that credential"]
  R2["R2 · The flow-suite-testing skill draws `cleanup → verify removal` but says nothing about which credential the verify step may use"]
  W4["97 earlier runs passed, so the race stayed hidden for 13 days"]
  W5["A new monitor ran the flow on the self-hosted runner, where the delete happened to finish first"]
  R3["R3 · New and reshaped flows are soaked on one runner type only, so a timing race passes until another runner runs it"]
  W6["The red run stayed red and nobody saw it for 3.5 h"]
  W7["A monitor reruns nothing, and its failures reach only the monitor history the routine reads four times a day"]
  R4["R4 · Monitors have no rerun or alert path for a failed suite run (open action of the 2026-11-08 monitor transport postmortem)"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| R1
  W3 -->|why?| R2
  P -->|why?| W4
  W4 -->|why?| W5
  W5 -->|why?| R3
  P -.->|why so bad?| W6
  W6 -->|why?| W7
  W7 -->|why?| R4
  class P problem
  class R1,R2,R3,R4 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** A scheduled run of the echopoint dogfood suite went red on `Workspace isolation`
  - **Why?** `cleanup-flow-gone` got 401 instead of 404 on `GET /flows/{A}` _Evidence: Execution 01a1d7ee node `cleanup-flow-gone`: `assertion 1 failed: status_code equals expected=404 actual=401`_
    - **Why?** The org whose key the check sends was already deleted, so Anchor's per-request decision refused the key _Evidence: `cleanup-org` and `cleanup-flow-gone` both started 02:47:37Z; delete 339 ms, check 383 ms; echopoint#675 asks Anchor on every request_
      - **Why?** The flow has no edge between the check and the org delete: both wait only on the owned cleanups _Evidence: Flow 174cb56e edges: `cleanup-flow-a → cleanup-flow-gone`, `cleanup-flow-a → cleanup-org`; `gen_workspace_isolation.py` lines 184-185_
        - **Why?** Cleanup order is hand-written per flow, and nothing checks that a node reading with a run credential precedes the delete of that credential → **Root cause R1** (fixed by A1, A2)
        - **Why?** The flow-suite-testing skill draws `cleanup → verify removal` but says nothing about which credential the verify step may use → **Root cause R2** (fixed by A3)
  - **Why?** 97 earlier runs passed, so the race stayed hidden for 13 days _Evidence: Executions of 174cb56e: 91 CLI ephemeral + 6 Cloud scheduled completed; the first self-hosted run failed_
    - **Why?** A new monitor ran the flow on the self-hosted runner, where the delete happened to finish first _Evidence: Monitor 7e46c872 created 02:34:50Z, runner_type self_hosted_
      - **Why?** New and reshaped flows are soaked on one runner type only, so a timing race passes until another runner runs it → **Root cause R3** (fixed by A2)
  - **Why so bad?** The red run stayed red and nobody saw it for 3.5 h
    - **Why?** A monitor reruns nothing, and its failures reach only the monitor history the routine reads four times a day
      - **Why?** Monitors have no rerun or alert path for a failed suite run (open action of the 2026-11-08 monitor transport postmortem) → **Root cause R4** (fixed by A4)

## Root causes

- **R1** Cleanup order is hand-written per flow, and nothing checks that a node reading with a run credential precedes the delete of that credential
- **R2** The flow-suite-testing skill draws `cleanup → verify removal` but says nothing about which credential the verify step may use
- **R3** New and reshaped flows are soaked on one runner type only, so a timing race passes until another runner runs it
- **R4** Monitors have no rerun or alert path for a failed suite run (open action of the 2026-11-08 monitor transport postmortem)

## Contributing factors

- The new monitor duplicates the Cloud `Daily echopoint` tag on another runner type, so every flow now runs on three runner types.

## Lessons learned

### What went well

- `MONITOR-FAILED` in the suite script surfaced the run without anyone reading monitor history.
- The run's `always` cleanups all completed, so the throwaway org and flows were gone.

### What went wrong

- A 3-run soak on the CLI runner was taken as proof of a flow whose correctness depended on node timing.

### Where we got lucky

- The node that lost the race was a read. A cleanup DELETE with the org key in the same place would have left flow A in Echopoint's database: deleting the Anchor org does not remove Echopoint rows.
- The race fired on a monitor run, not in a post-deploy gate, where it would have held prod.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Order `cleanup-flow-gone` before `cleanup-org` in the live flow and in `gen_workspace_isolation.py` | prevent | Nanostack routine (echopoint-investigation) | 2026-11-14 | done |  | R1 |
| A2 | `audit_teardown_race.py` in `run_suites.sh`: print `TEARDOWN-RACE` for any node that reads with an org or key a parallel node deletes | detect | Nanostack routine (echopoint-investigation) | 2026-11-14 | done |  | R1, R3 |
| A3 | flow-suite-testing skill: a removal check that uses a credential the teardown deletes runs before that delete | process | Nanostack routine (echopoint-investigation) | 2026-11-14 | done | [skills#63](https://github.com/nanostack-dev/skills/pull/63) | R2 |
| A4 | Give monitors a rerun or alert path for a failed suite run (carried over from the 2026-11-08 monitor transport postmortem A2) | mitigate | echopoint maintainers | 2026-11-22 | open | [2026-11-08 postmortem](http://nanostack-dev-1340p:4320/postmortems/01a1bb20-3f32-79f6-a37d-48272301c765) | R4 |

## Responders

- **Investigation**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

The first self-hosted monitor run failed `Workspace isolation`: a removal check raced the delete of the org whose key it used. Flow ordered, every flow audited (one race found), audit added to the suite script.

### Customers

None: dev and CI only.

## Supporting information

- [Atelier](http://nanostack-dev-1340p:4320/postmortems/01a1d8bb-f60a-709b-bdd5-88e3314338d5)
- [echopoint#675 (Anchor decides every request)](https://github.com/nanostack-dev/echopoint/pull/675)
- [skills#63](https://github.com/nanostack-dev/skills/pull/63)

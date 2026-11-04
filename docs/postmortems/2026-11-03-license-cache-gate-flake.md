# A new gate flow read a per-replica license cache right after an Anchor write and failed by replica luck

| | |
|---|---|
| **Date** | 2026-11-03 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint flow suite (`echopoint: invitation email budget`), Anchor SDK license cache |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~4h 37m (trigger to resolution) |
| **Time to detect** | ~4h 26m |
| **Time to mitigate** | ~4h 36m |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

`echopoint: invitation email budget` was added to the `echopoint` gate tag at about 18:00Z after three green runs and one green suite run. At 19:41:34Z, in the post-deploy gate for echopoint#733, its node `usage-lowered` read `limit 20` 79 ms after the flow PATCHed the license to 5 on Anchor. Echopoint reads licenses through the Anchor SDK cache (30 s TTL per replica) and the PATCH bypasses Echopoint, so a replica that served the previous read answers stale data. The earlier green runs passed because the two reads landed on different replicas. The flow now polls the limit through a module and makes that poll its final check; it ran green three times.

## Impact

Dev and CI only. The flake was one of the two checks that failed the echopoint gate for echopoint#733, so it would have held prod promotion on its own.

- **79 ms** between the PATCH and the stale read
- **30 s** Anchor SDK license cache TTL per replica
- **2** dev Echopoint replicas, each with its own cache

## Trigger

Gate run 41705330775: `usage-beta` (19:41:33.914Z) and `usage-lowered` (19:41:34.135Z) both landed on `echopoint-dev_echopoint.1`, around the Anchor PATCH at 19:41:34.056Z (VictoriaLogs).

## Detection

The echopoint-investigation routine read the red gate at 00:08Z. The gate's Discord alert at 19:42Z had no owner (see the companion SEV4 on gate flows that pinned old behaviour). Detection was adequate for a flake: the gate failed closed. The missing piece is an owner for red gates, covered by the companion postmortem's action.

## Resolution

New module `license: invitation limit poll (module)` polls `GET /license/usage` until the limit equals the expected value (2 s interval, 60 s timeout); the flow ends on that poll. A first version that polled and then read once more failed 3 of 3 runs: the poll was answered by the fresh replica and the next read by the stale one.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| ~18:00 | T−1h 41m | **Flow tagged `echopoint` after 3 green runs** |
| 19:41:34 | T+0s | **Gate: usage-lowered limit 20, expected 5** ([link](https://github.com/nanostack-dev/infra/actions/runs/41705330775)) |
| 19:42:02 | T+28s | **Deploy-failure alert to Discord, no owner** |
| ~00:08 | T+4h 26m | **Routine reads the red gate** |
| 00:11:12 | T+4h 29m | **Inline poll fails: a poll body cannot read node outputs** |
| 00:17:02 | T+4h 35m | **Poll then read: 3/3 red, proves per-replica caches** |
| ~00:18 | T+4h 36m | **Poll becomes the final check** |
| ~00:19 | T+4h 37m | **Flow green 3 times** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The echopoint post-deploy gate failed on a new flow, which alone would have held prod promotion"]
  W1["`usage-lowered` read limit 20 from a replica that had cached the license 220 ms earlier"]
  W2["Echopoint reads licenses through the Anchor SDK cache, 30 s per replica, and the flow wrote the license on Anchor directly"]
  R1["R1 · The flow guide covers projections that lag a write, not read caches in front of another service"]
  W3["Four earlier green runs hid the race: the two reads usually landed on different replicas"]
  W4["The routine's acceptance rule is three serial green runs, written for count races in one process"]
  R2["R2 · Repeated serial runs do not vary replica placement, so they cannot prove a check free of per-replica state"]
  W5["A flow three runs old sat in a gate that holds the whole product's promotion"]
  W6["The routine tags a flow into the gate as soon as it passes alone; the gate runs it beside 46 others"]
  R3["R3 · New flows join the gate tag with no soak period in the concurrent suite"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| R1
  P -->|why?| W3
  W3 -->|why?| W4
  W4 -->|why?| R2
  P -.->|why so bad?| W5
  W5 -->|why?| W6
  W6 -->|why?| R3
  class P problem
  class R1,R2,R3 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The echopoint post-deploy gate failed on a new flow, which alone would have held prod promotion
  - **Why?** `usage-lowered` read limit 20 from a replica that had cached the license 220 ms earlier _Evidence: VictoriaLogs: both GETs on `echopoint.1`; PATCH on Anchor between them_
    - **Why?** Echopoint reads licenses through the Anchor SDK cache, 30 s per replica, and the flow wrote the license on Anchor directly _Evidence: `anchorsdk/license.go` `defaultLicenseCacheTTL = 30 * time.Second`; `licenses/resolver.go` reads via the SDK_
      - **Why?** The flow guide covers projections that lag a write, not read caches in front of another service → **Root cause R1** (fixed by A1, A2, A4)
  - **Why?** Four earlier green runs hid the race: the two reads usually landed on different replicas _Evidence: A version with one extra request in between failed 3/3 at 00:17Z (parity shifted)_
    - **Why?** The routine's acceptance rule is three serial green runs, written for count races in one process _Evidence: Run notes: 'run any new or reshaped flow 3x before trusting it' (2026-10-05 count race)_
      - **Why?** Repeated serial runs do not vary replica placement, so they cannot prove a check free of per-replica state → **Root cause R2** (fixed by A1, A2)
  - **Why so bad?** A flow three runs old sat in a gate that holds the whole product's promotion
    - **Why?** The routine tags a flow into the gate as soon as it passes alone; the gate runs it beside 46 others _Evidence: Run notes coverage entry: green 3x + in the suite, tagged the same run_
      - **Why?** New flows join the gate tag with no soak period in the concurrent suite → **Root cause R3** (fixed by A3, A5)

## Root causes

- **R1** The flow guide covers projections that lag a write, not read caches in front of another service
- **R2** Repeated serial runs do not vary replica placement, so they cannot prove a check free of per-replica state
- **R3** New flows join the gate tag with no soak period in the concurrent suite

## Contributing factors

- The same gate also failed on a flow that pinned behaviour echopoint#733 changed on purpose, so the promotion was held either way.

## Lessons learned

### What went well

- VictoriaLogs task names showed the replica of each request, which made the cause provable in one query.

### What went wrong

- The first fix (poll, then read) passed review in my head and failed every run.

### Where we got lucky

- The flake fired in the same gate as a real failure, so it held nothing extra; next time it can hold a clean deploy.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Poll the limit in a module and end the flow on that poll | prevent | Nanostack routine (echopoint-investigation) | 2026-11-04 | done |  | R1, R2 |
| A2 | flow-suite-testing skill: a read behind a per-replica cache after a write that bypasses it is polled, and the poll is the final check | prevent | Nanostack routine (echopoint-investigation) | 2026-11-04 | done |  | R1, R2 |
| A3 | New flows run in the full concurrent tag twice before they are tagged into a gate | process | Nanostack routine (echopoint-investigation) | 2026-11-04 | done |  | R3 |
| A4 | Invalidate the Echopoint license cache on Anchor `organization.license.updated`, if Echopoint receives that event | mitigate | echopoint maintainers | 2026-11-30 | open |  | R1 |
| A5 | Routine reads every Deploy Router gate result each run and runs a red flow through this loop | detect | Nanostack routine (echopoint-investigation) | 2026-11-04 | done |  | R3 |

## Responders

- **Detection and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

The invitation email budget flow failed the echopoint gate on a 30 s license cache; it now polls. No product bug.

### Customers

None: dev and CI only.

## Supporting information

- [Report (artifact)](https://claude.ai/artifact/93ezZXvL7E99pDf7T81vg4)
- [Echopoint gate run](https://github.com/nanostack-dev/infra/actions/runs/41705330775)
- [SEV4 gate flows pinned old behaviour](https://claude.ai/artifact/Xxmi3NC6ppsTvwJDKYczLZ)

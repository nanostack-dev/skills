# Echopoint gate red: two flows raced Anchor's per-product licensing lock

| | |
|---|---|
| **Date** | 2026-11-08 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | flow-suite |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | 13m 51s (trigger to resolution) |
| **Time to detect** | 1m 58s |
| **Time to mitigate** | 9m 25s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

The echopoint post-deploy gate for `4bd153dc` (echopoint#786) failed at 17:42Z on one flow, so prod echopoint stayed on the previous commit for about 12 minutes. `echopoint: integration operation outputs` PATCHed its throwaway org's license and Anchor answered 409 `LICENSING_WRITE_IN_PROGRESS`: 2 ms earlier, `license gauges under concurrent creates` had PATCHed another org's license on the same Nanostack product, and Anchor serializes licensing writes per product with a try-lock that refuses at once (ADR-0018). The gate runs the tag in parallel, and seven echopoint flows now write licenses on that one product, none of them retrying the documented 409. The next merge's gate passed and promoted at 17:54Z. Every license PATCH on the shared product now goes through a module that repeats the PATCH while it answers 409.

## Impact

Dev and CI only. One echopoint deploy (test-only change) waited about 12 minutes for prod; no customer saw a change. No resource leaked: the flow's `always` cleanups deleted the throwaway org and key.

- **1/58** gate flows red
- **~12 min** prod promotion held
- **2 ms** between the competing PATCHes

## Trigger

At 17:40:42.072Z Anchor replica 1 refused `PATCH …/organizations/org_3Lpmyyl…/license` (409 in 758 µs) while replica 2 held the product's licensing lock for the `license gauges` PATCH (200 at .074Z).

## Detection

The Deploy Router gate failed at 17:42:40Z and named the node (`lic-stripe`, expected 200, got 409). The routine read it at 18:08Z and took the error code from the node result. Detection was good enough: the gate is the check.

## Resolution

The next echopoint merge (#787) passed its gate at 17:5xZ and promoted all of `main` to prod at 17:54:33Z. The permanent fix replaces every license PATCH on `{{nanostackProductId}}` with module `license: patch through the licensing lock` (`4606aa53`), which polls the PATCH until it answers the expected status.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| ~12:08 | T−2d 05h | **`license gauges` flow joins the echopoint tag** Its PATCH on the shared product sits right after org create, like most of the license flows. |
| ~18:08 | T−23h 32m | **`integration operation outputs` joins the tag** Seventh echopoint-tag flow to PATCH a license on the shared Nanostack product. |
| 17:33:17 | T−7m 25s | **echopoint#786 merged (test-only)** ([link](https://github.com/nanostack-dev/echopoint/pull/786)) |
| 17:39:40 | T−1m 02s | **Deploy Router 42506060864 starts** ([link](https://github.com/nanostack-dev/infra/actions/runs/42506060864)) |
| 17:40:42 | T+0s | **lic-stripe PATCH gets 409 LICENSING_WRITE_IN_PROGRESS** Replica 2 answered the `license gauges` PATCH 200 at .074Z; replica 1 refused this one at .072Z. VictoriaLogs `deployment.environment:dev`. |
| 17:42:40 | T+1m 58s | **Gate fails: 1 flow red, prod promotion skipped** ([link](https://github.com/nanostack-dev/infra/actions/runs/42506060864)) |
| 17:50:07 | T+9m 25s | **Next deploy (#787) starts; its gate passes** ([link](https://github.com/nanostack-dev/infra/actions/runs/42506923417)) |
| 17:54:33 | T+13m 51s | **Prod echopoint promoted** ([link](https://github.com/nanostack-dev/infra/actions/runs/42506923417)) |
| 18:08:51 | T+28m 09s | **Routine reads the red gate and the node result** |
| ~18:40 | T+59m 18s | **Retry module 4606aa53 created; flows switched** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The echopoint deploy of 4bd153dc did not reach prod: its post-deploy gate was red"]
  W1["`integration operation outputs` node lic-stripe expected 200 and got 409 LICENSING_WRITE_IN_PROGRESS"]
  W2["Another flow's license PATCH on the same Nanostack product held Anchor's licensing lock 2 ms earlier"]
  W3["Anchor takes a per-product try-lock for every licensing write and refuses a competing one at once"]
  W4["The flows send each license PATCH once and expect 200, though the contract says to retry the 409"]
  R1["R1 · No helper or guide rule makes a write to a provider-serialized resource retry its documented conflict"]
  W5["The throwaway-org pattern isolates each run's org, but every org lives in the one shared Nanostack product"]
  W6["Seven tag flows write licenses on that product, most right after org create, so their PATCHes cluster"]
  R2["R2 · Flow isolation was judged at the org, while the provider's lock scope is the product"]
  W7["Serial authoring runs and two tag soaks never showed it: the race needs two PATCHes within ~10 ms"]
  W8["The soak proves a flow alone, not its contention with siblings at gate parallelism"]
  R3["R3 · The authoring checklist has no step that lists shared locks a new flow writes through"]
  W9["One refused write failed the flow and held prod, though waiting 10 ms would have succeeded"]
  W10["Anchor refuses instead of waiting a bounded time, so every overlap becomes a client error"]
  R4["R4 · Org license writes share a product-wide zero-wait lock (code note: use finer locks if contention warrants)"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| W4
  W4 -->|why?| R1
  W2 -->|why?| W5
  W5 -->|why?| W6
  W6 -->|why?| R2
  W1 -->|why?| W7
  W7 -->|why?| W8
  W8 -->|why?| R3
  P -.->|why so bad?| W9
  W9 -->|why?| W10
  W10 -->|why?| R4
  class P problem
  class R1,R2,R3,R4 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The echopoint deploy of 4bd153dc did not reach prod: its post-deploy gate was red
  - **Why?** `integration operation outputs` node lic-stripe expected 200 and got 409 LICENSING_WRITE_IN_PROGRESS _Evidence: Gate log `✗ Flow 2e4b608f…`; node result `response_body_parsed.errors[0].code`_
    - **Why?** Another flow's license PATCH on the same Nanostack product held Anchor's licensing lock 2 ms earlier _Evidence: VictoriaLogs 17:40:42: replica 2 `PATCH …org_3Lpmyvw…/license -> 200`, replica 1 `-> 409 (758µs)`_
      - **Why?** Anchor takes a per-product try-lock for every licensing write and refuses a competing one at once _Evidence: anchor `license_write_lock.go` `TryAdvisoryXactLock`; ADR-0018 says the client retries_
        - **Why?** The flows send each license PATCH once and expect 200, though the contract says to retry the 409 _Evidence: 11 PATCH nodes in 7 echopoint-tag flows, plain request nodes with a status 200 or 400 assertion_
          - **Why?** No helper or guide rule makes a write to a provider-serialized resource retry its documented conflict → **Root cause R1** (fixed by A1, A2)
      - **Why?** The throwaway-org pattern isolates each run's org, but every org lives in the one shared Nanostack product _Evidence: All 11 PATCH URLs use `{{nanostackProductId}}`; the lock key is tenant + product_
        - **Why?** Seven tag flows write licenses on that product, most right after org create, so their PATCHes cluster _Evidence: Exports 2026-11-08; gauges added 11-06, integration flows 11-07_
          - **Why?** Flow isolation was judged at the org, while the provider's lock scope is the product → **Root cause R2** (fixed by A1)
    - **Why?** Serial authoring runs and two tag soaks never showed it: the race needs two PATCHes within ~10 ms _Evidence: 3 serial greens + 2 tag runs per new flow (Run notes); 14 green tag runs since 11-07_
      - **Why?** The soak proves a flow alone, not its contention with siblings at gate parallelism
        - **Why?** The authoring checklist has no step that lists shared locks a new flow writes through → **Root cause R3** (fixed by A2, A3)
  - **Why so bad?** One refused write failed the flow and held prod, though waiting 10 ms would have succeeded _Evidence: The holding PATCH took 9.9 ms_
    - **Why?** Anchor refuses instead of waiting a bounded time, so every overlap becomes a client error _Evidence: `withLicenseWrite` returns ErrLicensingWriteInProgress when the try-lock fails_
      - **Why?** Org license writes share a product-wide zero-wait lock (code note: use finer locks if contention warrants) → **Root cause R4** (fixed by A4)

## Root causes

- **R1** No helper or guide rule makes a write to a provider-serialized resource retry its documented conflict
- **R2** Flow isolation was judged at the org, while the provider's lock scope is the product
- **R3** The authoring checklist has no step that lists shared locks a new flow writes through
- **R4** Org license writes share a product-wide zero-wait lock (code note: use finer locks if contention warrants)

## Contributing factors

- The gate's rerun step reruns transport failures only, so a retryable 409 stays red.
- Gates followed each other quickly during the framework migration (six deploys in 30 minutes), which raised the number of gate runs exposed to the race.

## Lessons learned

### What went well

- The node result kept the response body, so the error code and the competing write were found in minutes.
- Every `always` cleanup completed: no leaked org or key.

### What went wrong

- Seven flows grew around one shared lock without anyone listing it.
- The same class (a provider lock that refuses at once) already showed with FLOW_TREE_CONFLICT on 2026-11-07 and was fixed per flow, not as a rule.

### Where we got lucky

- The held change was test-only, and another merge followed ten minutes later and promoted it.
- Anchor-tag flows PATCH licenses on their own products, so the two gates did not race each other.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Route every license PATCH on the shared product through module `4606aa53` (poll until the expected status) | prevent | Nanostack routine (echopoint-investigation) | 2026-11-08 | done |  | R1, R2 |
| A2 | flow-suite-testing rule: a write the provider serializes per shared scope retries its documented conflict in a poll module | process | Nanostack routine (echopoint-investigation) | 2026-11-08 | done |  | R1, R3 |
| A3 | Authoring checklist: name the provider locks a new flow writes through and grep the tag for siblings on the same scope | process | Nanostack routine (echopoint-investigation) | 2026-11-08 | done |  | R3 |
| A4 | Decide whether an org license write takes a per-org lock or waits a bounded time for the product lock (ADR-0018 change) | mitigate | Anchor maintainers | 2026-11-22 | open |  | R4 |

## Responders

- **Detection and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Echopoint gate red at 17:42Z on a flow-suite race: two flows PATCHed licenses on the shared Nanostack product 2 ms apart and Anchor's per-product lock refused one (409, documented). Prod held ~12 min until #787's gate. License PATCHes now retry the 409 through a poll module.

### Customers

None: dev and CI only.

## Supporting information

- [Atelier](http://nanostack-dev-1340p:4320/postmortems/01a1bc67-8f42-7de9-afb4-4a4545e563bb)
- [Deploy Router 42506060864](https://github.com/nanostack-dev/infra/actions/runs/42506060864)
- [echopoint#786](https://github.com/nanostack-dev/echopoint/pull/786)
- [Related: tree lock race](2026-11-07-suite-overlapped-deploy-gate.md)

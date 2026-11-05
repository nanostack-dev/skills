# The Daily echopoint monitor ran two security flows from stale published versions

| | |
|---|---|
| **Date** | 2026-11-05 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint flow suites (prod CI org, monitor `Daily echopoint`), echopoint flow versions |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | 3h 14m (trigger to resolution) |
| **Time to detect** | ~3h 10m |
| **Time to mitigate** | 3h 13m |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

At 09:00Z the `Daily echopoint` monitor failed two flows: `security — auth forgery & scheme boundaries` expected `BAD_REQUEST` and `security — ephemeral direct completion contract` expected `200`. Both had been updated to the echopoint#733 contract on 2026-11-04, and the gate and suite runs passed on them. A monitor runs a flow's latest **published** version, while `flows run` (suites and gate) runs the draft; these flows had versions published on 2026-10-17/20, and the 2026-11-04 updates were never published. Four flows had this drift. The routine published all four at 12:13Z and added a drift check to the suite script. Dev and CI only: the monitor calls the dev APIs and no deploy was held.

## Impact

Two red flows in the Daily monitor run on dev, a failure email to the monitor owner, and a monitor that tested a contract echopoint replaced on 2026-11-03. No prod deploy was held: the gate runs the drafts.

- **2 / 47** Daily monitor flows failed at 09:00Z
- **4** flows whose draft differed from the published version
- **3 h 11 min** from the failed run to the fix

## Trigger

The `Daily echopoint` monitor ran at 2026-11-05T09:00:04Z, the first run since 2026-11-01, and launched the latest published version of each selected flow.

## Detection

The routine read the monitor's scheduled executions at about 12:11Z while it checked that echopoint#742 had unblocked the Daily monitor. The monitor also emailed its owner on failure; nothing reads that email automatically.

## Resolution

`flows publish` on the four drifted flows at 12:13:10Z. A rescan at 12:14:41Z found no flow whose draft differs from its latest published version. The drafts are green in the suites and the gate, so the next Daily run uses green definitions.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| 04:17:18 | T−19d 04h | **Security tracker flows get published versions** The echopoint pentest session published versions of F-1, F-3, F-5 and auth forgery flows (`flows version list`). ([link](https://github.com/nanostack-dev/echopoint/pull/652)) |
| 01:59:36 | T−16d 07h | **Auth forgery flow published with BAD_REQUEST** Last published version of `f2f5ed74` asserts `BAD_REQUEST` on a blank organization id. |
| ~09:00 | T−4d 00h | **Daily echopoint stops running** Its fan-out never settled; fixed by echopoint#742. ([link](https://github.com/nanostack-dev/echopoint/pull/742)) |
| 00:10:42 | T−1d 08h | **Auth forgery draft updated to INVALID_ORGANIZATION_ID** The routine fixed the flow after echopoint#733 failed the 2026-11-03T19:41Z gate. It updated the draft only. ([link](https://github.com/nanostack-dev/echopoint/pull/733)) |
| 11:45:14 | T−21h 14m | **F-1 draft updated to 409 EPHEMERAL_JOB_COMPLETION_REQUIRED** Another session aligned the flow to #733. Draft only. |
| 12:16:23 | T−20h 43m | **F-3 and F-5 drafts updated** Renamed and given the workspace header. Draft only. |
| 09:00:04 | T+0s | **Daily monitor runs; two flows fail on old assertions** `expected=200 actual=409` and `expected=BAD_REQUEST actual=INVALID_ORGANIZATION_ID` (executions `01a1aaef-cba6…`, `01a1aaef-cb7a…`). |
| ~12:11 | T+3h 10m | **Routine finds the two failed scheduled runs** |
| ~12:12 | T+3h 11m | **Cause confirmed: monitors run the latest published version** `internal/feature/flowschedules/service.go` `latestPublishedVersionID`; draft vs version diff shows the assertions. |
| 12:13:10 | T+3h 13m | **Four drifted flows published** |
| 12:14:41 | T+3h 14m | **Rescan: no draft differs from its published version** |
| ~12:20 | T+3h 19m | **Suite script drift and monitor checks; skill lesson** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The Daily echopoint monitor failed two flows on behaviour echopoint changed on purpose two days earlier"]
  W1["The monitor ran versions of the flows published on 2026-10-17/20, not the updated definitions"]
  W2["A monitor launches a flow's latest published version, and a flow run from the CLI or gate launches the draft"]
  W3["The 2026-11-04 updates changed only the drafts; nobody published them"]
  W4["The fix procedure (update the gate flow, run it, see green) checks only the draft path"]
  R1["R1 · Nothing compares a flow's draft with its published version, so a suite or gate pass says nothing about what monitors run"]
  W5["`flows update` accepts a change to a flow with published versions without a word"]
  R2["R2 · The flow API and CLI do not tell an editor that monitors keep running an older published version"]
  W6["The failure stayed unseen for three hours and the drift for a day"]
  W7["The Daily monitor did not run from 2026-11-01 to 2026-11-05, so no earlier run showed the drift"]
  R4["R4 · A fan-out settle bug kept scheduled runs from finishing, so the monitor skipped every day (fixed by echopoint#742)"]
  W8["A failed monitor run only emails the monitor owner; the routine reads gate runs, not monitor runs"]
  R3["R3 · The routine had no step that lists failed scheduled runs in the suite org"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| W4
  W4 -->|why?| R1
  W3 -->|why?| W5
  W5 -->|why?| R2
  P -.->|why so bad?| W6
  W6 -->|why?| W7
  W7 -->|why?| R4
  W6 -->|why?| W8
  W8 -->|why?| R3
  class P problem
  class R1,R2,R4,R3 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The Daily echopoint monitor failed two flows on behaviour echopoint changed on purpose two days earlier
  - **Why?** The monitor ran versions of the flows published on 2026-10-17/20, not the updated definitions _Evidence: Scheduled runs asserted `200` and `BAD_REQUEST`; only the published versions hold those values (`flows version list` diff)_
    - **Why?** A monitor launches a flow's latest published version, and a flow run from the CLI or gate launches the draft _Evidence: `flowschedules/service.go:521` `latestPublishedVersionID`; `flows launch` and `flows run` take no version_
      - **Why?** The 2026-11-04 updates changed only the drafts; nobody published them _Evidence: Draft `updated_at` 2026-11-04, latest version 2026-10-17/20_
        - **Why?** The fix procedure (update the gate flow, run it, see green) checks only the draft path _Evidence: Workspace AGENTS.md cross-repo rule and skills `flow-suite-testing` named no publish step_
          - **Why?** Nothing compares a flow's draft with its published version, so a suite or gate pass says nothing about what monitors run → **Root cause R1** (fixed by A1, A2, A3)
        - **Why?** `flows update` accepts a change to a flow with published versions without a word _Evidence: echopoint-cli `flows update` output: no warning about published versions_
          - **Why?** The flow API and CLI do not tell an editor that monitors keep running an older published version → **Root cause R2** (fixed by A4)
  - **Why so bad?** The failure stayed unseen for three hours and the drift for a day _Evidence: Drift from 2026-11-04T00:10Z; failed run 09:00Z; found 12:11Z_
    - **Why?** The Daily monitor did not run from 2026-11-01 to 2026-11-05, so no earlier run showed the drift _Evidence: No scheduled executions of `1d02b3cf` before 2026-11-05T09:00Z since 2026-11-01; echopoint#742_
      - **Why?** A fan-out settle bug kept scheduled runs from finishing, so the monitor skipped every day (fixed by echopoint#742) → **Root cause R4** (fixed by A6)
    - **Why?** A failed monitor run only emails the monitor owner; the routine reads gate runs, not monitor runs _Evidence: Monitor `recipient_emails` = owner only; Run notes checked Deploy Router gates only_
      - **Why?** The routine had no step that lists failed scheduled runs in the suite org → **Root cause R3** (fixed by A5)

## Root causes

- **R1** Nothing compares a flow's draft with its published version, so a suite or gate pass says nothing about what monitors run
- **R2** The flow API and CLI do not tell an editor that monitors keep running an older published version
- **R4** A fan-out settle bug kept scheduled runs from finishing, so the monitor skipped every day (fixed by echopoint#742)
- **R3** The routine had no step that lists failed scheduled runs in the suite org

## Contributing factors

- The two other drifted flows (F-3, F-5) passed: their drafts differ only by the workspace header, and their published assertions already expected the fixed contract.
- Most suite flows have no published version, so the monitor runs their drafts; the four tracker flows were the exception.

## Lessons learned

### What went well

- The monitor's per-flow error message named the expected and actual values, so the stale version was found in two queries.
- The flow version API keeps every published definition, so the diff proved the cause.

### What went wrong

- Three sessions updated these flows on 2026-11-04 and none checked whether they had published versions.
- The routine's Run notes described the monitor as a runner of tags, not of published versions.

### Where we got lucky

- The gate runs drafts. Had the gate run published versions, the #733 fix would have held echopoint prod.
- The drift hit a dev-only CI monitor. A customer's monitor or a public status page flow with a stale published version would report a false outage.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Publish the four drifted flows and rescan for drift | mitigate | Nanostack routine (echopoint-investigation) | 2026-11-05 | done |  | R1 |
| A2 | `run_suites.sh` prints `PUBLISH-DRIFT` for each tag flow whose draft differs from its latest published version | detect | Nanostack routine (echopoint-investigation) | 2026-11-05 | done |  | R1 |
| A3 | `flow-suite-testing` skill: find which version each caller runs; publish after updating a published flow | process | Nanostack routine (echopoint-investigation) | 2026-11-05 | done |  | R1 |
| A4 | echopoint-cli `flows update` (and the flow editor) warn when the flow has a published version that monitors keep running | prevent | echopoint-cli maintainers | 2026-11-19 | open |  | R2 |
| A5 | `run_suites.sh` prints `MONITOR-FAILED` for every failed scheduled run in the last 24 h; the routine triages each | detect | Nanostack routine (echopoint-investigation) | 2026-11-05 | done |  | R3 |
| A6 | Settle schedule runs whose executions are no longer visible (echopoint#742) | prevent | echopoint maintainers | 2026-11-04 | done |  | R4 |

## Responders

- **Detection and fix**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

The Daily echopoint monitor failed two security flows at 09:00Z because monitors run the latest published flow version and the 2026-11-04 fixes changed only drafts. Published; the suite script now flags draft/published drift.

### Customers

None: dev and CI only.

## Supporting information

- [Atelier postmortem](http://nanostack-dev-1340p:4320/postmortems/01a1aba4-55d7-7b7b-b6ae-d69581e443b2)
- [echopoint#733 (contract change)](https://github.com/nanostack-dev/echopoint/pull/733)
- [echopoint#742 (Daily monitor unblocked)](https://github.com/nanostack-dev/echopoint/pull/742)
- [SEV4 gate flows pinned old behaviour](https://claude.ai/artifact/Xxmi3NC6ppsTvwJDKYczLZ)

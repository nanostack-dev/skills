# Echopoint suite red: the routine host's CLI predated email_wait when a gate flow gained an email wait

| | |
|---|---|
| **Date** | 2026-11-12 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint flow suite (routine host) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~6m 00s (trigger to resolution) |
| **Time to detect** | ~1m 00s |
| **Time to mitigate** | ~4m 00s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

At 17:35Z another session added an email wait to `echopoint: daily invitation email limit`, a flow in the `echopoint` gate tag. CLI v3.15.0, the first release that declares the `email_wait` runner capability, was released at 16:53Z, but the routine host still ran v3.14.3. At 18:16Z the routine's echopoint suite failed the flow: the API refused the embedded runner's claim and told it to upgrade the CLI. The gate installs the latest CLI and the Cloud worker pins runner v0.108.0, so only the routine host was affected. `run_suites.sh` now updates the CLI in its preflight and prints the version; the flow is green 2x on v3.15.0.

## Impact

Routine host only. One red flow in one run (echopoint 59/60). Gates, monitors and customers were unaffected.

- **1 of 60** echopoint flows red
- **~80 min** between the release and the failing run

## Trigger

The routine ran the echopoint tag with CLI v3.14.3 after the flow gained an `email_wait` node.

## Detection

`run_suites.sh` printed FAILED with the CLI's own message: the runner that claimed it cannot run an email wait; upgrade the CLI.

## Resolution

`echopoint update` to v3.15.0, two green reruns, and an update step in the `run_suites.sh` preflight.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| 16:04:21 | T−2h 11m | **echopoint#850: email wait behind a runner capability gate** ([link](https://github.com/nanostack-dev/echopoint/pull/850)) |
| 16:53:27 | T−1h 22m | **CLI v3.15.0 released (declares email_wait)** ([link](https://github.com/nanostack-dev/echopoint-cli/releases/tag/v3.15.0)) |
| 17:35:55 | T−40m 05s | **Gate flow 1342edd0 gains an email wait** |
| ~18:16 | T+0s | **Routine runs the flow on host CLI v3.14.3** |
| ~18:17 | T+1m 00s | **run_suites.sh prints FAILED: upgrade the CLI** |
| ~18:20 | T+4m 00s | **Host CLI updated to v3.15.0** |
| ~18:22 | T+6m 00s | **Flow green 2x on v3.15.0** |
| ~18:30 | T+14m 00s | **run_suites.sh updates the CLI in its preflight** |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The routine's echopoint suite failed `daily invitation email limit` with an upgrade-the-CLI refusal"]
  W1["The host CLI v3.14.3 embeds a runner that does not declare email_wait, and the flow now has an email wait"]
  W2["The routine kept whatever CLI the host had; only the gate installs the latest release"]
  R1["R1 · `run_suites.sh` had no step that keeps the host CLI on the released version"]
  W3["The refusal showed up as a product failure in the run summary"]
  W4["`run_suites.sh` prints FAILED for any failed flow and showed no CLI version"]
  R2["R2 · The suite report did not name the CLI it ran, so a version gap looked like a flow failure"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| R1
  P -.->|why so bad?| W3
  W3 -->|why?| W4
  W4 -->|why?| R2
  class P problem
  class R1,R2 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The routine's echopoint suite failed `daily invitation email limit` with an upgrade-the-CLI refusal
  - **Why?** The host CLI v3.14.3 embeds a runner that does not declare email_wait, and the flow now has an email wait _Evidence: `echopoint version` v3.14.3; flow 1342edd0 updated 17:35:55Z; claim refused with the upgrade message_
    - **Why?** The routine kept whatever CLI the host had; only the gate installs the latest release _Evidence: Gate job log `cli_version: latest`_
      - **Why?** `run_suites.sh` had no step that keeps the host CLI on the released version → **Root cause R1** (fixed by A1)
  - **Why so bad?** The refusal showed up as a product failure in the run summary
    - **Why?** `run_suites.sh` prints FAILED for any failed flow and showed no CLI version
      - **Why?** The suite report did not name the CLI it ran, so a version gap looked like a flow failure → **Root cause R2** (fixed by A2)

## Root causes

- **R1** `run_suites.sh` had no step that keeps the host CLI on the released version
- **R2** The suite report did not name the CLI it ran, so a version gap looked like a flow failure

## Contributing factors

- The flow change and the CLI release landed the same afternoon, between two routine runs.

## Lessons learned

### What went well

- The API refused with a message that named the fix.
- The gate and the Cloud worker were already current.

### What went wrong

- The routine host drifted from the client customers get by default.

### Where we got lucky

- The flow change came after the CLI release; the gate would have run the new flow green.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | `run_suites.sh` preflight runs `echopoint update` before the tags | prevent | Nanostack routine (echopoint-investigation) | 2026-11-12 | done |  | R1 |
| A2 | `run_suites.sh` prints `CLI <version>` and `CLI-UPDATED`/`CLI-UPDATE-FAILED` | detect | Nanostack routine (echopoint-investigation) | 2026-11-12 | done |  | R2 |

## Responders

- **Investigation**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Echopoint suite red on daily invitation email limit: the routine host CLI predated email_wait. CLI updated, preflight now updates it. Host only.

## Supporting information

- [echopoint#850](https://github.com/nanostack-dev/echopoint/pull/850)
- [Atelier](http://nanostack-dev-1340p:4320/postmortems/01a1d106-f49f-7e01-bdbb-3d89900c1622)

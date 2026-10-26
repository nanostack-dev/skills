# Suite run blind: the routine's prod CLI session expired after 7 days and nothing could renew it

| | |
|---|---|
| **Date** | 2026-10-26 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint-investigation routine (prod-org flow suites on dev) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~3h 23m (trigger to resolution) |
| **Time to detect** | 2h 47m |
| **Time to mitigate** | ~3h 08m |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

The 23:08Z run of the scheduled flow-suite routine checked no flow: both `flows run --tag` calls exited 1 with `stored credentials have expired`. The routine's `prod` CLI profile held only a browser session, a JWT with a fixed 7-day life and no refresh token, signed in on 2026-10-19T20:21Z; it expired at 2026-10-26T20:21Z. Nothing warned before expiry, the CLI never falls back to a stored API key once a session expired, and the routine cannot sign in by itself. Post-deploy gates and the Daily schedule were unaffected (they use their own credentials), and no backend change merged in the window. The suite runner now checks the credential before launching; a CLI fallback awaits review; a human must store a CI-org API key to end the class.

## Impact

One routine run (of four a day) checked 0 of 66 flows; coverage of new dev merges stays blind until a human signs in again. Customers saw nothing: the flows only target dev, and the gates and Daily schedule run with separate credentials.

- **0 / 66** flows checked at 23:08Z
- **7 days** fixed session life, no refresh
- **2 h 47 min** from expiry to detection

## Trigger

The `prod` profile's session JWT reached its `exp` at 2026-10-26T20:21:26Z.

## Detection

The next scheduled run (23:08Z) saw both suite launches exit 1 within a second; `anchor.log` and `echopoint.log` held `stored credentials have expired`. The expiry date had been visible in `echopoint auth status` for 7 days, but nothing read it.

## Resolution

Not resolved by the routine: re-authentication needs a person at a browser, and the routine never enters credentials. `run_suites.sh` now stops with `AUTH-EXPIRED` and warns `AUTH-EXPIRES-SOON` 48 h ahead; a CLI change lets a stored API key replace an expired session.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| 20:21:26 | T−7d 00h | **Prod CLI profile signed in by browser (7-day JWT)** `exp` minus 7 days; the login is also noted in the routine's Run notes (credential written without `organization_id`). |
| ~17:20 | T−3h 01m | **Last green suite run ends (anchor 27/27, echopoint 39/39)** |
| 20:21:26 | T+0s | **Session JWT expires** `~/.echopoint/credentials/prod.json` `expires_at` 2026-10-26T16:21:26-04:00, keys `access_token`, `expires_at`, `organization_id`: no refresh token, no API key. |
| 23:08:47 | T+2h 47m | **Both suite tags exit 1: credentials expired** `run_suites.sh` output `anchor: exit 1 pass 0 fail 0`, `echopoint: exit 1 pass 0 fail 0`. |
| ~23:30 | T+3h 08m | **Preflight added: AUTH-EXPIRED / AUTH-EXPIRES-SOON** The runner now stops with an actionable line and warns 48 h before the next expiry. |
| ~23:45 | T+3h 23m | **Impact bounded: run reported, human sign-in requested** Suites stay blind until a person signs in or stores an API key (action A1). |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The 23:08Z routine run checked no flow, so a dev regression merged now would go unseen"]
  W1["Every `flows run --profile prod` exited 1 with `stored credentials have expired` before launching"]
  W2["The prod profile held only a browser session: a JWT with a fixed 7-day `exp` and no refresh token"]
  W3["The routine runs unattended four times a day but signs in as a person, the way an interactive user does"]
  R1["R1 · No non-expiring credential (a CI-org API key) is set up for unattended suite runs on the routine host"]
  W4["A stored API key would not have helped: the CLI fails on an expired session before it looks at a stored key"]
  R2["R2 · CLI command auth treats an expired session as fatal even when a stored (or preferred) API key exists"]
  W5["Nobody knew ahead: the expiry date sat in `auth status` for 7 days and the run found out only after the fact"]
  W6["`run_suites.sh` launched the suites without reading the credential"]
  R3["R3 · The suite runner had no credential preflight and no warning before expiry"]
  W7["Recovery waits for a person: the routine cannot sign in by itself and must not handle passwords"]
  W8["Browser sign-in is the only credential the host holds, and it needs a person at a browser"]
  R4["R4 · The routine has no credential path it can renew without a person (same gap as R1)"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| R1
  W1 -->|why?| W4
  W4 -->|why?| R2
  P -.->|why so bad?| W5
  W5 -->|why?| W6
  W6 -->|why?| R3
  P -.->|why so bad?| W7
  W7 -->|why?| W8
  W8 -->|why?| R4
  class P problem
  class R1,R2,R3,R4 root
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The 23:08Z routine run checked no flow, so a dev regression merged now would go unseen
  - **Why?** Every `flows run --profile prod` exited 1 with `stored credentials have expired` before launching _Evidence: `runs/2026-10-26T2308/anchor.log` and `echopoint.log`_
    - **Why?** The prod profile held only a browser session: a JWT with a fixed 7-day `exp` and no refresh token _Evidence: `prod.json` keys; `tokenExpiry` reads `exp` from the JWT (`echopoint-cli/internal/auth/browser.go`)_
      - **Why?** The routine runs unattended four times a day but signs in as a person, the way an interactive user does
        - **Why?** No non-expiring credential (a CI-org API key) is set up for unattended suite runs on the routine host → **Root cause R1** (fixed by A1, A4)
    - **Why?** A stored API key would not have helped: the CLI fails on an expired session before it looks at a stored key _Evidence: `resolveToken` returns the expiry error before `resolveStoredAPIKey` (`internal/commands/root.go`); `echopoint mcp` already falls back (`mcp.go`)_
      - **Why?** CLI command auth treats an expired session as fatal even when a stored (or preferred) API key exists → **Root cause R2** (fixed by A2)
  - **Why so bad?** Nobody knew ahead: the expiry date sat in `auth status` for 7 days and the run found out only after the fact
    - **Why?** `run_suites.sh` launched the suites without reading the credential
      - **Why?** The suite runner had no credential preflight and no warning before expiry → **Root cause R3** (fixed by A3, A4)
  - **Why so bad?** Recovery waits for a person: the routine cannot sign in by itself and must not handle passwords
    - **Why?** Browser sign-in is the only credential the host holds, and it needs a person at a browser
      - **Why?** The routine has no credential path it can renew without a person (same gap as R1) → **Root cause R4** (fixed by A1)

## Root causes

- **R1** No non-expiring credential (a CI-org API key) is set up for unattended suite runs on the routine host
- **R2** CLI command auth treats an expired session as fatal even when a stored (or preferred) API key exists
- **R3** The suite runner had no credential preflight and no warning before expiry
- **R4** The routine has no credential path it can renew without a person (same gap as R1)

## Contributing factors

- The `dev` profile (used by the `echopoint_dev` MCP) is a browser session too and expires at 2026-10-27T03:03Z.
- The 2026-10-19 sign-in already broke one run (missing `organization_id`); that fix pinned the org but did not question the credential type.

## Lessons learned

### What went well

- The CLI error named the cause and the fix, so diagnosis took one command.
- Gates and the Daily schedule use separate credentials, so prod promotion checks were unaffected.

### What went wrong

- A known expiry date went unread for 7 days.
- The CLI's fallback to a stored API key works in `echopoint mcp` but not in commands, so the obvious mitigation would also have failed.

### Where we got lucky

- No echopoint, anchor, runner or CLI change merged during the blind window.
- The expiry hit between runs, not during one: a mid-run expiry would have left half-run flows and leaked cleanup.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Create a CI-org API key for the routine and store it on the host with `echopoint auth login --profile prod --api-key <key> --default` (and the same for `dev` if the dev MCP must stay up); sign in again meanwhile | prevent | Workspace owner (human) | 2026-10-28 | open |  | R1, R4 |
| A2 | CLI commands fall back to a stored API key when the session expired, like `echopoint mcp` | prevent | echopoint-cli maintainers | 2026-10-30 | open | [echopoint-cli#81](https://github.com/nanostack-dev/echopoint-cli/pull/81) | R2 |
| A3 | `run_suites.sh` preflight: stop with `AUTH-EXPIRED`, warn `AUTH-EXPIRES-SOON` 48 h ahead, skip when an API key is preferred | detect | Nanostack routine (echopoint-investigation) |  | done |  | R3 |
| A4 | flow-suite-testing skill: an unattended run signs in with an org API key and checks it before launching | process | Nanostack routine (echopoint-investigation) |  | done |  | R1, R3 |

## Responders

- **Detection and write-up**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Flow suites did not run at 23:08Z: the routine's prod CLI session expired (7-day browser JWT). Please sign in again, ideally store a CI-org API key with `--default`. Gates and Daily are unaffected.

### Customers

None: dev-only test infrastructure.

## Supporting information

- [Postmortem report](https://claude.ai/artifact/MHmBmRaALmA1yYysNNbJpv)
- [echopoint-cli#81 (A2, waiting review)](https://github.com/nanostack-dev/echopoint-cli/pull/81)
- [Suite run host sleep (earlier routine-host postmortem)](https://github.com/nanostack-dev/skills/blob/main/docs/postmortems/2026-10-17-suite-run-host-sleep.md)

# Scheduled flow suites ran blind: the host's VPN dropped Go TLS handshakes while curl still worked

| | |
|---|---|
| **Date** | 2026-10-30 |
| **Severity** | SEV4 |
| **Status** | In review |
| **Service** | echopoint-investigation routine (prod-org dogfood suites on dev APIs) |
| **Authors** | Nanostack routine (echopoint-investigation) |
| **Duration** | ~1h 11m (trigger to resolution) |
| **Time to detect** | 1m 39s |
| **Time to mitigate** | ~59m 07s |

> Blameless: this document names systems, processes and missing guards, not people.

## Summary

The 05:08Z scheduled run of the anchor and echopoint dogfood suites checked **0 of 68 flows**. Both tags exited 3 before launching anything: the CLI could not finish a TLS handshake with `api.echopoint.dev`. The laptop that hosts the suites routes IPv4 through a VPN tunnel, and on that path TLS handshakes from Go, Python and OpenSSL got no answer for an hour or more, even with a 166-byte ClientHello. SecureTransport curl on the same path still worked, so the usual `/health` probe said the network was fine. `run_suites.sh` now probes the control plane with the CLI itself and stops with `NETWORK-DOWN` instead of reporting `pass 0 fail 0`. Product coverage did not change: the CI post-deploy gate had run the anchor suite green on the same commits at 04:21Z.

## Impact

One scheduled suite run produced no result. No customer impact and no product signal lost: dev and prod already served the commits the CI gate had tested. About 60 min of routine time went to diagnosis instead of coverage.

- **0 / 68** flows checked in the 05:08Z run
- **60+ min** CLI unable to complete TLS
- **0** customer-visible effects

## Trigger

At 05:08:17Z `run_suites.sh` started both tags; each `flows run --tag` timed out on `POST https://api.echopoint.dev/flows/search` and exited 3.

## Detection

The routine read `anchor: exit 3 pass 0 fail 0` at 05:09:56Z. The cause took longer: a curl `/health` probe answered 200 in 40 ms, which pointed away from the network until Go, Python and OpenSSL handshakes were tested one by one.

## Resolution

No mitigation was in the routine's reach: changing the host's VPN is a system setting for a human. The run was closed as blind. `run_suites.sh` gained a CLI-based reachability preflight that waits up to 10 min and then exits 4 with `NETWORK-DOWN`, the default-route interface and the curl result.

## Timeline (UTC)

| Time | | Event |
|---|---|---|
| 23:08:00 | T−6h 00m | **Last suite run green on this host (anchor 28, echopoint 39)** Recorded in the routine's run log. |
| ~04:09 | T−58m 39s | **VPN log starts: tunnel up, NetShield 2, split-tcp on** Earliest line of the rotated ProtonVPN log; the connect time itself is not in the log. |
| 04:21:33 | T−46m 44s | **CI gate runs the anchor suite green on 206b6eed** ([link](https://github.com/nanostack-dev/infra/actions/runs/41002447291)) |
| 05:08:17 | T+0s | **Both tags exit 3: flows/search times out** `Client.Timeout exceeded while awaiting headers`; no flow launched. |
| 05:09:56 | T+1m 39s | **Routine reads `exit 3 pass 0 fail 0` and the CLI log** |
| 05:10:48 | T+2m 31s | **Rerun fails the same way: `TLS handshake timeout`** |
| ~05:15 | T+6m 43s | **curl /health 200 in 40 ms; IPv6 path dead; gh fails** curl uses SecureTransport and falls back to IPv4. `gh` (Go) also gets `TLS handshake timeout` on api.github.com. |
| 05:32:08 | T+23m 51s | **10-min recovery poll ends: CLI still down** |
| ~05:40 | T+31m 43s | **OpenSSL, Python TLS 1.2/1.3 fail; 1400-byte DF ping passes** `openssl s_client` writes a 166-byte ClientHello and reads 0 bytes from 172.64.80.1, so packet size is not the cause. |
| 06:03:38 | T+55m 21s | **15-min recovery poll ends: CLI still down** |
| ~06:07 | T+59m 07s | **NETWORK-DOWN preflight added to run_suites.sh** |
| ~06:20 | T+1h 11m | **Run closed as blind; next run re-probes at 11:08Z** The CLI still timed out at 06:07Z. The next scheduled run stops with `NETWORK-DOWN` if the path is still broken. |

## Root cause analysis: the five whys

Start at the impact and ask why until the answer is something the team can change. Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.

```mermaid
flowchart TD
  P["The 05:08Z scheduled suite run checked 0 of 68 flows; the routine had no suite result for that window"]
  W1["Both tags exited 3 before launching: the CLI's first request to the control plane never completed TLS"]
  W2["On this host, Go, Python and OpenSSL TLS handshakes got 0 bytes back from every tested HTTPS host; SecureTransport curl did not"]
  W3["Packet size is not the cause: 1400-byte DF pings pass and a 166-byte ClientHello also gets no answer"]
  W4["The IPv4 default route is a VPN tunnel with NetShield and split-tcp on; which part drops non-Apple handshakes is unconfirmed"]
  W5["The suite's network path is whatever the laptop's owner configured for personal use that day"]
  R1["R1 · Scheduled suites run on a personal laptop, so its VPN, Wi-Fi and sleep settings decide if a run can happen"]
  W6["The run reported `exit 3 pass 0 fail 0` twice and took about an hour to name as a host network fault"]
  W7["`run_suites.sh` checked auth expiry and kept the host awake, but never proved the CLI could reach the API"]
  R2["R2 · The suite script assumed the control plane was reachable and had no distinct outcome for a launch-time network failure"]
  W8["The first network check, curl `/health`, passed and pointed the diagnosis away from the network"]
  R3["R3 · Reachability was probed with a different TLS stack than the client under test, and nothing said that probe can mislead"]
  P -->|why?| W1
  W1 -->|why?| W2
  W2 -->|why?| W3
  W3 -->|why?| W4
  W2 -->|why?| W5
  W5 -->|why?| R1
  P -.->|why so bad?| W6
  W6 -->|why?| W7
  W7 -->|why?| R2
  W6 -->|why?| W8
  W8 -->|why?| R3
  class P problem
  class R1,R2,R3 root
  class W4 open
  classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210
  classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold
  classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00
```

- **Problem:** The 05:08Z scheduled suite run checked 0 of 68 flows; the routine had no suite result for that window
  - **Why?** Both tags exited 3 before launching: the CLI's first request to the control plane never completed TLS _Evidence: `error: search flows by tag: Post "https://api.echopoint.dev/flows/search": net/http: TLS handshake timeout` in `anchor.log` and `echopoint.log` of the run_
    - **Why?** On this host, Go, Python and OpenSSL TLS handshakes got 0 bytes back from every tested HTTPS host; SecureTransport curl did not _Evidence: `openssl s_client -tls1_2` to 172.64.80.1: `read 0 bytes and written 166 bytes`; `curl -4` same IP: 200, TLS done in 36 ms; Python `ssl` TimeoutError for TLS 1.2 and 1.3_
      - **Why?** Packet size is not the cause: 1400-byte DF pings pass and a 166-byte ClientHello also gets no answer _Evidence: `ping -D -s 1372 172.64.80.1`: 0% loss; `GODEBUG=tlsmlkem=0` (smaller Go hello) still times out_
        - **Why?** The IPv4 default route is a VPN tunnel with NetShield and split-tcp on; which part drops non-Apple handshakes is unconfirmed _Evidence: `netstat -rn`: default via utun7 (10.2.0.2, MTU 1420); ProtonVPN log: `netshield-level: 2`, `split-tcp: true`_ → _open, still investigating_
      - **Why?** The suite's network path is whatever the laptop's owner configured for personal use that day _Evidence: The suites run on the CLI's embedded runner on the developer laptop (Run notes; 2026-10-17 host-sleep postmortem A3 still open)_
        - **Why?** Scheduled suites run on a personal laptop, so its VPN, Wi-Fi and sleep settings decide if a run can happen → **Root cause R1** (fixed by A1, A2)
  - **Why so bad?** The run reported `exit 3 pass 0 fail 0` twice and took about an hour to name as a host network fault
    - **Why?** `run_suites.sh` checked auth expiry and kept the host awake, but never proved the CLI could reach the API _Evidence: `run_suites.sh` before this change: preflight checks `expires_at` only; its transport rerun handles failed flows, not a launch that selected none_
      - **Why?** The suite script assumed the control plane was reachable and had no distinct outcome for a launch-time network failure → **Root cause R2** (fixed by A3)
    - **Why?** The first network check, curl `/health`, passed and pointed the diagnosis away from the network _Evidence: curl 8.7.1 (SecureTransport) to `api.echopoint.dev/health`: 200 in 40 ms while the CLI timed out_
      - **Why?** Reachability was probed with a different TLS stack than the client under test, and nothing said that probe can mislead → **Root cause R3** (fixed by A4)

## Root causes

- **R1** Scheduled suites run on a personal laptop, so its VPN, Wi-Fi and sleep settings decide if a run can happen
- **R2** The suite script assumed the control plane was reachable and had no distinct outcome for a launch-time network failure
- **R3** Reachability was probed with a different TLS stack than the client under test, and nothing said that probe can mislead

## Contributing factors

- IPv6 was also black-holed on the host, and GitHub DNS failed for about 20 minutes, which hid the TLS pattern behind more general noise.
- The VPN log rotates and starts at 04:09Z, so when the tunnel or its features changed after the last green run (23:08Z) is not on record.

## Lessons learned

### What went well

- The run did not report a red suite or file product bugs: `exit 3` with zero flows was read as a launch failure, not as test results.
- Testing the handshake with four TLS clients and two packet sizes separated a host-path fault from an MTU or server fault in minutes.

### What went wrong

- A curl health check stood in for the CLI's reachability; it passed while the CLI could not connect at all.
- Two fixed-length recovery polls (10 and 15 min) spent the run's time without new information.

### Where we got lucky

- The CI post-deploy gate had run the anchor suite green on the same commits 47 min earlier, so no merged change went untested.
- anchor#284 and #287 had already been covered by another session; a merge that needed new flows would have gone uncovered this run.
- git (SecureTransport) and the REST API through curl still reached GitHub, so the fix and this report could still ship while `gh` could not.

## Action items

| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |
|---|---|---|---|---|---|---|---|
| A1 | Decide the suite host: an always-on machine on a plain network, or Cloud launches for the scheduled runs (same decision as the 2026-10-17 A3) | prevent | Nanostack maintainers | 2026-11-13 | open |  | R1 |
| A2 | Until A1: exclude `*.echopoint.dev` and `*.tryanchor.dev` from the VPN tunnel on the suite host, or confirm which VPN feature drops the handshakes | mitigate | Laptop owner | 2026-11-06 | open |  | R1 |
| A3 | `run_suites.sh` probes the control plane with the CLI itself, waits up to 10 min, then exits 4 with `NETWORK-DOWN`, the route interface and the curl result | detect | Nanostack routine (echopoint-investigation) |  | done |  | R2 |
| A4 | flow-suite-testing: probe reachability with the client that runs the suite, since another TLS stack can pass where it fails | process | Nanostack routine (echopoint-investigation) |  | done |  | R3 |

## Responders

- **Detection and write-up**: Nanostack routine (echopoint-investigation)

## Messaging

### Internal

Scheduled flow suites (05:08Z) checked 0 flows: on the suite laptop the VPN path drops Go/OpenSSL TLS handshakes; curl still works. No product signal lost (CI gate green at 04:21Z). run_suites.sh now stops with NETWORK-DOWN. Needed: decide the suite host, or exclude the API hosts from the VPN.

### Customers

None: dev and CI tooling only.

## Supporting information

- [Postmortem report](https://claude.ai/artifact/WvHsuSKxdJ7Lqt4szExThR)
- [Suite run host sleep (same host, 2026-10-17)](https://github.com/nanostack-dev/skills/blob/main/docs/postmortems/2026-10-17-suite-run-host-sleep.md)
- [Suite transport reset (2026-10-21)](https://github.com/nanostack-dev/skills/blob/main/docs/postmortems/2026-10-21-suite-transport-reset.md)
- [CI anchor gate green at 04:21Z](https://github.com/nanostack-dev/infra/actions/runs/41002447291)

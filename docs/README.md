# Skill maintenance documentation

Start with [agent guidance](../AGENTS.md), [vocabulary](../CONTEXT.md) and the [skill catalog](../README.md).

- [Architecture](technical/architecture.md).
- [Setup](development/setup.md), [testing](development/testing.md), [troubleshooting](development/troubleshooting.md).
- [Publishing](runbooks/deployment.md), [rollback](runbooks/rollback.md), [ADRs](adr/README.md).
- Existing postmortems: [flow-count race](postmortems/2026-10-05-specs-flow-count-race.md), [search-indexing race](postmortems/2026-10-06-specs-search-indexing-race.md), [suite run host sleep](postmortems/2026-10-17-suite-run-host-sleep.md), [suite transport reset](postmortems/2026-10-21-suite-transport-reset.md), [reset leaked cleanup](postmortems/2026-10-23-suite-transport-reset-leaked-cleanup.md), [suite CLI session expired](postmortems/2026-10-26-suite-cli-session-expired.md), [suite host TLS blackhole](postmortems/2026-10-30-suite-host-network-tls.md), [license cache gate flake](postmortems/2026-11-03-license-cache-gate-flake.md), [gate tag flow cap](postmortems/2026-11-04-gate-tag-flow-cap.md), [monitor ran a stale published flow](postmortems/2026-11-05-monitor-ran-stale-published-flow.md), [suite CLI session expired again](postmortems/2026-11-05-suite-cli-session-expired-again.md), [suite overlapped deploy gate](postmortems/2026-11-07-suite-overlapped-deploy-gate.md), [gate licensing lock race](postmortems/2026-11-08-gate-licensing-lock-race.md), [event retry after clear](postmortems/2026-11-12-event-delivery-retry-after-clear.md), [suite CLI behind email_wait](postmortems/2026-11-12-suite-cli-behind-email-wait.md), [teardown check raced org delete](postmortems/2026-11-14-teardown-check-raced-org-delete.md), [monitor launch refusal](postmortems/2026-11-14-monitor-target-refused-at-launch.md). Each has its `.json` source and the standalone `.html` report beside it.
- Skill-owned examples/resources remain beside their SKILL.md; the catalog supplies their entry points.

New optional research/postmortems should capture actual evidence and prevention.

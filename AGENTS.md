# Nanostack skills agent guide

This repository owns portable agent procedures, plugin metadata and the scripts/templates used by those procedures. It is independently cloneable; its local guides supply maintenance instructions.

Read [CONTEXT.md](CONTEXT.md), [docs/README.md](docs/README.md) and [architecture](docs/technical/architecture.md) before changing skill interfaces. Editing instructions also uses the local procedure/metadata rules in [testing](docs/development/testing.md); publishing or repairing consumers uses [deployment](docs/runbooks/deployment.md) and [rollback](docs/runbooks/rollback.md).

Each SKILL.md states its invocation trigger and completion criteria. Keep project commands in the caller's project guide; a public skill must work with explicit project-owned inputs rather than assuming a sibling checkout or home-directory installation. Relative supporting-resource links must remain inside this repository.

Use isolated worktrees, Conventional Commits and focused PRs. Preserve upstream invocation policies and public-safe metadata. Update the owning maintenance docs and verified troubleshooting in the same PR after behavior changes. Record consequential choices in [ADRs](docs/adr/README.md); optional incident/research records require real evidence.

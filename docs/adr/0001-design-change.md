# 0001: Use design-change for ADR and feature-design outputs

Status: proposed

## Context

The library already distributes self-contained skills and Atelier already has a design/review path. Reusing both makes the requested output contract explicit without adding another procedure or replacing the workflow.

## Options

| Option | Tradeoffs |
| --- | --- |
| Keep generic ADR instructions | No packaging or workflow changes. / Does not distribute the requested skill or guarantee concrete visual design outputs. |
| Publish design-change and update the existing Design path | Reuses root skill discovery and existing design review/approval routes. / Adds a Python/Graphviz report dependency and requires artifacts to be regenerated after findings. |
| Create a separate ADR-only skill and new workflow path | Allows a separate discovery trigger. / Duplicates decision rationale and visual-design conventions and expands routing unnecessarily. |


## Decision

Publish design-change and update the existing Design path

## Consequences

- The public library gains one portable root skill and a deliberately updated plugin version.
- The shared feature-design instructions require ADR output for significant decisions, and JSON/Markdown/offline HTML outputs for big features.
- Engineering blogs and published designs inform alternatives; baseline claims remain grounded in repository evidence and provider guarantees in official versioned docs.
- Graphviz is required for offline visual output; the documented Markdown-only fallback records missing HTML rather than claiming full completion.
- Atelier installs a recorded exact source revision and mirrors the complete folder through its existing skill synchronization.
- Pinned consumers still require their own source-pin update; publishing the library alone does not update every product.


## Evidence

| ID | Status | Source | Claim |
| --- | --- | --- | --- |
| E1 | observed | README.md and .claude-plugin/plugin.json at skills 7f045c0 | Six root skill directories are cataloged; plugin discovery uses the repository root and version 1.11.0. |
| E2 | observed | AGENTS.md; docs/technical/architecture.md; docs/runbooks/deployment.md | The library requires portable resources, isolated worktrees, focused reviewed PRs, and explicit consumer verification. |
| E3 | observed | Atelier workflows/default.json revision 28 | Design currently requires acceptance/contracts and an ADR for a big feature, without naming design-change or required generated outputs. |
| E4 | observed | Maintainer request on 2026-10-12 | Publish design-change to Nanostack and Atelier; explicitly require its ADR output and cite relevant technical blogs for new features, especially big ones. |


## Implementation and verification

The [design-change procedure](../../design-change/SKILL.md) owns the report input,
renderer and examples. [Agent workflow](../../agent-workflow/SKILL.md) invokes it
before feature implementation. The [builder contract tests](../../design-change/scripts/test_build.py)
ran with `python3 -B design-change/scripts/test_build.py`: 8 passed. Full and
Markdown-only fictional example builds also passed. These checks validate the
procedure and packaging; future feature acceptance scenarios remain specified.

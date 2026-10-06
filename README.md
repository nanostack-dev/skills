# skills

Public skill library. Two ways to use it:

- **Plugin marketplace** — add `https://github.com/nanostack-dev/skills` as a
  marketplace in Claude Code, then install the `nanostack-skills` plugin.
- **Raw GitHub URL** — for Nanostack cloud workers (routines, remote agents)
  that cannot access the local `~/.claude/skills/` filesystem or attach
  plugins.

## Usage

Point a cloud worker prompt at the raw `SKILL.md` URL, same pattern as the
third-party skills already used by the nightly craft routines
(`mattpocock/skills`, `emilkowalski/skills`):

```
https://raw.githubusercontent.com/nanostack-dev/skills/main/<skill-name>/SKILL.md
```

## Skills

- [`agent-workflow`](agent-workflow/SKILL.md) — implement features with affected-area
  E2E verified locally before pushing and CI as the complete final gate; cloud
  agents without local runtime access continue through CI with a top-of-PR warning
  and a concrete access request. Uses each project's own guides and commands.
- [`feature-review`](feature-review/SKILL.md) — complete browser feature review
  with mobile, tablet and desktop E2E checks, inspected screenshots, independent
  validation and readable PR videos, while keeping ordinary tests fast.
- [`real-world-examples`](real-world-examples/SKILL.md) — ground explanations,
  comparisons, and recommendations in concrete real-world examples.
- [`flow-suite-testing`](flow-suite-testing/SKILL.md) — API testing with workflow
  graphs: discover the engine's capabilities, design dependencies and reliable
  cleanup, reuse scoped variables, verify external effects and emitted events,
  and keep contract assertions aligned with the API.
- [`change-map`](change-map/SKILL.md) — turn a PR or in-progress branch into an
  picture-first review page: system diagram, decisions to approve, animated
  scenarios, lifecycle, ER schema, tests as Given/When/Then, and the noise split.
- [`postmortem`](postmortem/SKILL.md) — blameless postmortem for an incident:
  evidence-backed timeline, a branching Five Whys tree in Mermaid, an owned
  action per root cause, published as an animated HTML report plus a Markdown
  document.

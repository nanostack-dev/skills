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

- [`real-world-examples`](real-world-examples/SKILL.md) — ground explanations,
  comparisons, and recommendations in concrete real-world examples.
- [`flow-suite-testing`](flow-suite-testing/SKILL.md) — end-to-end API testing
  with echopoint flows: the authoring loop, designing a flow as a branching graph
  rather than a chain, reusing organization and flow variables instead of
  hardcoding, verifying side effects at the third party, and keeping assertions
  in step with a status change.
- [`change-map`](change-map/SKILL.md) — turn a PR or in-progress branch into an
  picture-first review page: system diagram, decisions to approve, animated
  scenarios, lifecycle, ER schema, tests as Given/When/Then, and the noise split.
- [`postmortem`](postmortem/SKILL.md) — blameless postmortem for an incident:
  evidence-backed timeline, a branching Five Whys tree in Mermaid, an owned
  action per root cause, published as an animated HTML report plus a Markdown
  document.

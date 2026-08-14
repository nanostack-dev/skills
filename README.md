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

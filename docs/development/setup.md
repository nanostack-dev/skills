# Standalone skill maintenance setup

Clone this repository and install Git and Python 3. Inspect each supporting script's imports/CLI before running it; Markdown/metadata edits do not need an application server or a sibling product checkout.

Read a skill's SKILL.md together with its referenced resources before editing its trigger, sequence or completion criterion. The [README](../../README.md) explains plugin and raw URL consumption. Consumer-specific configuration remains owned by that consumer.

Use [testing](testing.md) for metadata/resource checks and a disposable artifact when exercising a renderer.

Codex, OpenCode and Grok Build read the local `AGENTS.md`. Claude Code loads it through the repository-owned `.claude/settings.json` session-start hook. Review project/hook trust in the client and start a fresh session after changing this configuration; personal overrides remain in ignored `settings.local.json`.

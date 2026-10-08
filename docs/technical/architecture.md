# Skill library architecture

The six root skill directories contain SKILL.md entry points. [The catalog](../../README.md) names their current responsibilities. Each procedure discloses its supporting references, scripts, templates and viewers only when needed.

[Plugin metadata](../../.claude-plugin/plugin.json) discovers skills from the repository root; [marketplace metadata](../../.claude-plugin/marketplace.json) packages this repository as the Nanostack skills plugin. Raw GitHub consumers load the same instructions with relative supporting-resource URLs. Pinned consumers follow an explicit source commit; changing main does not update those pins automatically.

Projects own runtime setup, tests, domain terms and deployment authorization. Generic procedures consume those local guides and report missing prerequisites honestly. [Change-map](../../change-map/SKILL.md) and [postmortem](../../postmortem/SKILL.md) own their rendering scripts/templates; generated reports are consumer artifacts rather than library source.

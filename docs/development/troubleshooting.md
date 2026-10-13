# Skill troubleshooting

- A skill is undiscoverable: inspect the plugin/marketplace paths and the consumer's pinned source or local catalog rather than assuming a global installation.
- A cloud/raw consumer misses a helper: verify the resource path resolves relative to the fetched SKILL.md and the URL uses the same repository/ref.
- A consumer still uses old instructions: identify its pin/cache; update the declared pin through that consumer's review process. Updating this repository's main alone does not refresh it.
- A generated report fails: use the skill's supplied example/template, inspect the supporting script's arguments, and validate the output schema and rendered artifact.

- `design-change` cannot build HTML because `dot` is missing: its builder needs
  Graphviz for SVG layout. Use `--markdown-only` to deliver the ADR and Markdown,
  and explicitly report the missing visual output. The supplied tests exercise
  this fallback without Graphviz. Raw consumers must materialize the builder and
  sibling `assets/viewer.html` from the same repository/ref before running it.

Capture verified fixes without customer data, credentials or raw sensitive exchanges.

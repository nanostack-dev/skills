# Validate skill changes

For documentation changes, check affected local links, SKILL.md resource pointers and `git diff --check`. Parse tracked plugin/marketplace JSON and confirm their discovery paths correspond to the actual root skill catalog.

For supporting Python scripts, use `python3 -m py_compile <changed-script>`, inspect `--help`, then run a supplied example or disposable consumer fixture through the changed behavior and inspect the generated artifact. Compilation alone does not verify a report.

For procedure changes, exercise the changed branch against a concrete consumer problem, preserving the skill's invocation policy and evidence/completion criteria. Verify cloud/raw consumers can reach all disclosed resources. There is no tracked repository CI workflow that automatically proves every procedure; report exact manual validation and any unexercised behavior.

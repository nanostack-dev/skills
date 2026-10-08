# Publish skill revisions

This repository publishes procedures, not a service. Open a reviewed PR for source/resource changes and update plugin version metadata deliberately when the packaging requires a version change.

After merge, consumers following raw main URLs can see the new instructions immediately. Plugin consumers update through their client. Pinned consumers require an explicit reviewed commit-pin update and reinstall in their own repository/tool.

Verify the intended consumer can discover the skill, honors invocation policy and can fetch its supporting resources. Report the published commit, consumer method and concrete exercised behavior. Do not claim every product adopted a change merely because main advanced.

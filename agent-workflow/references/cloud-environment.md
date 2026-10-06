# Cloud environment exception

Use this branch when an agent cannot run the project's owned local integration
environment from its cloud executor. Establish the actual blocker using the
documented setup and available authorized access: for example, an inaccessible
Docker daemon, unavailable container execution, or missing approved development
identity-provider credentials. A cloud label, a product assertion failure or a
preference for CI is not evidence that local execution is unavailable.

## Continue with an explicit boundary

Run every feasible local check and implement the affected E2E tests with their
normal fixtures, assertions and setup dependencies. Record precisely which local
scenarios could not execute and why. Use existing authorized setup paths before
declaring the environment inaccessible.

Create or update the PR without waiting for the access request to be answered.
Put the warning below at the very top of its body, before the repository template,
and ask the user for the specific missing capability. This exception permits CI
iteration while the request remains unanswered; it does not permit mutation of
shared production/development deployments, disabling authentication, or exporting
credentials without authorization. Ask for secure provisioning, never secret
values in PR text or comments.

```markdown
> [!WARNING]
> **Affected-area local E2E could not be completed in this cloud environment.**
> Blocker: <documented command and safe observed error or missing capability>.
> Local E2E not executed: <affected scenarios and setup dependencies>.
> Please provide <specific Docker/container access, approved development credentials,
> or access to a suitable executor> so I can run the complete local test environment.
> Local checks completed: <actual commands and results>.
> Verification is continuing through CI: <current-head run links and results>.

<existing PR template, evidence and automation markers>
```

Adapt the warning to partial coverage when some scenarios ran. The request is for
access to the full local environment; once restored, the normal local gate remains
affected-area E2E rather than an unconditional full-suite run.

## Use CI as the fallback feedback loop

Push the proposed implementation and tests, then inspect the actual CI reports
and safe logs on that head. Confirm that the affected scenarios are included in
the project's complete required gate. If dedicated affected-area CI feedback is
already available, use it for diagnosis while retaining the final complete gate.

For product failures, fix from concrete evidence and rerun all feasible local
checks before pushing again. For platform-specific failures, reproduce in a
matching local container when accessible; otherwise diagnose through CI. Every
push or rerun should follow a relevant change, new evidence or a confirmed transient
recovery. When the same blocker repeats without new evidence, update the PR's
access request and continue independent work instead of rerunning it blindly.

Keep the normal coverage and assertion requirements. Skipping tests, weakening
assertions or increasing retries to obtain a green result does not satisfy this
exception. If CI also lacks the required access, state the remaining blocker in
the PR; unexecuted tests cannot be reported as passed or fully verified.

Update the top warning as the head and results change, keeping local results
separate from CI results. A green complete CI gate can support review readiness
with the local limitation disclosed. Required responsive or independent review
that remains unavailable is still an explicit outstanding requirement.

After access is provided, execute the affected local selection against the current
source, verify owned cleanup, and replace the warning with the actual local evidence.

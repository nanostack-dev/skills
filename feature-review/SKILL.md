---
name: feature-review
description: Complete a browser-visible feature or behavior change with mobile, tablet and desktop E2E tests, reviewed screenshots, independent agent validation and readable PR videos.
---

# Feature review

Use this before calling a browser-visible feature or behavior change complete.
The implementing agent owns repairs and PR evidence; a separate agent validates
the final result. Keep reusable procedure here and project commands, fixtures,
coverage rules and verified troubleshooting in the project's own test guide.

## Bind the workflow to the project

Read the repository's agent guide, browser-test guide, package scripts, test
configuration and owning scenarios. Identify the app directory, package manager,
managed runtime, device projects, fixtures, screenshot/checkpoint helpers,
regression gate, ignored media directory and supported PR uploader. Use the
project's actual commands and conventions; document missing bindings locally.

Prefer the existing E2E setup. For Playwright, read the selected projects and
their dependencies before adding a focused review configuration. An unavailable
runtime, missing profile or failed product behavior is an outstanding requirement,
with its command and evidence, until it is resolved.

For changes with no browser-visible behavior, complete review with a documented
PR boundary, passing service/contract/tooling checks and the repository's code
review requirements. The browser and media steps below apply to browser-visible
changes. A backend change that affects a UI journey still needs that journey
reviewed on all three profiles.

## Implement and validate

1. List every changed user action, relevant loading/error/empty state and
   persistence boundary. Extend the owning scenarios with real UI outcomes,
   isolated fixture data, accessible locators and assertion-based waits. Update
   route coverage and change-impact selection when the project maintains them.
   Add a regression for each reproduced defect; record its verified repair in
   the relevant test-guide troubleshooting file.
2. Use the narrow ordinary suite while implementing. For final responsive
   review, run every changed browser behavior on mobile, tablet and desktop.
   Confirm scenario discovery first, then execute the identical selection with
   setup dependencies enabled. Account for every expected scenario on every
   profile. Zero matches, skips, retries or failures leave validation incomplete.
3. Record each profile at its configured viewport. Guest or additional browser
   contexts must inherit that profile's emulation and recording settings.
   Authentication/bootstrap prerequisites do not establish device coverage of
   the feature. Changes to first-run initialization itself need a fresh-runtime
   journey on each profile. Name emulated devices, browser engines and physical
   hardware accurately in the results.
4. Capture meaningful screenshots immediately after assertions: validation
   feedback, a dialog, a saved/reloaded result or a changed layout. Inspect each
   profile for clipping/overflow, readable text, reachable controls, navigation,
   focus and touch interactions. For rendered UI changes, capture before/after
   pairs from the PR base and feature source with identical data, viewport and
   theme, using the repository's screenshot tool. Fix findings and rerun affected
   scenarios; generating screenshots alone is not a visual verdict.
5. Finish the project's ordinary regression gate and applicable UI, component,
   type, build and service checks. Responsive evidence supplements that gate.
   Preserve its coverage and the normal CI failure diagnostics.

## Keep review fast and maintainable

Focus the three-profile recording run on changed journeys and affected shared
behavior. Share expensive backend startup and bootstrap when isolation permits;
keep test data isolated and respect the runtime's ownership checks. Assign agents
separate domains, with one coordinator owning shared startup/configuration.

Keep action pacing, deliberate checkpoint holds and always-on video in a review
mode. Ordinary correctness waits remain assertions, and ordinary CI retains its
existing speed and capture policy. Measure recording time separately from normal
test performance. Resolve flakes instead of weakening assertions or excluding
scenarios. Keep reusable fixtures and small checkpoint helpers in the test suite;
evolve the project guide when a verified solution changes a convention.

## Delegate independent validation

After browser checks pass and the implementing agent has inspected its captures,
dispatch a validation agent with the worktree, final commit/diff, changed behaviors, exact
scenario selection and report/media paths. Ask it to read the changes for missing
behavior or weak assertions, rerun the affected scenarios on all three profiles,
inspect screenshots and videos, and return evidence with a ready/not-ready verdict.

The validator reports findings to the implementing agent rather than editing the
same files concurrently. Resolve findings against the final source. After a UI
repair, refresh the affected tests, captures and independent review. Shut down
owned test services and verify cleanup when validation finishes.

## Publish readable evidence

Inspect each relevant video at normal playback speed. Add review-only pacing or
checkpoint holds when important actions, text or feedback pass too quickly. Trim
unrelated setup when useful, retaining the action, feedback and outcome at native
speed. State how playback was inspected, including any sampling limitation.

Playwright finalizes videos after contexts close. Its video configuration should
use the selected viewport, rather than the default downscaled recording size.
Keep action captions disabled when entered values could appear in them, including
passwords. Use named states and checkpoints to explain the clip. Use disposable
fixture data and inspect media for secrets before uploading.

Label each profile's screenshots and videos in the PR description, alongside the
tested commit, scenario selection, results, visual verdict, independent verdict
and remaining coverage boundaries. Keep the repository's template sections and
automation markers. Upload media with the supported GitHub mechanism; inspect
`gh pr create --help` or `gh pr edit --help` for attachment support. Convert WebM
to a supported format such as MP4 with `ffmpeg` when necessary, preserving speed.

Verify the saved description and that GitHub loads the images and video players.
If upload partly fails, inspect the existing PR and retry only missing files.
Local paths, artifact-download links and promised recordings do not satisfy the
attached-video requirement. Keep media in ignored scratch, outside commits.

Browser review is complete when every changed behavior passes on the three
profiles, inspected screenshots and readable videos have no unresolved findings,
the independent validator is ready, the regression gate passes and the PR holds
working review evidence. This skill does not itself authorize merging or deploying.

Primary references: [Playwright projects](https://playwright.dev/docs/test-projects),
[emulation](https://playwright.dev/docs/emulation),
[videos](https://playwright.dev/docs/videos) and
[test best practices](https://playwright.dev/docs/best-practices).

---
name: postmortem
description: Write a blameless postmortem for an incident, outage, failed deploy, data loss or near miss. It finds the root causes with a branching Five Whys tree drawn in Mermaid, and ships an animated HTML report (timeline replay, whys tree growing level by level) plus a Markdown document to commit. Use when asked for a postmortem, incident review, post-incident report, RCA or Five Whys, or when an incident is resolved and needs a write-up.
---

# Postmortem

A postmortem turns an incident into changes that stop the next one. It is **blameless**: every answer names a system, a process or a missing guard. Where a person's action shows up, the next why asks what made that action possible or likely.

The format joins Google SRE's (summary, impact, root causes, trigger, detection, resolution, lessons with *where we got lucky*) and PagerDuty's (contributing factors, responders, internal and customer messages, owned action items), with a Five Whys tree at the centre.

ultrathink: the whys are where a postmortem is won or lost. The first answer to each why is usually a symptom. Think each branch through to a cause the team can change before writing it down.

## Files

You write one file, `postmortem.json`. `scripts/build.py` checks it and writes the other two:

| File | Written by | Holds |
|---|---|---|
| `postmortem.json` | you | facts, timeline, the whys tree, actions (shape: `template.json`) |
| `postmortem.md` | `build.py` | the document to commit or paste: tables, the whys as a nested list, the Mermaid diagram |
| `postmortem.html` | `build.py` | the report to publish as an artifact, drawn by the fixed `viewer.html` |

The viewer draws the clock (duration, time to detect, time to mitigate), an animated SVG **timeline replay** (a playhead sweeps the incident while the phases grow and each event pops in), the **whys tree** in Mermaid, revealed one level at a time, root causes beside the actions that fix them, lessons, the action table, and copy buttons for the messages and the whole Markdown. Never write the HTML or the Markdown by hand, and never edit the viewer for one incident.

On a cloud worker, fetch the files first:

```
base=https://raw.githubusercontent.com/nanostack-dev/skills/main/postmortem
for f in scripts/build.py viewer.html template.json examples/echopoint-migration-timeout/postmortem.json; do curl -fsSL --create-dirs -o "$f" "$base/$f"; done
```

## Steps

### 1. Build the timeline from evidence

Collect what happened from primary sources: the incident channel, alerts, deploy and CI runs (`gh run view`, job start and end times), logs, metrics, commits and PRs, and the people who responded. Write every time in UTC with its source as `link`.

Mark the events the report measures from, using `kind`:

| kind | Meaning |
|---|---|
| `change` | a deploy, merge or config change that came before |
| `trigger` | impact starts. T+0 for the whole report |
| `detect` | the team first knows. Time to detect ends here |
| `escalate`, `comms`, `note` | people pulled in, updates sent, anything else worth a line |
| `mitigate` | the impact stops growing. The first one ends time to mitigate |
| `resolve` | the impact is over |
| `followup` | the permanent fix, after resolution |

Done when every event has a time and a source, there is one `trigger`, one `detect` and one `resolve`, and every time you reconstructed rather than read is marked `"approx": true`.

### 2. Ask the Five Whys

The Five Whys is a [root cause identification technique](https://www.atlassian.com/team-playbook/plays/5-whys):

- Begin with a description of the impact and ask why it occurred. That impact is `whys.problem`: what a customer or the business saw, not the internal error.
- Note the impact that it had.
- Ask why this happened, and why it had the resulting impact. These are two lenses on every incident. The default `cause` lens asks why it happened. The `impact` lens (`"lens": "impact"`, drawn dashed and labelled *why so bad?*) asks why the damage was as large as it was: late detection, a wide blast radius, a slow or manual recovery. Give every postmortem at least one impact branch.
- Then continue asking why until you arrive at a root cause.

List the whys in the postmortem. `build.py` writes them twice: as a Mermaid flowchart and as a nested list, both in the Markdown and in the report.

Five is a reference, not a count. A branch ends at its root cause, often after three to seven whys. `build.py` warns under three, where a "root cause" is usually a symptom, and over eight, where the chain has usually drifted off the incident.

**Branch.** When an answer has more than one cause, give each cause its own child and follow each to its own root. A real incident is a tree; a single chain usually hides a second cause. The worked example has three branches from the problem and one split two levels down.

**Each why is a fact.** Put the log line, graph, run or commit that shows it in `evidence`. A why you believe but have not confirmed gets `"open": true` and stays open until it is checked. A `final` postmortem has no open branch.

**A root cause** (`"root": true`, `id` `R1`, `R2`…) is a condition the team can change that removes the whole class of failure, not this instance: a budget nobody set, a check that does not exist, an assumption a design makes. "Migration 45 was slow" is an instance; "data rewrites ran inside a time budget meant for app wiring" is a class. When the answer is a person's action, ask why again: why the system let that action through, or made it likely.

Done when every leaf is a root cause or explicitly open, and each root cause names something a team can change.

### 3. Turn every root cause into an action

Every root cause gets at least one action, and every action has an owner and a due date (or `status: done`). `fixes` lists the root causes it removes.

- `prevent` removes the cause. Prefer it.
- `detect` catches the next one sooner. Include one, or say in `detection` why detection was already good enough.
- `mitigate` makes the next one smaller or faster to recover from.
- `process` changes how people work. It decays fastest, so pair it with a prevent or detect action where one exists.

Done when `build.py` reports no root cause without an action.

### 4. Write the lessons

`lessons.well`, `lessons.wrong` and `lessons.lucky`. *Where we got lucky* is the most valuable of the three: each lucky break is a failure that did not happen this time and will next time. When a lucky item points at a real risk, it usually deserves an action of its own.

### 5. Write postmortem.json

Read `template.json`: it shows every key in its exact shape. `examples/echopoint-migration-timeout/postmortem.json` is the quality bar: a real failed deploy with four root causes, two of them on the impact lens.

Write short. An event `label` stays under 64 characters (detail goes in `detail`), a why under 140 so the diagram stays legible, and the summary is four to six sentences. Inline `code`, **bold** and [links](https://example.com) render everywhere. Use the team's own severity scale and roles; names appear only under `responders`, never inside a why. `short` is the page title, two to four words.

### 6. Build

```
python3 scripts/build.py postmortem.json -o postmortem.html --md postmortem.md
```

It prints every problem (a missing trigger, events out of order, a branch with no root, a root with no action, an action with no owner, a why that blames a person, a chain too short or too long) and a one-line summary. Fix and rerun until there is no warning. Add `--standalone` to open the page from disk.

### 7. Deliver

Publish `postmortem.html` with the Artifact tool, with a one-sentence description of the incident. Commit `postmortem.md` where the team keeps postmortems (a `postmortems/` folder in the affected repo, named `YYYY-MM-DD-<slug>.md`), or hand it to the user when there is none. In chat, give the link, the root causes in one line each, and the open actions with their owners.

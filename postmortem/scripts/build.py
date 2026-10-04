#!/usr/bin/env python3
"""Validate a postmortem and render it twice: a Markdown document and an HTML report.

    build.py postmortem.json -o postmortem.html --md postmortem.md
    build.py postmortem.json -o postmortem.html --standalone   # adds a doctype, to open the file locally
    build.py postmortem.json --check                          # validate only

postmortem.json is what the agent writes (see template.json). The script
derives everything else: the time to detect, mitigate and resolve, the
mermaid source of the whys tree, the depth of every why (the report animates
the tree level by level), and the Markdown document. The report embeds the
Markdown so a reader can copy it.

The viewer is found next to this script (../viewer.html). Pass --viewer with a
path or URL when the script runs alone, for example on a cloud worker.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

VIEWER_URL = "https://raw.githubusercontent.com/nanostack-dev/skills/main/postmortem/viewer.html"
KINDS = {"change", "trigger", "detect", "escalate", "comms", "note", "mitigate", "resolve", "followup"}
ACTION_TYPES = {"prevent", "detect", "mitigate", "process"}
ACTION_STATUS = {"open", "in progress", "done"}
BLAME = re.compile(r"\b(human error|forgot|careless|negligen\w*|should have|did(?:n't| not) (?:check|notice|test|think))\b", re.I)
ROOT_ID = re.compile(r"^R\d+$")
CLASSDEFS = [
    "classDef problem fill:#fdecea,stroke:#c2362f,stroke-width:2px,color:#4a1210",
    "classDef root fill:#e7f5ec,stroke:#1f7a45,stroke-width:2px,color:#0f3a20,font-weight:bold",
    "classDef open fill:#fff4d9,stroke:#9a6200,stroke-dasharray:5 4,color:#3f2a00",
]


def read_viewer(where):
    if where.startswith("http"):
        with urllib.request.urlopen(where) as resp:
            return resp.read().decode()
    with open(where) as fh:
        return fh.read()


def parse_time(raw):
    t = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("no timezone")
    return t.astimezone(timezone.utc)


def dur(seconds):
    s = int(round(abs(seconds)))
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60:02d}s"
    if s < 86400:
        return f"{s // 3600}h {s % 3600 // 60:02d}m"
    return f"{s // 86400}d {s % 86400 // 3600:02d}h"


def rel(seconds):
    return ("T+" if seconds >= 0 else "T−") + dur(seconds)


def clock(event):
    t = parse_time(event["t"])
    return ("~" + t.strftime("%H:%M")) if event.get("approx") else t.strftime("%H:%M:%S")


# ---------------------------------------------------------------- timeline

def timeline_metrics(data, problems):
    events = (data.get("timeline") or {}).get("events") or []
    if not events:
        problems.append("timeline.events is empty")
        return {}
    for i, e in enumerate(events):
        where = f"timeline.events[{i}]"
        try:
            e["_ms"] = int(parse_time(e["t"]).timestamp() * 1000)
        except (KeyError, ValueError) as err:
            problems.append(f"{where}: `t` must be ISO 8601 with a timezone ({err})")
            e["_ms"] = 0
        if e.get("kind") not in KINDS:
            problems.append(f"{where}: kind {e.get('kind')!r} is not one of {sorted(KINDS)}")
        if len(e.get("label", "")) > 64:
            problems.append(f"{where}: label is {len(e['label'])} chars; keep it under 64 and move the rest to `detail`")
    if [e["_ms"] for e in events] != sorted(e["_ms"] for e in events):
        problems.append("timeline.events are not in time order (sorted for you, fix the file)")
        events.sort(key=lambda e: e["_ms"])

    first = {}
    for e in events:
        first.setdefault(e.get("kind"), e["_ms"])
    for kind in ("trigger", "detect", "resolve"):
        if kind not in first:
            problems.append(f"timeline has no `{kind}` event; the report measures from it")
    order = [k for k in ("trigger", "detect", "mitigate", "resolve") if k in first]
    for a, b in zip(order, order[1:]):
        if first[a] > first[b]:
            problems.append(f"the first `{a}` event comes after the first `{b}` event")
    if "trigger" not in first:
        return {}
    t0 = first["trigger"]
    for e in events:
        e["_rel"] = (e["_ms"] - t0) / 1000
    m = {"t0": t0}
    for kind, key in (("detect", "ttd"), ("mitigate", "ttm"), ("resolve", "ttr")):
        if kind in first:
            m[key] = (first[kind] - t0) / 1000
            m[f"{kind}_ms"] = first[kind]
    return m


# ---------------------------------------------------------------- whys

def walk_whys(whys, problems):
    """Number every why, check every chain, return (nodes, edges, depth, roots)."""
    nodes, edges, depth, roots = [], [], {"P": 0}, {}
    counter = [0]

    def visit(children, parent, level, path):
        if not children:
            return
        for child in children:
            if child.get("root"):
                nid = child.get("id", "")
                if not ROOT_ID.match(nid):
                    problems.append(f"root cause {child.get('text', '')[:40]!r} needs an id like R1")
                if nid in roots:
                    problems.append(f"root id {nid} is used twice")
                roots[nid] = child
            else:
                counter[0] += 1
                nid = f"W{counter[0]}"
            child["_id"] = nid
            depth[nid] = level
            text = child.get("text", "")
            if not text:
                problems.append(f"{nid}: why has no text")
            if len(text) > 140:
                problems.append(f"{nid}: {len(text)} chars is too long for the diagram; keep a why under 140 and put the rest in `evidence`")
            if BLAME.search(text):
                problems.append(f"{nid}: {BLAME.search(text).group(0)!r} points at a person; ask why the system let it happen")
            nodes.append(child)
            edges.append((parent, nid, child.get("lens", "cause")))
            if child.get("lens", "cause") not in ("cause", "impact"):
                problems.append(f"{nid}: lens must be cause or impact")
            kids = child.get("because") or []
            if child.get("root") and kids:
                problems.append(f"{nid}: a root cause ends its branch; move its children or drop `root`")
            if not kids:
                if not child.get("root") and not child.get("open"):
                    problems.append(f"{nid}: branch ends without a root cause; ask why again, or mark it `open` while still digging")
                if child.get("root") and level < 3:
                    problems.append(f"{nid}: root cause after only {level} whys; a cause this shallow is usually a symptom, ask why again")
                if level > 8:
                    problems.append(f"{nid}: {level} whys deep; the chain probably drifted off the incident, go back up")
            visit(kids, nid, level + 1, path + [nid])

    visit(whys.get("because") or [], "P", 1, ["P"])
    if not whys.get("problem"):
        problems.append("whys.problem is empty; start from the impact a customer saw")
    if not roots:
        problems.append("the whys tree has no root cause")
    if not any(n.get("lens") == "impact" for n in nodes):
        problems.append("no `impact` branch: also ask why the impact was as large as it was (detection, blast radius, recovery)")
    return nodes, edges, depth, roots


def mermaid_label(text):
    return text.replace('"', "#quot;").replace("\n", " ")


def mermaid(whys, nodes, edges, colors):
    out = ["flowchart TD", f'  P["{mermaid_label(whys.get("problem", ""))}"]']
    for n in nodes:
        text = n.get("text", "")
        if n.get("root"):
            text = f"{n['_id']} · {text}"
        out.append(f'  {n["_id"]}["{mermaid_label(text)}"]')
    for src, dst, lens in edges:
        out.append(f"  {src} -->|why?| {dst}" if lens == "cause" else f"  {src} -.->|why so bad?| {dst}")
    out.append("  class P problem")
    rid = [n["_id"] for n in nodes if n.get("root")]
    oid = [n["_id"] for n in nodes if n.get("open")]
    if rid:
        out.append(f"  class {','.join(rid)} root")
    if oid:
        out.append(f"  class {','.join(oid)} open")
    # The report colours nodes from its theme tokens; mermaid writes classDef colours inline with
    # !important, which no stylesheet can override, so the HTML copy keeps only the stroke widths.
    out += ["  " + c for c in CLASSDEFS] if colors else [
        "  classDef problem stroke-width:2px", "  classDef root stroke-width:2px", "  classDef open stroke-dasharray:5 4"]
    return "\n".join(out)


# ---------------------------------------------------------------- actions

def check_actions(data, roots, problems):
    actions = data.get("actions") or []
    ids = set()
    fixed = set()
    for i, a in enumerate(actions):
        where = f"actions[{i}] ({a.get('id', '?')})"
        if a.get("id") in ids:
            problems.append(f"{where}: duplicate id")
        ids.add(a.get("id"))
        if not a.get("what"):
            problems.append(f"{where}: no `what`")
        if a.get("type") not in ACTION_TYPES:
            problems.append(f"{where}: type must be one of {sorted(ACTION_TYPES)}")
        status = a.get("status", "open")
        if status not in ACTION_STATUS:
            problems.append(f"{where}: status must be one of {sorted(ACTION_STATUS)}")
        if not a.get("owner"):
            problems.append(f"{where}: no owner; an action nobody owns does not happen")
        if status != "done" and not a.get("due"):
            problems.append(f"{where}: open action with no due date")
        for r in a.get("fixes") or []:
            if r not in roots:
                problems.append(f"{where}: fixes {r}, which is not a root cause id")
            fixed.add(r)
    for r in roots:
        if r not in fixed:
            problems.append(f"root cause {r} has no action that fixes it")
    if not any(a.get("type") == "detect" for a in actions):
        problems.append("no `detect` action; say how the next one gets caught sooner, or why detection was already good enough")


# ---------------------------------------------------------------- markdown

def md_whys(whys, nodes_by_parent, actions_by_root):
    lines = [f"- **Problem:** {whys.get('problem', '')}"]

    def visit(parent, indent):
        for n in nodes_by_parent.get(parent, []):
            q = "Why?" if n.get("lens", "cause") == "cause" else "Why so bad?"
            line = f"{'  ' * indent}- **{q}** {n.get('text', '')}"
            if n.get("evidence"):
                line += f" _Evidence: {n['evidence']}_"
            if n.get("root"):
                fix = ", ".join(actions_by_root.get(n["_id"], [])) or "none"
                line += f" → **Root cause {n['_id']}** (fixed by {fix})"
            if n.get("open"):
                line += " → _open, still investigating_"
            lines.append(line)
            visit(n["_id"], indent + 1)

    visit("P", 1)
    return lines


def cell(v):
    return str(v or "").replace("|", "\\|").replace("\n", " ")


def markdown(data, m, nodes, edges):
    L = []
    meta = [("Date", data.get("date")), ("Severity", data.get("severity")), ("Status", (data.get("status") or "").capitalize()),
            ("Service", data.get("service")), ("Authors", ", ".join(data.get("authors") or []))]
    events = (data.get("timeline") or {}).get("events") or []
    approx = lambda kind: "~" if next((e for e in events if e.get("kind") == kind), {}).get("approx") else ""
    if "ttr" in m:
        meta.append(("Duration", f"{approx('resolve')}{dur(m['ttr'])} (trigger to resolution)"))
    if "ttd" in m:
        meta.append(("Time to detect", approx("detect") + dur(m["ttd"])))
    if "ttm" in m:
        meta.append(("Time to mitigate", approx("mitigate") + dur(m["ttm"])))
    L += [f"# {data.get('title', 'Postmortem')}", "", "| | |", "|---|---|"]
    L += [f"| **{k}** | {cell(v)} |" for k, v in meta if v]
    L += ["", "> Blameless: this document names systems, processes and missing guards, not people.", ""]
    L += ["## Summary", "", data.get("summary", ""), ""]
    impact = data.get("impact") or {}
    L += ["## Impact", "", impact.get("text", "")]
    if impact.get("numbers"):
        L.append("")
        L += [f"- **{n['value']}** {n['label']}" for n in impact["numbers"]]
    L.append("")
    for key, title in (("trigger", "Trigger"), ("detection", "Detection"), ("resolution", "Resolution")):
        if data.get(key):
            L += [f"## {title}", "", data[key], ""]

    L += ["## Timeline (UTC)", "", "| Time | | Event |", "|---|---|---|"]
    for e in events:
        rel_s = rel(e["_rel"]) if "_rel" in e else ""
        text = f"**{cell(e.get('label'))}**"
        if e.get("detail"):
            text += f" {cell(e['detail'])}"
        if e.get("link"):
            text += f" ([link]({e['link']}))"
        L.append(f"| {clock(e)} | {rel_s} | {text} |")
    L.append("")

    whys = data.get("whys") or {}
    by_parent = {}
    for src, dst, _ in edges:
        by_parent.setdefault(src, []).append(next(n for n in nodes if n["_id"] == dst))
    actions_by_root = {}
    for a in data.get("actions") or []:
        for r in a.get("fixes") or []:
            actions_by_root.setdefault(r, []).append(a.get("id", "?"))
    L += ["## Root cause analysis: the five whys", "",
          "Start at the impact and ask why until the answer is something the team can change. "
          "Solid edges ask why it happened; dashed edges ask why the impact was as large as it was.", ""]
    L += ["```mermaid", data["_mermaid"], "```", ""]
    L += md_whys(whys, by_parent, actions_by_root)
    L.append("")

    roots = [n for n in nodes if n.get("root")]
    if roots:
        L += ["## Root causes", ""]
        L += [f"- **{n['_id']}** {n.get('text', '')}" for n in roots]
        L.append("")
    if data.get("contributing"):
        L += ["## Contributing factors", ""] + [f"- {c}" for c in data["contributing"]] + [""]

    lessons = data.get("lessons") or {}
    L += ["## Lessons learned", ""]
    for key, title in (("well", "What went well"), ("wrong", "What went wrong"), ("lucky", "Where we got lucky")):
        L += [f"### {title}", ""] + [f"- {x}" for x in lessons.get(key) or ["_Nothing recorded._"]] + [""]

    L += ["## Action items", "", "| ID | Action | Type | Owner | Due | Status | Ticket | Fixes |", "|---|---|---|---|---|---|---|---|"]
    for a in data.get("actions") or []:
        t = a.get("ticket") or {}
        ticket = f"[{t.get('label', 'link')}]({t['url']})" if t.get("url") else cell(t.get("label"))
        L.append(f"| {cell(a.get('id'))} | {cell(a.get('what'))} | {cell(a.get('type'))} | {cell(a.get('owner'))} | "
                 f"{cell(a.get('due'))} | {cell(a.get('status', 'open'))} | {ticket} | {cell(', '.join(a.get('fixes') or []))} |")
    L.append("")

    if data.get("responders"):
        L += ["## Responders", ""] + [f"- **{r.get('role')}**: {r.get('name')}" for r in data["responders"]] + [""]
    msg = data.get("messaging") or {}
    if msg.get("internal") or msg.get("external"):
        L += ["## Messaging", ""]
        if msg.get("internal"):
            L += ["### Internal", "", msg["internal"], ""]
        if msg.get("external"):
            L += ["### Customers", "", msg["external"], ""]
    if data.get("links"):
        L += ["## Supporting information", ""] + [f"- [{x['label']}]({x['url']})" for x in data["links"]] + [""]
    return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------- main

def check(data):
    problems = []
    for key in ("title", "date", "severity", "status", "summary"):
        if not data.get(key):
            problems.append(f"`{key}` is empty")
    if not (data.get("impact") or {}).get("text"):
        problems.append("impact.text is empty")
    if not (data.get("lessons") or {}).get("lucky"):
        problems.append("lessons.lucky is empty; what you got lucky on is the next incident")
    m = timeline_metrics(data, problems)
    whys = data.get("whys") or {}
    nodes, edges, depth, roots = walk_whys(whys, problems)
    if data.get("status") == "final" and any(n.get("open") for n in nodes):
        problems.append("status is final but a why branch is still open")
    check_actions(data, roots, problems)
    data["_m"] = m
    data["_depth"] = depth
    data["_mermaid"] = mermaid(whys, nodes, edges, colors=True)
    data["_mermaid_html"] = mermaid(whys, nodes, edges, colors=False)
    return problems, nodes, edges


def summary(data, nodes):
    m = data["_m"]
    roots = sum(1 for n in nodes if n.get("root"))
    deep = max((v for v in data["_depth"].values()), default=0)
    parts = [data.get("severity", "?"), data.get("status", "?")]
    if "ttr" in m:
        parts.append(f"resolved {rel(m['ttr'])}")
    parts += [f"{len(nodes)} whys, {roots} root causes, deepest {deep}", f"{len(data.get('actions') or [])} actions"]
    return " · ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("-o", "--out", default="postmortem.html")
    ap.add_argument("--md", default=None, help="also write the Markdown document here")
    ap.add_argument("--viewer", default=None)
    ap.add_argument("--standalone", action="store_true")
    ap.add_argument("--check", action="store_true", help="validate and print the summary, write nothing")
    args = ap.parse_args()

    with open(args.data) as fh:
        data = json.load(fh)
    problems, nodes, edges = check(data)
    for p in problems:
        print(f"warn: {p}", file=sys.stderr)
    print(summary(data, nodes), file=sys.stderr)
    if args.check:
        sys.exit(1 if problems else 0)

    md = markdown(data, data["_m"], nodes, edges)
    data["_markdown"] = md
    if args.md:
        with open(args.md, "w") as fh:
            fh.write(md)
        print(f"wrote {args.md}", file=sys.stderr)

    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer.html")
    viewer = read_viewer(args.viewer or (local if os.path.exists(local) else VIEWER_URL))
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    page = viewer.replace("/*POSTMORTEM_DATA*/null", payload, 1)
    title = data.get("short") or "Postmortem"
    page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", page, count=1)
    if args.standalone:
        page = f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n{page}\n</body></html>\n'

    with open(args.out, "w") as fh:
        fh.write(page)
    print(f"wrote {args.out} ({len(page) // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()

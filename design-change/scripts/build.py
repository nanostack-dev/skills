#!/usr/bin/env python3
"""Build a portable design report from two factual/proposed snapshots.

Python standard library; Graphviz dot is needed only for SVG diagrams.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
STATUSES = {"proposed", "accepted", "rejected", "superseded"}
EVIDENCE = {"observed", "assumption", "unknown", "illustrative"}
KINDS = {"actor", "system", "service", "store", "entity", "external"}
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def obj(value, path, required=(), optional=()):
    require(isinstance(value, dict), f"{path}: expected an object")
    require(not (set(required) - value.keys()), f"{path}: missing {set(required) - value.keys()}")
    require(not (value.keys() - set(required) - set(optional)),
            f"{path}: unknown keys {value.keys() - set(required) - set(optional)}")


def string(value, path):
    require(isinstance(value, str) and bool(value.strip()), f"{path}: expected nonempty text")


def strings(value, path):
    require(isinstance(value, list), f"{path}: expected a list")
    for i, v in enumerate(value):
        string(v, f"{path}[{i}]")


def enum(value, values, path):
    require(isinstance(value, str) and value in values, f"{path}: expected one of {sorted(values)}")


def records(value, path, required, optional=()):
    require(isinstance(value, list), f"{path}: expected a list")
    for i, v in enumerate(value):
        obj(v, f"{path}[{i}]", required, optional)
    return value


def ids(items, path):
    result = set()
    for v in items:
        ident = v["id"]
        require(isinstance(ident, str) and ID.fullmatch(ident), f"{path}: invalid ID {ident!r}")
        require(ident not in result, f"{path}: duplicate ID {ident}")
        result.add(ident)
    return result


def refs(values, known, path):
    strings(values, path)
    require(set(values) <= known, f"{path}: unresolved references {set(values) - known}")


def validate(d):
    obj(d, "design", ("schema_version", "title", "status", "baseline", "summary", "problem",
        "goals", "non_goals", "evidence", "invariants", "decisions", "views", "flows",
        "pseudocode", "acceptance", "rollout", "risks", "questions", "omitted_views"))
    require(type(d["schema_version"]) is int and d["schema_version"] == 1, "schema_version must be 1")
    for k in ("title", "summary", "problem"):
        string(d[k], k)
    enum(d["status"], STATUSES, "status")
    obj(d["baseline"], "baseline", ("label", "revision"))
    for k in d["baseline"]:
        string(d["baseline"][k], f"baseline.{k}")
    strings(d["goals"], "goals")
    strings(d["non_goals"], "non_goals")
    require(d["goals"], "at least one goal is required")
    ev = records(d["evidence"], "evidence", ("id", "status", "source", "claim"))
    ev_ids = ids(ev, "evidence")
    for e in ev:
        enum(e["status"], EVIDENCE, f"{e['id']}.status")
        string(e["claim"], f"{e['id']}.claim")
        require(isinstance(e["source"], str), f"{e['id']}.source: expected text")
        if e["status"] == "observed":
            string(e["source"], f"{e['id']}.source")
    inv = records(d["invariants"], "invariants", ("id", "text", "evidence"))
    inv_ids = ids(inv, "invariants")
    for item in inv:
        string(item["text"], f"{item['id']}.text")
        refs(item["evidence"], ev_ids, f"{item['id']}.evidence")
    acc = records(d["acceptance"], "acceptance", ("id", "title", "given", "when", "then", "status", "invariants"))
    acc_ids = ids(acc, "acceptance")
    for a in acc:
        for k in ("title", "given", "when"):
            string(a[k], f"{a['id']}.{k}")
        strings(a["then"], f"{a['id']}.then")
        require(a["then"], f"{a['id']}: at least one observable outcome required")
        enum(a["status"], {"specified", "passed", "failed", "not-run"}, f"{a['id']}.status")
        refs(a["invariants"], inv_ids, f"{a['id']}.invariants")
    decisions = records(d["decisions"], "decisions", ("id", "title", "status", "context", "options",
        "choice", "consequences", "evidence"), ("supersedes",))
    ids(decisions, "decisions")
    for dec in decisions:
        for k in ("title", "context", "choice"):
            string(dec[k], f"{dec['id']}.{k}")
        enum(dec["status"], STATUSES, f"{dec['id']}.status")
        opts = records(dec["options"], "options", ("name", "tradeoffs"))
        require(len(opts) >= 2, f"{dec['id']}: compare at least two options, including the status quo when credible")
        for opt in opts:
            string(opt["name"], "option.name")
            strings(opt["tradeoffs"], "option.tradeoffs")
        require(len({o['name'] for o in opts}) == len(opts), f"{dec['id']}: duplicate option names")
        require(dec["choice"] in {o['name'] for o in opts}, f"{dec['id']}: choice is not an option")
        strings(dec["consequences"], "consequences")
        refs(dec["evidence"], ev_ids, f"{dec['id']}.evidence")
        if "supersedes" in dec:
            string(dec["supersedes"], "supersedes")
    views = records(d["views"], "views", ("id", "title", "kind", "note", "evidence", "before", "after"))
    ids(views, "views")
    for view in views:
        enum(view["kind"], {"context", "services", "entities"}, f"{view['id']}.kind")
        for k in ("title", "note"):
            string(view[k], f"{view['id']}.{k}")
        refs(view["evidence"], ev_ids, f"{view['id']}.evidence")
        for side in ("before", "after"):
            snap = view[side]
            obj(snap, f"{view['id']}.{side}", ("nodes", "edges"))
            nodes = records(snap["nodes"], "nodes", ("id", "name", "kind", "owner", "fields"))
            node_ids = ids(nodes, f"{view['id']}.{side}.nodes")
            require(nodes, f"{view['id']}.{side}: empty view; use omitted_views for inapplicable views")
            for n in nodes:
                enum(n["kind"], KINDS, f"{n['id']}.kind")
                for k in ("name", "owner"):
                    string(n[k], f"{n['id']}.{k}")
                require(isinstance(n["fields"], dict), f"{n['id']}.fields: expected field-name -> value object")
                for key, value in n["fields"].items():
                    string(key, f"{n['id']}.field name")
                    string(value, f"{n['id']}.{key}")
            edges = records(snap["edges"], "edges", ("id", "from", "to", "label", "cardinality"))
            ids(edges, f"{view['id']}.{side}.edges")
            for e in edges:
                string(e['from'], f"{e['id']}.from")
                string(e['to'], f"{e['id']}.to")
                require(e["from"] in node_ids and e["to"] in node_ids, f"{e['id']}: dangling endpoint")
                string(e["label"], f"{e['id']}.label")
                require(isinstance(e["cardinality"], str), f"{e['id']}.cardinality: expected text")
                if view["kind"] == "entities":
                    string(e["cardinality"], f"{e['id']}.cardinality")
    flows = records(d["flows"], "flows", ("id", "title", "kind", "contract", "evidence", "participants", "scenarios"))
    ids(flows, "flows")
    scenario_ids = set()
    for f in flows:
        enum(f["kind"], {"internal", "third-party"}, f"{f['id']}.kind")
        for k in ("title", "contract"):
            string(f[k], f"{f['id']}.{k}")
        refs(f["evidence"], ev_ids, f"{f['id']}.evidence")
        participants = records(f["participants"], "participants", ("id", "name", "role"))
        pids = ids(participants, f"{f['id']}.participants")
        require(participants, f"{f['id']}: no participants")
        for p in participants:
            string(p["name"], f"{p['id']}.name")
            string(p["role"], f"{p['id']}.role")
        scenarios = records(f["scenarios"], "scenarios", ("id", "title", "steps", "acceptance"))
        require(scenarios, f"{f['id']}: no scenarios")
        sids = ids(scenarios, f"{f['id']}.scenarios")
        require(not (scenario_ids & sids), "scenario IDs must be unique across flows")
        scenario_ids |= sids
        for s in scenarios:
            string(s["title"], f"{s['id']}.title")
            refs(s["acceptance"], acc_ids, f"{s['id']}.acceptance")
            steps = records(s["steps"], "steps", ("from", "to", "label", "mode", "detail"))
            require(steps, f"{s['id']}: no steps")
            for step in steps:
                string(step['from'], f"{s['id']}.from")
                string(step['to'], f"{s['id']}.to")
                require(step["from"] in pids and step["to"] in pids, f"{s['id']}: dangling participant")
                enum(step["mode"], {"sync", "async", "reply", "local"}, f"{s['id']}.mode")
                if step["mode"] == "local":
                    require(step["from"] == step["to"], f"{s['id']}: a local step needs the same participant")
                for k in ("label", "detail"):
                    string(step[k], f"{s['id']}.{k}")
    pseudos = records(d["pseudocode"], "pseudocode", ("id", "title", "code", "invariants", "acceptance"))
    ids(pseudos, "pseudocode")
    for p in pseudos:
        for k in ("title", "code"):
            string(p[k], f"{p['id']}.{k}")
        refs(p["invariants"], inv_ids, f"{p['id']}.invariants")
        refs(p["acceptance"], acc_ids, f"{p['id']}.acceptance")
    for r in records(d["rollout"], "rollout", ("stage", "entry", "change", "exit", "recovery")):
        for k, v in r.items():
            string(v, f"rollout.{k}")
    for r in records(d["risks"], "risks", ("risk", "mitigation", "acceptance")):
        string(r["risk"], "risk")
        string(r["mitigation"], "mitigation")
        refs(r["acceptance"], acc_ids, "risk.acceptance")
    for q in records(d["questions"], "questions", ("question", "affects")):
        string(q["question"], "question")
        string(q["affects"], "question.affects")
    omissions = records(d["omitted_views"], "omitted_views", ("view", "reason"))
    allowed = {"big-picture", "entities", "service-interactions", "third-party", "pseudocode", "acceptance"}
    require(len({o['view'] for o in omissions}) == len(omissions), "duplicate omitted view")
    for o in omissions:
        enum(o["view"], allowed, "omitted_views.view")
        string(o["reason"], "omission.reason")
    present = set()
    if any(v["kind"] == "context" for v in views): present.add("big-picture")
    if any(v["kind"] == "entities" for v in views): present.add("entities")
    if flows: present.add("service-interactions")
    if any(f["kind"] == "third-party" for f in flows): present.add("third-party")
    if pseudos: present.add("pseudocode")
    if acc: present.add("acceptance")
    omitted = {o['view'] for o in omissions}
    require(not (present & omitted), f"views both present and omitted: {present & omitted}")
    require(present | omitted == allowed, f"account for missing views: {allowed - present - omitted}")
    return d


def changes(before, after):
    b = {v["id"]: v for v in before}
    a = {v["id"]: v for v in after}
    return [{"id": ident, "before": b.get(ident), "after": a.get(ident),
        "status": "added" if ident not in b else "removed" if ident not in a else
            "unchanged" if b[ident] == a[ident] else "changed"}
        for ident in dict.fromkeys([*b, *a])]


def describe(item):
    if item is None:
        return "Absent"
    if "name" in item:
        return "; ".join([f"{item['name']} ({item['kind']}; owner: {item['owner']})",
            *[f"{k}: {v}" for k, v in item["fields"].items()]])
    return f"{item['from']} → {item['to']}: {item['label']}" + (f" [{item['cardinality']}]" if item['cardinality'] else "")


def wrap(text, limit=45):
    # HTML labels, escaped before they reach Graphviz.
    import textwrap
    return "<BR ALIGN=\"LEFT\"/>".join(html.escape(x) for x in textwrap.wrap(text, limit, break_long_words=True) or [""])


def graph(view):
    nodes = changes(view["before"]["nodes"], view["after"]["nodes"])
    edges = changes(view["before"]["edges"], view["after"]["edges"])
    lines = ['digraph G { graph [rankdir=LR, bgcolor="transparent", pad="0.3", nodesep="0.45", ranksep="0.65"];',
        'node [shape=box, style="rounded", fontname="Helvetica", fontsize=13, margin="0.16,0.12"];',
        'edge [fontname="Helvetica", fontsize=11, arrowsize=0.7];']
    metadata = {}
    for c in nodes:
        n = c["after"] or c["before"]
        import textwrap
        def node_lines(node, change=None):
            if node is None: return []
            result = [node['name']]
            if change: result.append(change.upper())
            result.append(f"{node['kind']} · {node['owner']}")
            result.extend(f"{k}: {v}" for k,v in node['fields'].items())
            return [line for text in result for line in textwrap.wrap(text, 37, break_long_words=True)]
        modes = {side: node_lines(c[side]) for side in ('before', 'after')}
        if c['status'] == 'changed':
            modes['changes'] = node_lines(n, c['status'])[:3] + ['BEFORE'] + node_lines(c['before']) + ['AFTER'] + node_lines(c['after'])
        else:
            modes['changes'] = node_lines(n, c['status'])
        width = max(220, max(len(line) for rows in modes.values() for line in rows) * 8 + 28)
        height = max(len(rows) for rows in modes.values()) * 18 + 28
        ident = f"{view['id']}-node-{c['id']}"
        lines.append(f'{json.dumps(c["id"])} [id={json.dumps(ident)}, label="", fixedsize=true, width={width / 72:.3f}, height={height / 72:.3f}];')
        metadata[ident] = {"status": c["status"], "type": "node", "before": describe(c["before"]), "after": describe(c["after"]), "modes": modes}
    for c in edges:
        # A moved/changed edge needs two paths to preserve the old connection.
        versions = [("before", c["before"]), ("after", c["after"])] if c['status'] == 'changed' else [("both", c['after'] or c['before'])]
        for side, e in versions:
            ident = f"{view['id']}-edge-{c['id']}-{side}"
            status = c['status'] if side == 'both' else 'removed' if side == 'before' else 'added'
            label = f"{e['label']}" + (f" [{e['cardinality']}]" if e['cardinality'] else '')
            if status != 'unchanged': label = f"{status.upper()}: {label}"
            lines.append(f'{json.dumps(e["from"])} -> {json.dumps(e["to"])} [id={json.dumps(ident)}, label=<{wrap(label, 28)}>];')
            metadata[ident] = {"status": status, "type": "edge", "before": describe(c['before']), "after": describe(c['after'])}
    lines.append('}')
    try:
        result = subprocess.run(["dot", "-Tsvg"], input='\n'.join(lines), text=True,
            capture_output=True, check=True, timeout=30)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise Invalid(f"Graphviz could not render {view['id']}: {getattr(exc, 'stderr', '')}") from exc
    svg = ET.fromstring(result.stdout)
    svg.set("role", "img")
    svg.set("aria-label", view['title'] + ': stable union of existing and proposed structure. See the change ledger for text.')
    svg.set("class", "architecture")
    svg.set('style', f"min-width:{float(svg.get('viewBox').split()[2]) * 11 / 12:.1f}px")
    for group in svg.iter(f"{{{NS}}}g"):
        m = metadata.get(group.get("id"))
        if not m: continue
        group.set("class", group.get("class", "") + f" state-{m['status']}")
        group.set("data-before", m['before'])
        group.set("data-after", m['after'])
        if m['type'] == 'edge':
            import copy
            for text in list(group.findall(f'{{{NS}}}text')):
                text.set('class', 'change-edge-label')
                snapshot_text = copy.deepcopy(text)
                snapshot_text.set('class', 'snapshot-edge-label')
                snapshot_text.text = re.sub(r'^(ADDED|REMOVED):\s*', '', snapshot_text.text or '')
                group.append(snapshot_text)
        if m['type'] == 'node':
            shape = group.find(f'{{{NS}}}path')
            require(shape is not None, 'Graphviz returned an unexpected node shape')
            coords = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', shape.get('d', ''))]
            left, top = min(coords[::2]), min(coords[1::2])
            for mode, rows in m['modes'].items():
                label_group = ET.SubElement(group, f'{{{NS}}}g', {'class': 'node-label label-' + mode})
                for i, row in enumerate(rows):
                    text = ET.SubElement(label_group, f'{{{NS}}}text', {'x': str(left + 14), 'y': str(top + 22 + i * 18), 'text-anchor': 'start', 'class': 'node-name' if i == 0 else 'node-detail'})
                    text.text = row
    return ET.tostring(svg, encoding="unicode")


def safe(text):
    return html.escape(str(text), quote=True)


def paragraph(text):
    return f"<p>{safe(text)}</p>"


def bullets(items):
    return '<ul>' + ''.join('<li>' + safe(x) + '</li>' for x in items) + '</ul>'


def table(headers, rows):
    return '<div class="table-scroll"><table><thead><tr>' + ''.join(f'<th scope="col">{safe(x)}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + safe(x) + '</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def section(ident, title, content):
    return f'<section id="{safe(ident)}"><header><h2>{safe(title)}</h2></header>{content}</section>'


def html_report(d):
    sections = [section("overview", "The decision at a glance", paragraph(d['problem']) +
        '<div class="columns"><div><h3>Goals</h3>' + bullets(d['goals']) + '</div><div><h3>Outside this change</h3>' + bullets(d['non_goals']) + '</div></div>' +
        table(["Invariant", "Contract"], [[i['id'], i['text']] for i in d['invariants']]))]
    for v in d['views']:
        ledger = [c for key in ('nodes', 'edges') for c in changes(v['before'][key], v['after'][key]) if c['status'] != 'unchanged']
        sections.append(section('view-' + v['id'], v['title'], paragraph(v['note']) +
            '<div class="view" data-mode="changes"><div class="compare" role="group" aria-label="Structure snapshot">' +
            ''.join(f'<button type="button" data-mode="{mode}" aria-pressed="{str(mode == "changes").lower()}">{name}</button>' for mode, name in [('before', 'Before'), ('changes', 'Changes'), ('after', 'After')]) +
            '</div><p class="legend"><span>Unchanged</span><span class="added">+ Added</span><span class="changed">~ Changed</span><span class="removed">− Removed</span></p>' +
            '<div class="graph-scroll">' + graph(v) + '</div><p class="snapshot-label" aria-live="polite">Changes: existing and proposed structure together.</p></div>' +
            table(['Object', 'Change', 'Before', 'After'], [[c['id'], c['status'], describe(c['before']), describe(c['after'])] for c in ledger])))
    for f in d['flows']:
        content = paragraph(f['contract']) + table(['Participant', 'Responsibility / authority'], [[p['name'], p['role']] for p in f['participants']])
        names = {p['id']: p['name'] for p in f['participants']}
        for s in f['scenarios']:
            steps = '<ol class="steps">' + ''.join(f'<li data-step="{i}"><strong>{safe(names[t["from"]])} → {safe(names[t["to"]])}</strong><span class="mode">{safe(t["mode"])}</span><p>{safe(t["label"])}</p><p class="step-detail">{safe(t["detail"])}</p></li>' for i,t in enumerate(s['steps'])) + '</ol>'
            content += f'<article class="scenario" data-scenario="{safe(s["id"])}"><h3>{safe(s["title"])} <small>{safe(s["id"])}</small></h3><div class="sequence-scroll">{sequence_svg(f, s)}</div><div class="step-controls"><button type="button" data-action="previous">Previous</button><button type="button" data-action="next">Next step</button><span class="step-status" aria-live="polite"></span></div>{steps}<p class="trace">Acceptance: {safe(", ".join(s["acceptance"]) or "Unspecified")}</p></article>'
        sections.append(section('flow-' + f['id'], f['title'], content))
    sections.append(section('decisions', 'Why this direction', ''.join('<article><h3>' + safe(dec['id'] + ' · ' + dec['title']) + '</h3><p class="status">' + safe(dec['status']) + '</p>' + (paragraph('Supersedes: ' + dec['supersedes']) if dec.get('supersedes') else '') + paragraph(dec['context']) + table(['Option', 'Tradeoffs'], [[o['name'], ' / '.join(o['tradeoffs'])] for o in dec['options']]) + paragraph('Choice: ' + dec['choice']) + bullets(dec['consequences']) + '</article>' for dec in d['decisions'])))
    sections.append(section('pseudocode', 'Behavior in pseudocode', ''.join('<article><h3>' + safe(p['title']) + '</h3><pre><code>' + safe(p['code']) + '</code></pre><p class="trace">' + safe('Invariants: ' + ', '.join(p['invariants']) + ' · Acceptance: ' + ', '.join(p['acceptance'])) + '</p></article>' for p in d['pseudocode'])))
    sections.append(section('acceptance', 'Acceptance in domain language', ''.join('<article class="acceptance"><h3>' + safe(a['id'] + ' · ' + a['title']) + '</h3><p class="status">' + safe(a['status']) + '</p>' + paragraph('Given ' + a['given']) + paragraph('When ' + a['when']) + '<p><strong>Then</strong></p>' + bullets(a['then']) + '<p class="trace">' + safe('Invariants: ' + ', '.join(a['invariants'])) + '</p></article>' for a in d['acceptance'])))
    sections.append(section('rollout', 'Getting from here to there', table(['Stage', 'Entry', 'Change', 'Exit / proof', 'Recovery'], [[r[k] for k in ('stage', 'entry', 'change', 'exit', 'recovery')] for r in d['rollout']]) + '<h3>Risks</h3>' + table(['Risk', 'Mitigation', 'Acceptance'], [[r['risk'], r['mitigation'], ', '.join(r['acceptance'])] for r in d['risks']])))
    sections.append(section('questions', 'Open questions', table(['Question', 'Decision affected'], [[q['question'], q['affects']] for q in d['questions']]) if d['questions'] else paragraph('No open questions recorded.')))
    sections.append(section('evidence', 'Evidence and assumptions', table(['ID', 'Status', 'Source', 'Establishes'], [[e[k] for k in ('id', 'status', 'source', 'claim')] for e in d['evidence']]) + (table(['Omitted view', 'Reason'], [[o['view'], o['reason']] for o in d['omitted_views']]) if d['omitted_views'] else '')))
    viewer = (ROOT / 'assets/viewer.html').read_text()
    return viewer.replace('<!--TITLE-->', safe(d['title'])).replace('<!--STATUS-->', safe(d['status'])).replace('<!--BASELINE-->', safe(d['baseline']['label'] + ' · ' + d['baseline']['revision'])).replace('<!--SUMMARY-->', safe(d['summary'])).replace('<!--CONTENT-->', '\n'.join(sections))


def sequence_svg(flow, scenario):
    # Fixed readable lanes; explicit scrolling on small viewports, rather than microscopic text.
    participants = flow['participants']
    width = max(680, 220 * len(participants))
    import textwrap
    heading_lines = max(len(textwrap.wrap(p['name'], 23, break_long_words=True)) for p in participants)
    heading_height = max(60, 24 + 18 * heading_lines)
    wrapped = [textwrap.wrap(f"{i+1}. {t['label']}", 34, break_long_words=True) for i,t in enumerate(scenario['steps'])]
    heights = [max(100, 45 + len(lines) * 16) for lines in wrapped]
    height = heading_height + sum(heights) + 30
    xs = {p['id']: 110 + i * 220 for i, p in enumerate(participants)}
    marker = f"arrow-{flow['id']}-{scenario['id']}"
    out = [f'<svg class="sequence" style="width:{width}px" role="img" aria-label="{safe(scenario["title"])}: numbered service interactions; full details below." viewBox="0 0 {width} {height}"><defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/></marker></defs>']
    for p in participants:
        x = xs[p['id']]
        for j, line in enumerate(textwrap.wrap(p['name'], 23, break_long_words=True)):
            out.append(f'<text x="{x}" y="{24+18*j}" text-anchor="middle" class="participant">{safe(line)}</text>')
        out.append(f'<line class="lifeline" x1="{x}" y1="{heading_height}" x2="{x}" y2="{height - 15}"/>')
    offset = heading_height
    for i, t in enumerate(scenario['steps']):
        x1, x2, y = xs[t['from']], xs[t['to']], offset + heights[i] - 20
        offset += heights[i]
        out.append(f'<g data-message="{i}" class="message">')
        if x1 == x2:
            out.append(f'<path class="{t["mode"]}" d="M {x1} {y} h 60 v 22 h -60" marker-end="url(#{marker})"/>')
            tx, anchor = x1 + 16, 'start'
        else:
            out.append(f'<line class="{t["mode"]}" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" marker-end="url(#{marker})"/>')
            tx, anchor = (x1 + x2) / 2, 'middle'
        for j, line in enumerate(wrapped[i]):
            out.append(f'<text x="{tx}" y="{y - 14 - (len(wrapped[i])-1)*16 + 16*j}" text-anchor="{anchor}">{safe(line)}</text>')
        out.append('</g>')
    out.append('</svg>')
    return ''.join(out)


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', '<br>')


def md_table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] + ['| ' + ' | '.join(cell(x) for x in r) + ' |' for r in rows]) + '\n'


def md_list(items):
    return '\n'.join('- ' + x for x in items) + '\n'


def mm(text):
    # Mermaid quoted-label syntax needs entities; source text cannot inject markup/directives.
    entities = {'&':'#38;', '"':'#quot;', '<':'#60;', '>':'#62;', '#':'#35;', ';':'#59;', '`':'#96;', '|':'#124;', '\n':'<br/>', '\r':''}
    return ''.join(entities.get(c,c) for c in str(text))


def mermaid(view, side):
    snap = view[side]
    lines = ['flowchart LR']
    names = {n['id']: f'n{i}' for i, n in enumerate(snap['nodes'])}
    for n in snap['nodes']:
        label = '<br/>'.join(mm(v) for v in [n['name'], n['kind'] + ' · ' + n['owner'], *[k + ': ' + v for k,v in n['fields'].items()]])
        lines.append(f'  {names[n["id"]]}["{label}"]')
    for e in snap['edges']:
        label = e['label'] + (f" [{e['cardinality']}]" if e['cardinality'] else '')
        lines.append(f'  {names[e["from"]]} -->|"{mm(label)}"| {names[e["to"]]}')
    return '```mermaid\n' + '\n'.join(lines) + '\n```\n'


def adr(dec, evidence):
    lines = [f"# {dec['id']}: {dec['title']}", f"Status: {dec['status']}"]
    if dec.get('supersedes'): lines.append('Supersedes: ' + dec['supersedes'])
    lines += ['## Context', dec['context'], '## Options', md_table(['Option', 'Tradeoffs'], [[o['name'], ' / '.join(o['tradeoffs'])] for o in dec['options']]), '## Decision', dec['choice'], '## Consequences', md_list(dec['consequences']), '## Evidence', md_table(['ID', 'Status', 'Source', 'Claim'], [[e[k] for k in ('id', 'status', 'source', 'claim')] for e in evidence if e['id'] in dec['evidence']])]
    return '\n\n'.join(lines) + '\n'


def markdown(d):
    lines = [f"# {d['title']}", f"Status: {d['status']}", 'Baseline: ' + d['baseline']['label'] + ' · ' + d['baseline']['revision'], d['summary'], '## Problem', d['problem'], '## Goals', md_list(d['goals']), '## Non-goals', md_list(d['non_goals']), '## Invariants', md_table(['ID', 'Contract', 'Evidence'], [[i['id'], i['text'], ', '.join(i['evidence'])] for i in d['invariants']])]
    for v in d['views']:
        lines += ['## ' + v['title'], v['note']]
        for side in ('before', 'after'):
            lines += ['### ' + side.title(), mermaid(v, side)]
        ledger = [c for key in ('nodes', 'edges') for c in changes(v['before'][key], v['after'][key]) if c['status'] != 'unchanged']
        lines += ['### Change ledger', md_table(['Object', 'Status', 'Before', 'After'], [[c['id'], c['status'], describe(c['before']), describe(c['after'])] for c in ledger])]
    for f in d['flows']:
        lines += ['## ' + f['title'], f['contract'], md_table(['Participant', 'Role'], [[p['name'], p['role']] for p in f['participants']])]
        names = {p['id']: f'p{i}' for i,p in enumerate(f['participants'])}
        for s in f['scenarios']:
            diagram = ['sequenceDiagram'] + [f'  participant {names[p["id"]]} as {mm(p["name"])}' for p in f['participants']]
            for t in s['steps']:
                arrow = {'sync': '->>', 'async': '-)', 'reply': '-->>', 'local': '->>'}[t['mode']]
                diagram.append(f'  {names[t["from"]]}{arrow}{names[t["to"]]}: {mm(t["label"])}')
            lines += ['### ' + s['id'] + ' · ' + s['title'], '```mermaid\n' + '\n'.join(diagram) + '\n```', md_table(['Step', 'Mode', 'Behavior / outcome'], [[str(i+1), t['mode'], t['detail']] for i,t in enumerate(s['steps'])]), 'Acceptance: ' + ', '.join(s['acceptance'])]
    lines += ['## Decisions'] + [re.sub(r'^(#{1,2}) ', r'##\1 ', adr(dec, d['evidence']), flags=re.MULTILINE) for dec in d['decisions']]
    lines += ['## Pseudocode']
    for p in d['pseudocode']:
        fence = '`' * max(3, max((len(m[0]) for m in re.finditer(r'`+', p['code'])), default=0) + 1)
        lines += ['### ' + p['title'], fence + 'text\n' + p['code'] + '\n' + fence, 'Invariants: ' + ', '.join(p['invariants']) + ' · Acceptance: ' + ', '.join(p['acceptance'])]
    lines += ['## Acceptance scenarios']
    for a in d['acceptance']:
        lines += ['### ' + a['id'] + ' · ' + a['title'], 'Execution: ' + a['status'], '**Given** ' + a['given'], '**When** ' + a['when'], '**Then**\n\n' + md_list(a['then']), 'Invariants: ' + ', '.join(a['invariants'])]
    lines += ['## Rollout', md_table(['Stage', 'Entry', 'Change', 'Exit', 'Recovery'], [[r[k] for k in ('stage', 'entry', 'change', 'exit', 'recovery')] for r in d['rollout']]), '## Risks', md_table(['Risk', 'Mitigation', 'Acceptance'], [[r['risk'], r['mitigation'], ', '.join(r['acceptance'])] for r in d['risks']]), '## Open questions', md_table(['Question', 'Affects'], [[q['question'], q['affects']] for q in d['questions']]), '## Evidence', md_table(['ID', 'Status', 'Source', 'Claim'], [[e[k] for k in ('id', 'status', 'source', 'claim')] for e in d['evidence']]), '## Omitted views', md_table(['View', 'Reason'], [[o['view'], o['reason']] for o in d['omitted_views']])]
    return '\n\n'.join(lines) + '\n'


def warnings(d):
    result = []
    if d['status'] == 'accepted' and any(e['status'] in {'unknown', 'assumption'} for e in d['evidence']):
        result.append('Accepted design retains assumptions/unknown facts; confirm which are decision-critical.')
    covered = {i for a in d['acceptance'] for i in a['invariants']}
    for i in d['invariants']:
        if i['id'] not in covered: result.append(i['id'] + ': no acceptance scenario references this invariant.')
    for f in d['flows']:
        if f['kind'] == 'third-party' and len(f['scenarios']) < 2:
            result.append(f['id'] + ': only one third-party scenario; consider its important failure/unknown-outcome path.')
    if any(e['status'] == 'illustrative' for e in d['evidence']):
        result.append('Contains illustrative evidence. This is an example, not a verified system design.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='design JSON input')
    parser.add_argument('--out', type=Path, required=True, help='report directory; existing generated files are replaced')
    parser.add_argument('--markdown-only', action='store_true', help='skip SVG/HTML; Graphviz is not needed')
    args = parser.parse_args()
    try:
        d = validate(json.loads(args.source.read_text()))
        require(args.source.resolve().parent != args.out.resolve(), 'Use a separate report directory so the JSON input cannot be overwritten.')
        if not args.markdown_only:
            require(shutil.which('dot'), 'Graphviz dot is missing. Install Graphviz or use --markdown-only.')
        # Complete rendering before writing anything: a failed graph does not leave partial deliverables.
        report = None if args.markdown_only else html_report(d)
        md = markdown(d)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'design.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
        (args.out / 'design.md').write_text(md)
        for dec in d['decisions']:
            (args.out / f"adr-{dec['id']}.md").write_text(adr(dec, d['evidence']))
        if report is not None: (args.out / 'design.html').write_text(report)
        elif (args.out / 'design.html').exists():
            (args.out / 'design.html').unlink()
        for warning in warnings(d): print('WARNING: ' + warning, file=sys.stderr)
        print(f"Built {len(d['views'])} views, {sum(len(f['scenarios']) for f in d['flows'])} flow scenarios, {len(d['acceptance'])} acceptance scenarios → {args.out}")
    except (Invalid, OSError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

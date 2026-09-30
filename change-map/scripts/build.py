#!/usr/bin/env python3
"""Merge a change map and inline it into the viewer as one self-contained page.

    build.py change.json judgment.json gwt.json -o change-map.html
    build.py change.json judgment.json gwt.json -o change-map.html --standalone   # adds a doctype, to open locally
    build.py change.json judgment.json gwt.json --check                            # validate only

Files merge left to right. change.json comes from triage.py. judgment.json is
what the agent writes (see template.json). A file holding a JSON list is the
Given/When/Then rules. Merge rules that keep judgment.json small:

- meta merges key by key.
- api as an object {"POST /path": {scope, emits, note}} enriches the routes
  triage found; as a list it replaces them.
- schema.tables as an object {table: {note, notes, cols: {col: meaning},
  idx: {index: serves}}} enriches the tables triage parsed; schema.refs as an
  object {table: note} annotates referenced tables. Lists replace.
- every other key replaces.

The viewer is found next to this script (../viewer.html). Pass --viewer with a
path or URL when the script runs alone, for example on a cloud worker.
"""

import argparse
import json
import os
import re
import sys
import urllib.request

VIEWER_URL = "https://raw.githubusercontent.com/nanostack-dev/skills/main/change-map/viewer.html"
CAPS = {"decisions": 7, "watch": 6, "flows": 5, "api": 16, "rules": 10, "scenarios": 4}


def read_viewer(where):
    if where.startswith("http"):
        with urllib.request.urlopen(where) as resp:
            return resp.read().decode()
    with open(where) as fh:
        return fh.read()


def merge_api(base, over):
    if isinstance(over, list):
        return over
    routes = [dict(r) for r in base or []]
    for key, fields in over.items():
        method, _, path = key.partition(" ")
        hit = next((r for r in routes if r["m"] == method.upper() and r["p"] == path), None)
        if hit:
            hit.update(fields)
        else:
            routes.append({"m": method.upper(), "p": path, **fields})
    return routes


def merge_schema(base, over):
    if not base or isinstance(over.get("tables"), list):
        return {**(base or {}), **over}
    out = {**base, **{k: v for k, v in over.items() if k not in ("tables", "refs")}}
    tables = {t["name"]: t for t in base.get("tables") or []}
    for name, patch in (over.get("tables") or {}).items():
        table = tables.setdefault(name, {"name": name, "cols": [], "idx": []})
        for key, value in patch.items():
            if key == "cols" and isinstance(value, dict):
                for col in table["cols"]:
                    if col[0] in value:
                        v = value[col[0]]
                        col[:] = [col[0], *v] if isinstance(v, list) else [*col[:3], v]
                drop = {c for c, v in value.items() if v is None}
                table["cols"] = [c for c in table["cols"] if c[0] not in drop]
            elif key == "idx" and isinstance(value, dict):
                for idx in table["idx"]:
                    for name, serves in value.items():
                        if idx[0] == name or idx[0].endswith(name.lstrip("…")):
                            idx[2] = serves
            else:
                table[key] = value
    out["tables"] = list(tables.values())
    refs = over.get("refs")
    if isinstance(refs, dict):
        known = {r["name"]: r for r in base.get("refs") or []}
        for name, note in refs.items():
            known.setdefault(name, {"name": name, "cols": []})["note"] = note
        out["refs"] = list(known.values())
    elif isinstance(refs, list):
        out["refs"] = refs
    return out


def merge(base, over):
    if isinstance(over, list):
        return {**base, "rules": over}
    out = dict(base)
    for key, value in over.items():
        if key == "meta":
            out["meta"] = {**base.get("meta", {}), **value}
        elif key == "api":
            out["api"] = merge_api(base.get("api"), value)
        elif key == "schema" and isinstance(value, dict):
            out["schema"] = merge_schema(base.get("schema"), value)
        else:
            out[key] = value
    return out


def check(data):
    problems = []
    for key in ("meta", "summary", "decisions"):
        if not data.get(key):
            problems.append(f"missing {key}")
    for key, cap in CAPS.items():
        if len(data.get(key) or []) > cap:
            problems.append(f"{key} has {len(data[key])} entries, cap is {cap}: merge or cut")
    for d in data.get("decisions") or []:
        for field in ("id", "title", "choice", "why", "instead", "cost"):
            if not d.get(field):
                problems.append(f"decision {d.get('id') or d.get('title')!r} has no {field}")
    for f in data.get("flows") or []:
        tx = f.get("tx")
        if tx and not (0 <= tx[0] <= tx[1] < len(f.get("steps") or [])):
            problems.append(f"flow {f.get('name')!r} has tx {tx} outside its steps")
    scenario_ids = {sc.get("id") for sc in data.get("scenarios") or []}
    for d in data.get("decisions") or []:
        if d.get("see") and d["see"] not in scenario_ids:
            problems.append(f"decision {d.get('id')!r} points at missing scenario {d['see']!r}")
    for sc in data.get("scenarios") or []:
        actors = {a["id"] for a in sc.get("actors") or []}
        steps = sc.get("steps") or []
        if len(steps) > 12:
            problems.append(f"scenario {sc.get('id')!r} has {len(steps)} steps, cap is 12")
        for i, st in enumerate(steps):
            for end in ("from", "to"):
                if st.get(end) is not None and st[end] not in actors:
                    problems.append(f"scenario {sc.get('id')!r} step {i} {end} {st[end]!r} is not an actor")
            if st.get("k") == "block" and not (i < st.get("until", -1) < len(steps)):
                problems.append(f"scenario {sc.get('id')!r} step {i} blocks until a step that does not follow it")
            if len(st.get("label", "")) > 44:
                problems.append(f"scenario {sc.get('id')!r} step {i} label is over 44 characters")
    system = data.get("system") or {}
    nodes = {n["id"] for n in system.get("nodes") or []}
    if len(nodes) > 12:
        problems.append(f"system has {len(nodes)} nodes, cap is 12")
    cells = [(n.get("col"), n.get("row")) for n in system.get("nodes") or []]
    if len(cells) != len(set(cells)):
        problems.append("two system nodes share a col and row")
    for e in system.get("edges") or []:
        if e.get("from") not in nodes or e.get("to") not in nodes:
            problems.append(f"system edge {e.get('from')} -> {e.get('to')} names a missing node")
    ops = (data.get("model") or {}).get("ops") or {}
    for row in ops.get("rows") or []:
        if len(row) != len(ops.get("cols") or []) + 1:
            problems.append(f"model.ops row {row[0]!r} has {len(row) - 1} cells for {len(ops['cols'])} columns")
    names = {n for t in data.get("tests") or [] for n in t.get("names") or []}
    examples = [e.get("test") for r in data.get("rules") or [] for e in r.get("examples") or []]
    if names and examples:
        missing, unknown = names - set(examples), set(examples) - names
        if missing:
            problems.append(f"{len(missing)} tests have no Given/When/Then row, e.g. {sorted(missing)[0]}")
        if unknown:
            problems.append(f"{len(unknown)} examples name a test that is not in the diff, e.g. {sorted(unknown)[0]}")
        dupes = {t for t in examples if examples.count(t) > 1}
        if dupes:
            problems.append(f"{len(dupes)} tests appear in more than one row, e.g. {sorted(dupes)[0]}")
    points = (data.get("decisions") or []) + (data.get("watch") or [])
    bare = [pt.get("id") or pt.get("title") for pt in points if not pt.get("example")]
    if bare:
        problems.append(f"{len(bare)} of {len(points)} review points have no example (request, response, row, event), e.g. {bare[0]!r}")
    for pt in points:
        for ex in pt.get("example") or []:
            if not ex.get("code") or len(ex["code"].splitlines()) > 24:
                problems.append(f"example {ex.get('label')!r} on {pt.get('id')!r} is empty or over 24 lines")
    for t in (data.get("schema") or {}).get("tables") or []:
        blank = [c[0] for c in t.get("cols") or [] if not c[3]]
        if blank:
            problems.append(f"schema {t['name']}: no meaning for {', '.join(blank)}")
    return problems


def summary(data):
    count = lambda k: len(data.get(k) or [])
    tables = len((data.get("schema") or {}).get("tables") or [])
    examples = sum(len(r.get("examples") or []) for r in data.get("rules") or [])
    return (f"{count('decisions')} decisions, {count('watch')} watch, {count('scenarios')} scenarios, "
            f"{len((data.get('system') or {}).get('nodes') or [])} system nodes, {tables} tables, "
            f"{count('flows')} flows, {count('api')} routes, {count('rules')} rules / {examples} examples")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="+")
    ap.add_argument("-o", "--out", default="change-map.html")
    ap.add_argument("--viewer", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--standalone", action="store_true")
    ap.add_argument("--check", action="store_true", help="validate and print the summary, write nothing")
    args = ap.parse_args()

    data = {}
    for path in args.data:
        with open(path) as fh:
            data = merge(data, json.load(fh))
    problems = check(data)
    for p in problems:
        print(f"warn: {p}", file=sys.stderr)
    print(summary(data), file=sys.stderr)
    if args.check:
        sys.exit(1 if problems else 0)

    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer.html")
    viewer = read_viewer(args.viewer or (local if os.path.exists(local) else VIEWER_URL))

    meta = data.get("meta") or {}
    title = args.title or (
        f"{(meta.get('repo') or '').split('/')[-1].capitalize()} #{meta['number']} review".strip()
        if meta.get("number") else f"{meta.get('head', 'Work')} change map")
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    page = viewer.replace("/*CHANGE_MAP_DATA*/null", payload, 1)
    page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", page, count=1)
    if args.standalone:
        page = f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n{page}\n</body></html>\n'

    with open(args.out, "w") as fh:
        fh.write(page)
    print(f"wrote {args.out} ({len(page) // 1024} KB, data {len(payload) // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()

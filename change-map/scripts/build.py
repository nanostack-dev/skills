#!/usr/bin/env python3
"""Inline a change map into the viewer and write one self-contained HTML page.

    build.py change.json -o change-map.html               # for the Artifact tool
    build.py change.json -o change-map.html --standalone  # adds a doctype, to open locally

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


def check(data):
    problems = []
    for key in ("meta", "summary", "decisions"):
        if not data.get(key):
            problems.append(f"missing {key}")
    for key, cap in CAPS.items():
        if len(data.get(key) or []) > cap:
            problems.append(f"{key} has {len(data[key])} entries, cap is {cap}: merge or cut")
    for d in data.get("decisions") or []:
        for field in ("id", "title", "choice", "why"):
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
    nodes = {n["id"] for n in (data.get("system") or {}).get("nodes") or []}
    if len(nodes) > 12:
        problems.append(f"system has {len(nodes)} nodes, cap is 12")
    for e in (data.get("system") or {}).get("edges") or []:
        if e.get("from") not in nodes or e.get("to") not in nodes:
            problems.append(f"system edge {e.get('from')} -> {e.get('to')} names a missing node")
    names = {n for t in data.get("tests") or [] for n in t.get("names") or []}
    examples = [e.get("test") for r in data.get("rules") or [] for e in r.get("examples") or []]
    if names and examples:
        missing = names - set(examples)
        unknown = set(examples) - names
        if missing:
            problems.append(f"{len(missing)} tests have no Given/When/Then row, e.g. {sorted(missing)[0]}")
        if unknown:
            problems.append(f"{len(unknown)} examples name a test that is not in the diff, e.g. {sorted(unknown)[0]}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("-o", "--out", default="change-map.html")
    ap.add_argument("--viewer", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--standalone", action="store_true")
    args = ap.parse_args()

    with open(args.data) as fh:
        data = json.load(fh)
    problems = check(data)
    for p in problems:
        print(f"warn: {p}", file=sys.stderr)

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

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
CAPS = {"decisions": 7, "watch": 6, "flows": 5, "api": 16, "rules": 10}


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

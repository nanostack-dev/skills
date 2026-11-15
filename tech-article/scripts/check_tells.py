#!/usr/bin/env python3
"""Flag writing tells in a draft (see ../references/writing-tells.md).

Usage:
  check_tells.py DRAFT [DRAFT ...]          report hits and rates
  check_tells.py --calibrate CORPUS_DIR     rebuild baseline.json from human articles

The report lists each hit with its line and the draft's rate per 10,000 words.
Terms that the pre-2023 baseline corpus also uses often are marked "context":
read the sentence and keep the word when it carries meaning. A hit is a prompt
to look, never proof of anything about the author.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE / "baseline.json"

# term -> plain replacement. Patterns are matched case-insensitively on word boundaries.
WORDS = {
    r"delv(e|es|ed|ing)": "look at, examine, or cut",
    r"underscor(e|es|ed|ing)": "show, stress, or cut",
    r"showcas(e|es|ed|ing)": "show",
    r"highlight(s|ed|ing)?": "show, or cut",
    r"emphasi[sz](e|es|ed|ing)": "stress, or cut",
    r"foster(s|ed|ing)?": "encourage, build",
    r"enhanc(e|es|ed|ing|ement)": "improve, and say by how much",
    r"elevat(e|es|ed|ing)": "improve",
    r"leverag(e|es|ed|ing)": "use",
    r"utili[sz](e|es|ed|ing|ation)": "use",
    r"harness(es|ed|ing)?": "use",
    r"streamlin(e|es|ed|ing)": "simplify, or name what was removed",
    r"bolster(s|ed|ing)?": "strengthen",
    r"garner(s|ed|ing)?": "get",
    r"encompass(es|ed|ing)?": "include",
    r"(align|resonate)s? with": "match, fit",
    r"prioriti[sz](e|es|ed|ing)": "put first",
    r"facilitat(e|es|ed|ing)": "help, let",
    r"unlock(s|ed|ing)?": "let you",
    r"empower(s|ed|ing)?": "let you",
    r"embark(s|ed|ing)?": "start",
    r"navigat(e|es|ed|ing) the complexit(y|ies)": "handle",
    r"(serves|stands|functions|acts) as": "is",
    r"boasts?": "has",
    r"comprises?": "has, is made of",
    r"crucial(ly)?": "name the effect, or cut",
    r"vital": "name the effect, or cut",
    r"pivotal": "name the effect",
    r"significant(ly)?": "give the number",
    r"robust(ness)?": "say what it survives",
    r"seamless(ly)?": "say what the reader no longer does",
    r"comprehensive": "list what it covers",
    r"intricate": "name the parts",
    r"multifaceted": "name the parts",
    r"nuanced": "state the nuance",
    r"meticulous(ly)?": "careful, or show the care",
    r"groundbreaking": "give the evidence",
    r"renowned": "give the evidence",
    r"cutting[- ]edge": "give the evidence",
    r"state[- ]of[- ]the[- ]art": "give the evidence",
    r"(a )?diverse array": "many, or the count",
    r"wide range of": "many, or the count",
    r"vibrant": "cut",
    r"profound(ly)?": "cut",
    r"enduring": "lasting",
    r"valuable insights?": "state the insight",
    r"landscape": "field, area, or name it",
    r"realm": "area",
    r"tapestry": "name the parts",
    r"testament to": "shows",
    r"interplay": "relationship",
    r"(at|in) the heart of": "cut",
    r"nestled": "cut",
    r"bustling": "cut",
    r"(setting|sets|set) the stage": "led to",
    r"pav(e|es|ed|ing) the way": "led to",
    r"focal point": "center",
    r"cornerstone": "cut",
    r"game[- ]changer": "state the change",
    r"indelible": "cut",
    r"deeply rooted": "cut",
    r"notably": "cut",
    r"importantly": "cut",
    r"interestingly": "cut",
    r"remarkabl[ey]": "cut",
    r"moreover": "and, or a new sentence",
    r"furthermore": "and, or a new sentence",
    r"additionally": "and, also",
    r"ultimately": "cut",
    r"it'?s worth noting": "cut",
    r"it'?s important to note": "cut",
    r"plays? an? (crucial|key|vital|pivotal|important) role": "say how",
    r"fast-paced world": "cut",
    r"ever-(evolving|changing)": "cut",
    r"let'?s dive in": "cut",
    r"deep dive": "cut",
    r"at its core": "cut",
    r"think of it as": "state the thing",
    r"imagine a world": "state the thing",
    r"here'?s the kicker": "cut",
    r"experts (say|argue|agree)": "name the source",
    r"studies show": "name the source",
    r"in conclusion": "cut, or a real conclusion",
    r"in summary": "cut, or a real conclusion",
    r"to sum up": "cut",
    r"i hope this helps": "cut",
    r"happy coding": "cut",
    r"as of my last": "a date",
}

PATTERNS = {
    "negative parallelism": (re.compile(r"\b(not (just|only|merely) [^.;:]{1,60}[,;:—-]+ (it'?s|but|it is)|isn'?t (just|about) [^.]{1,60}\. it'?s)", re.I), "state what it is"),
    "punchy fragment reveal": (re.compile(r"(^|[.!?]\s+)(The|And the|So the|What) [A-Za-z ]{1,30}\? [A-Z]", re.M), "write the sentence plainly"),
    "trailing -ing analysis": (re.compile(r", (highlighting|underscoring|showcasing|emphasizing|reflecting|symbolizing|ensuring|demonstrating) ", re.I), "cut the clause or give it a subject"),
    "bold-header bullet": (re.compile(r"^\s*[-*] \*\*[^*]{1,40}:?\*\*:?", re.M), "plain sentence or a table"),
    "colon or title-case heading": (re.compile(r"^#{1,4} ([A-Z][a-z]+ ){1,}[A-Z][a-z]+:? [A-Z]", re.M), "sentence case that names the topic"),
    "emoji": (re.compile("[\U0001F300-\U0001FAFF☀-➿]"), "cut"),
}

TOKEN = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def _blank(m):
    # keep newlines so reported line numbers match the source file
    return "\n" * m.group(0).count("\n")


def strip_markup(text):
    text = text.replace("\u2019", "'")  # curly apostrophes
    text = re.sub(r"^---\n.*?\n---\n", _blank, text, flags=re.S)  # frontmatter
    text = re.sub(r"```.*?```", _blank, text, flags=re.S)  # code blocks
    text = re.sub(r"<(script|style|pre|code)\b.*?</\1>", _blank, text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", lambda m: " " + _blank(m), text)  # tags, keep text
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def compiled():
    return {k: re.compile(r"\b" + k + r"\b", re.I) for k in WORDS}


def count(text, regs):
    return {k: len(r.findall(text)) for k, r in regs.items()}


def calibrate(corpus_dir):
    regs = compiled()
    totals = {k: 0 for k in WORDS}
    words = 0
    files = sorted(Path(corpus_dir).glob("*.txt"))
    for f in files:
        t = strip_markup(f.read_text(errors="ignore"))
        words += len(TOKEN.findall(t))
        for k, n in count(t, regs).items():
            totals[k] += n
    rates = {k: round(v * 10000 / max(words, 1), 2) for k, v in totals.items()}
    dashes = sum(f.read_text(errors="ignore").count("—") for f in files)
    out = {
        "corpus": "pre-2023 technical articles (see ../references/exemplars.md)",
        "files": len(files),
        "words": words,
        "em_dash_per_10k": round(dashes * 10000 / max(words, 1), 2),
        "rate_per_10k": rates,
    }
    BASELINE.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"baseline: {len(files)} files, {words} words -> {BASELINE}")


def report(path, base):
    raw = Path(path).read_text(errors="ignore")
    text = strip_markup(raw)
    nwords = max(len(TOKEN.findall(text)), 1)
    regs = compiled()
    lines = text.splitlines()
    hits = []
    for i, line in enumerate(lines, 1):
        for k, r in regs.items():
            for m in r.finditer(line):
                hits.append((i, m.group(0), WORDS[k], k))
    pattern_hits = []
    for name, (r, fix) in PATTERNS.items():
        for m in r.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            pattern_hits.append((ln, name, m.group(0).strip()[:60], fix))
    rates = base.get("rate_per_10k", {}) if base else {}
    print(f"{path}: {nwords} words, {len(hits)} word hits ({len(hits) * 10000 / nwords:.1f} per 10k)")
    if base:
        human = sum(rates.values())
        print(f"  baseline: {human:.1f} per 10k across {base['files']} pre-2023 articles")
    for ln, word, fix, k in sorted(hits):
        tag = " [context]" if rates.get(k, 0) >= 0.4 else ""
        print(f"  {ln:>4}  {word!r:24} -> {fix}{tag}")
    for ln, name, snippet, fix in sorted(pattern_hits):
        print(f"  {ln:>4}  pattern: {name}: {snippet!r} -> {fix}")
    dashes = raw.count("—")
    dash_rate = dashes * 10000 / nwords
    base_dash = base.get("em_dash_per_10k") if base else None
    note = f" (baseline {base_dash})" if base_dash is not None else ""
    print(f"  em dashes: {dashes} ({dash_rate:.1f} per 10k){note}")
    lengths = [len(TOKEN.findall(s)) for s in re.split(r"(?<=[.!?])\s+", text) if TOKEN.search(s)]
    if len(lengths) >= 10:
        mean = sum(lengths) / len(lengths)
        sd = (sum((x - mean) ** 2 for x in lengths) / len(lengths)) ** 0.5
        flag = "  <- uniform rhythm, vary sentence length" if sd < 0.4 * mean else ""
        print(f"  sentence length: mean {mean:.1f}, sd {sd:.1f}{flag}")
    return len(hits) + len(pattern_hits)


def main(argv):
    if len(argv) >= 2 and argv[0] == "--calibrate":
        calibrate(argv[1])
        return 0
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else None
    for p in argv:
        report(p, base)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

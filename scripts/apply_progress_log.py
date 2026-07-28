#!/usr/bin/env python3
"""Splice new Progress Log entries into index.html's PROGRESS_LOG array.

Input is the JSON emitted by acp's `scripts/gen_progress_log.py` — commits that opted
into publication with a `Matrix-Note:` trailer. Reads stdin or a file:

    python scripts/apply_progress_log.py entries.json
    gh api ... | python scripts/apply_progress_log.py -

Why splice a marker-delimited block rather than have the page fetch a JSON file: this
repo's whole design is a single self-contained index.html with no build step (see
CLAUDE.md). A fetch() would break both that and opening the file over file://.

PREPEND-ONLY and idempotent. An entry whose `hash` already appears in the array is
skipped, so re-running on an overlapping range is safe and hand-edits to existing
entries are never clobbered. New entries go on top, matching the array's documented
newest-first order.

This writes ONLY the PROGRESS_LOG block. It never touches ROWS.a/ROWS.r — those are
capability claims that ground rule 1 requires a human to verify against shipped acp
code, and a tier is a judgment (ground rules 2 and 3), not a changelog fact.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

BEGIN = "// <<<PROGRESS_LOG:BEGIN"
END = "// <<<PROGRESS_LOG:END>>>"

FORMATS = ("docx", "xlsx", "pptx", "pdf")
REQUIRED = ("date", "hash", "title", "scs", "formats", "summary")


def _js_str(s: str) -> str:
    """A JS double-quoted literal. The existing entries contain curly quotes and
    apostrophes verbatim, so only the characters that would actually break the literal
    are escaped — keeping the diff readable and the file's existing style intact."""
    out = s.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + out.replace("\n", " ") + '"'


def render(e: dict) -> str:
    """One entry, formatted to match the hand-authored entries around it."""
    pr = str(e["pr"]) if e.get("pr") else "null"
    repo = f',repo:{_js_str(e["repo"])}' if e.get("repo") else ""
    scs = ",".join(_js_str(s) for s in e["scs"])
    fmts = ",".join(_js_str(f) for f in e["formats"])
    # `points` is optional: a commit describing one change emits no bullets and the entry keeps
    # the exact shape it had before the field existed. One bullet per line, since these are the
    # part a human is most likely to come back and reword.
    points = ""
    if e.get("points"):
        rendered = ",\n".join(
            "  {" + (f'label:{_js_str(p["label"])},' if p.get("label") else "")
            + f'text:{_js_str(p["text"])}}}'
            for p in e["points"])
        points = f',\n points:[\n{rendered}]'
    # `time` is optional: the entries written before timestamps existed have none, and render
    # without one rather than being back-filled with a fabricated hour.
    when = f',time:{_js_str(e["time"])}' if e.get("time") else ""
    return (f'{{date:{_js_str(e["date"])}{when},hash:{_js_str(e["hash"])},pr:{pr}{repo},\n'
            f' title:{_js_str(e["title"])},\n'
            f' scs:[{scs}],formats:[{fmts}],\n'
            f' summary:{_js_str(e["summary"])}{points}}},')


def validate(entries: list[dict]) -> None:
    for e in entries:
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            raise SystemExit(f"entry {e.get('hash', '?')}: missing {missing}")
        bad = [f for f in e["formats"] if f not in FORMATS]
        if bad:
            raise SystemExit(f"entry {e['hash']}: unknown format(s) {bad}")
        for i, p in enumerate(e.get("points") or []):
            if not isinstance(p, dict) or not (p.get("text") or "").strip():
                raise SystemExit(f"entry {e['hash']}: points[{i}] has no text")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]):
            raise SystemExit(f"entry {e['hash']}: date must be YYYY-MM-DD")


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = sys.stdin.read() if src == "-" else Path(src).read_text()
    entries = json.loads(raw)
    if not entries:
        print("no new entries — nothing to splice")
        return 0
    validate(entries)

    html = INDEX.read_text()
    i, j = html.find(BEGIN), html.find(END)
    if i < 0 or j < 0:
        raise SystemExit(f"{INDEX.name}: PROGRESS_LOG markers not found — someone "
                         f"removed them; restore the BEGIN/END comments first.")
    block = html[i:j]

    open_at = block.find("[")
    fresh = [e for e in entries if f'hash:"{e["hash"]}"' not in block]
    if not fresh:
        print(f"all {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} already "
              f"present — no change")
        return 0

    added = "\n".join(render(e) for e in fresh)
    rest = block[open_at + 1:].lstrip("\n")
    new_block = block[:open_at + 1] + "\n" + added + "\n" + rest
    INDEX.write_text(html[:i] + new_block + html[j:])
    for e in fresh:
        print(f"+ {e['date']}  {e['hash']}  {', '.join(e['scs'])}")
    print(f"spliced {len(fresh)} entr{'y' if len(fresh) == 1 else 'ies'} into "
          f"{INDEX.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

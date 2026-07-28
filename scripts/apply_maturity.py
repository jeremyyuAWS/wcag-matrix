#!/usr/bin/env python3
"""Splice acp's detection-maturity grid into index.html's MATURITY block.

Input is the `maturity` object from acp's `scripts/gen_matrix_coverage.py` — one entry per
(criterion, format) pair that has been migrated to acp's capability registry, carrying the
coverage level its detector honestly reaches and why.

    python scripts/apply_maturity.py coverage.json

WHY THIS IS A FULL REPLACE, NOT A PREPEND. `apply_progress_log.py` is deliberately
prepend-only: a log entry is a dated historical fact, so re-running must never rewrite one.
Maturity is the opposite — it is a *current-state* snapshot of what acp's code declares today,
and the entire point is that it changes when a detector improves. A pair that moves from
HEURISTIC to FULL must overwrite, and a pair whose registration is removed must disappear
rather than linger as a stale claim. So the block is regenerated wholesale every run.

That also makes hand-editing this block pointless: the next sync overwrites it. Coverage is
declared in acp, beside the detector it describes, which is the only place it can't drift from.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

BEGIN = "// <<<MATURITY:BEGIN"
END = "// <<<MATURITY:END>>>"

LEVELS = ("unsupported", "declared", "heuristic", "partial", "full")
FORMATS = ("docx", "xlsx", "pptx", "pdf")


def _js(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def render(maturity: dict) -> str:
    """`{sc: {fmt: {coverage, confidence, reason}}}` as a compact JS literal, SC-sorted so the
    diff between two runs shows only what actually changed."""
    if not maturity:
        return "const MATURITY={};"
    rows = []
    for sc in sorted(maturity, key=lambda s: [int(p) for p in s.split(".")]):
        cells = []
        for fmt in FORMATS:
            cell = maturity[sc].get(fmt)
            if not cell:
                continue
            cells.append(f'{fmt}:{{c:{_js(cell["coverage"])},'
                         f'conf:{_js(cell.get("confidence", ""))},'
                         f'why:{_js(cell.get("reason", ""))}}}')
        if cells:
            rows.append(f'"{sc}":{{' + ",".join(cells) + "}")
    return "const MATURITY={\n " + ",\n ".join(rows) + "};"


def validate(maturity: dict) -> None:
    for sc, fmts in maturity.items():
        for fmt, cell in fmts.items():
            if fmt not in FORMATS:
                raise SystemExit(f"{sc}: unknown format {fmt!r}")
            if cell.get("coverage") not in LEVELS:
                raise SystemExit(
                    f"{sc}/{fmt}: unknown coverage {cell.get('coverage')!r} — acp added a level "
                    f"this repo doesn't render. Add it to LEVELS here and to the legend in "
                    f"index.html before syncing, or the cell shows up unstyled.")


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = sys.stdin.read() if src == "-" else Path(src).read_text()
    cov = json.loads(raw)
    maturity = cov.get("maturity", {})
    validate(maturity)

    html = INDEX.read_text()
    i, j = html.find(BEGIN), html.find(END)
    if i < 0 or j < 0:
        raise SystemExit(f"{INDEX.name}: MATURITY markers not found — restore the BEGIN/END "
                         f"comments first.")
    # Keep the WHOLE BEGIN comment, which runs to the closing `>>>` several lines down — not
    # just its first line. Taking one line silently ate the rest of the explanation on every
    # sync, deleting the documentation that tells the next reader not to hand-edit the block.
    close = html.index(">>>", i)
    head = html[i:html.index("\n", close) + 1]
    new = head + render(maturity) + "\n"
    if html[i:j] == new:
        print("maturity unchanged")
        return 0
    INDEX.write_text(html[:i] + new + html[j:])
    pairs = sum(len(f) for f in maturity.values())
    print(f"spliced maturity for {pairs} (criterion, format) pair(s) "
          f"across {len(maturity)} criteria")
    return 0


if __name__ == "__main__":
    sys.exit(main())

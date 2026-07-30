#!/usr/bin/env python3
"""Every UPGRADE note must be about the cell it renders on.

UPGRADE was once one string per criterion, rendered unchanged on all four format columns. Fifteen
of the twenty entries named a specific format in their prose, so three cells out of four showed
claims about other formats: 1.3.2's DOCX cell read "XLSX: no safe mechanical path exists for
unmerging by design. PPTX/PDF are already at their assess ceiling" — three statements, none of
them about DOCX. On a page whose entire purpose is accurate per-cell capability claims, that is
the worst place to be approximate.

The shape is now {sc: {fmt: text, "*": text}}. This guard keeps it honest:

  1. A bare string entry may not name a format. That is exactly the old bug — shared text making
     format-specific claims. Convert it to per-format keys, or to {"*": ...} if it really is
     criterion-wide (an explicit declaration beats an implicit default).
  2. A per-format note may not LEAD with a different format's name. Referring to another format
     mid-sentence is legitimate and common ("ported the detector already used by docx/pptx/pdf");
     opening with "XLSX:" on the PDF cell is the pattern that was wrong.

Run: python3 scripts/check_upgrade_scope.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
FORMATS = ("docx", "xlsx", "pptx", "pdf")


def load_upgrade() -> dict:
    """Read UPGRADE out of index.html by evaluating just that literal in node.

    Parsed rather than regex-scraped: the values contain commas, colons, braces and em dashes,
    and a regex that got it subtly wrong would make this guard lie in the same way the data did.
    """
    src = HTML.read_text(encoding="utf-8")
    m = re.search(r'const UPGRADE=\{.*?\n"4\.1\.2":\{.*?\}\};', src, re.S)
    if not m:
        sys.exit("check_upgrade_scope: could not find the UPGRADE block in index.html")
    literal = re.sub(r";\s*$", "", m.group(0).replace("const UPGRADE=", "", 1))
    out = subprocess.run(
        ["node", "-e", "process.stdout.write(JSON.stringify(eval('(' + process.argv[1] + ')')))", literal],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit(f"check_upgrade_scope: UPGRADE is not valid JS\n{out.stderr}")
    return json.loads(out.stdout)


def main() -> int:
    upgrade = load_upgrade()
    problems: list[str] = []
    cells = 0

    for sc, val in upgrade.items():
        if isinstance(val, str):
            named = [f for f in FORMATS if f.upper() in val or f in val.split()]
            if named:
                problems.append(
                    f"{sc}: is a single shared string but names {'/'.join(named)} — it renders "
                    f"on all four format cells, so three of them get claims about a format they "
                    f"are not. Split it per format, or use {{\"*\": ...}} if it is criterion-wide."
                )
            cells += 1
            continue

        for key, text in val.items():
            cells += 1
            if key != "*" and key not in FORMATS:
                problems.append(f"{sc}: unknown key {key!r} (expected one of {FORMATS} or '*')")
                continue
            if key == "*":
                continue
            # Only a LEADING mention is a scope error; a mid-sentence cross-reference is fine.
            lead = text[:40].lower()
            for other in FORMATS:
                if other == key:
                    continue
                if re.match(rf"^{other}\b\s*[:\-—]", lead):
                    problems.append(
                        f"{sc}/{key}: the note opens with '{other.upper()}' — it is filed under "
                        f"{key} but reads as being about {other}."
                    )

    print(f"UPGRADE: {len(upgrade)} criteria, {cells} per-cell notes")
    if problems:
        print(f"\n{len(problems)} scope problem(s):\n")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("every note is scoped to the cell it renders on")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

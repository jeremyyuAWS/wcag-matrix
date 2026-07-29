#!/usr/bin/env python3
"""Fail when a capability cell changes without a Progress Log entry declaring it.

The grid and the log are two claims about the same thing, and only one of them was guarded.
`gen_progress_log.py --check` (in acp) catches rule CODE changing without a note. Nothing
caught the matrix's own cells changing without one — and that is the direction that actually
drifted: three PRs in one day moved capability claims, and only one of them said so in the log.
A reader comparing "what the grid says" against "when did that change" got no answer.

The rule is narrow and mechanical:

    if a commit changes ROWS[sc].a[fmt] or ROWS[sc].r[fmt],
    the same diff must ADD a PROGRESS_LOG entry whose `scs` includes that sc

Not "an entry mentioning it exists somewhere" — a NEW one, added by this diff. An old entry
about 1.4.3 does not explain why 1.4.3 changed again today, and accepting it would make the
guard pass forever after the first entry per criterion.

Deliberately silent about level moves it cannot judge. It does not check that the entry is
ACCURATE — no script can — only that a human was made to write one. That is the same posture
as the trailer guard in acp: a prompt to say what changed, not an attempt to infer it.

Usage:
    python scripts/check_log_covers_grid.py                 # origin/main..HEAD, or HEAD~1..HEAD
    python scripts/check_log_covers_grid.py --base <ref>
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

FORMATS = ("docx", "xlsx", "pptx", "pdf")
_ROW = re.compile(r'^\{sc:"(\d+\.\d+\.\d+)".*?\ba:\{([^}]*)\}.*?\br:\{([^}]*)\}', re.M)
_CELL = re.compile(r'(\w+):"([^"]*)"')
_ENTRY = re.compile(r'\{date:"[^"]*".*?hash:"([^"]*)".*?scs:\[([^\]]*)\]', re.S)
_SC = re.compile(r'"(\d+\.\d+\.\d+)"')


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def _at(ref: str) -> str:
    out = subprocess.run(["git", "show", f"{ref}:index.html"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"cannot read index.html at {ref}: {out.stderr.strip()}")
    return out.stdout


def grid(html: str) -> dict[tuple[str, str, str], str]:
    """(sc, axis, fmt) -> level, for every cell in ROWS."""
    cells: dict[tuple[str, str, str], str] = {}
    for sc, a, r in _ROW.findall(html):
        for axis, blob in (("a", a), ("r", r)):
            for fmt, lvl in _CELL.findall(blob):
                if fmt in FORMATS:
                    cells[(sc, axis, fmt)] = lvl
    return cells


def entries(html: str) -> dict[str, set[str]]:
    """PROGRESS_LOG hash -> the SCs it declares."""
    i, j = html.find("// <<<PROGRESS_LOG:BEGIN"), html.find("// <<<PROGRESS_LOG:END>>>")
    if i < 0 or j < 0:
        raise SystemExit("index.html: PROGRESS_LOG markers not found")
    return {h: set(_SC.findall(scs)) for h, scs in _ENTRY.findall(html[i:j])}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", help="ref to compare against")
    args = ap.parse_args()

    base = args.base
    if not base:
        for candidate in ("origin/main", "HEAD~1"):
            if _git("rev-parse", "--verify", "--quiet", candidate).strip():
                base = candidate
                break
    if not base:
        print("no base ref to compare against — nothing to check")
        return 0

    before, after = _at(base), _at("HEAD")
    g0, g1 = grid(before), grid(after)

    changed: dict[str, list[str]] = {}
    for key, new in sorted(g1.items()):
        old = g0.get(key)
        if old is not None and old != new:
            sc, axis, fmt = key
            changed.setdefault(sc, []).append(
                f"{fmt} {'assessment' if axis == 'a' else 'remediation'} {old}->{new}")
    if not changed:
        print(f"no capability cells changed vs {base} — nothing for the log to cover")
        return 0

    fresh = set(entries(after)) - set(entries(before))
    declared: set[str] = set()
    for h in fresh:
        declared |= entries(after)[h]

    uncovered = {sc: moves for sc, moves in changed.items() if sc not in declared}
    covered = len(changed) - len(uncovered)
    if not uncovered:
        print(f"log covers the grid — {len(changed)} criterion(s) changed vs {base}, "
              f"all declared by {len(fresh)} new Progress Log entr"
              f"{'y' if len(fresh) == 1 else 'ies'}")
        return 0

    print(f"{len(uncovered)} criterion(s) changed capability with no Progress Log entry "
          f"declaring them (vs {base}):\n", file=sys.stderr)
    for sc, moves in sorted(uncovered.items()):
        print(f"  {sc}", file=sys.stderr)
        for m in moves:
            print(f"      {m}", file=sys.stderr)
    if covered:
        print(f"\n({covered} other changed criterion(s) ARE covered.)", file=sys.stderr)
    print("\nThe grid now claims something it did not claim before, and the log does not say\n"
          "when or why. Add a PROGRESS_LOG entry listing these SCs in its `scs` — either by\n"
          "hand or via scripts/apply_progress_log.py — then re-run.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

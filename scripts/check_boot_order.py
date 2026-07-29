#!/usr/bin/env python3
"""Fail when a function that runs at page load reads a `const`/`let` declared below it.

This guards ONE bug, which has now shipped three times in this file:

    function cellTip(...){ ... COST_ASSUMPTIONS.humanRatePerHour ... }
    buildTable();                       // <- calls cellTip, at load
    const COST_ASSUMPTIONS = {...};     // <- declared 200 lines further down

`const` and `let` hoist but stay in the temporal dead zone until their declaration runs,
so this throws `Cannot access 'X' before initialization` — at load, before any of the
20 rows render. The page goes blank-bodied and the FIRST failing statement aborts the
whole script, so the symptom is never local to the mistake. Twice it was found only by
opening the page and noticing the table was gone; `node --check` cannot see it, because
the file is syntactically perfect.

The rule enforced is narrow on purpose:

    a top-level `const`/`let` declared AFTER the first top-level call
    must not be referenced by any function reachable from a boot call

Not "declare everything first". Drawer state (`CURRENT_CELL`), the data blocks spliced
in by the sync scripts (`MATURITY`, `PROGRESS_LOG`), and anything else only touched by a
click handler are all legitimately declared late, and this leaves them alone. Only the
boot-reachable subset matters, because only those run before the declaration does.

Reachability comes from a crude call graph, with two deliberate choices about strings:

  * quoted strings are dropped entirely — `"renderDrawer(...)"` in an onclick attribute
    is not a call that happens now, and treating it as one would flag every piece of
    drawer state in the file;
  * inside template literals only the `${...}` interpolations are kept — those DO run
    immediately, so a const read through one is a real TDZ hazard, while the surrounding
    HTML text (which is where the onclick attributes live) is not.

Usage:
    python scripts/check_boot_order.py            # exits 1 on a violation
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

_FUNC = re.compile(r"^function\s+([A-Za-z_$][\w$]*)\s*\(", re.M)
_DECL = re.compile(r"^(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=", re.M)
_CALL = re.compile(r"^([A-Za-z_$][\w$]*)\s*\(")
_IDENT = re.compile(r"[A-Za-z_$][\w$]*")


def _scan_code(src: str, i: int, n: int, out: list, until_close: bool = False) -> int:
    """Copy code through, dropping comments and string bodies. Returns the next index.

    `until_close` is set when scanning the inside of a `${...}`: it stops at the brace that
    closes the interpolation while letting object literals nest freely.
    """
    depth = 0
    while i < n:
        c = src[i]
        if c == "/" and src[i + 1:i + 2] == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if c == "/" and src[i + 1:i + 2] == "*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * src.count("\n", i, j))
            i = j
            continue
        if c in "'\"":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            j += 1
            out.append('""')                       # a value, so `x = "s"` still parses
            out.append("\n" * src.count("\n", i, j))
            i = j
            continue
        if c == "`":
            i = _scan_template(src, i + 1, n, out)
            continue
        if until_close:
            if c == "{":
                depth += 1
            elif c == "}":
                if depth == 0:
                    return i + 1
                depth -= 1
        out.append(c)
        i += 1
    return i


def _scan_template(src: str, i: int, n: int, out: list) -> int:
    """Inside a template literal (past the opening backtick). Returns the next index.

    Only `${...}` interpolations are kept — those run immediately, so a const read through
    one is a real TDZ hazard. The literal text between them is dropped, which is the whole
    point: that is where `onclick="renderDrawer(...)"` lives, and those fire on click, long
    after every declaration has run.

    Interpolations are scanned by _scan_code, so a template nested inside one is handled
    like any other. That mutual recursion is load-bearing rather than tidiness: this file
    really does contain ``${cond ? `  →  ${X}` : ""}``, and a flat scanner loses brace
    sync on it and silently truncates the enclosing function's body — which is exactly how
    an earlier version of this check reported a clean bill of health on a file that had
    the bug.
    """
    while i < n:
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == "`":
            return i + 1
        if src[i] == "$" and src[i + 1:i + 2] == "{":
            out.append(" ")
            i = _scan_code(src, i + 2, n, out, until_close=True)
            out.append(" ")
            continue
        if src[i] == "\n":
            out.append("\n")                       # keep line numbering intact
        i += 1
    return i


def strip_noise(src: str) -> str:
    """Comments and string bodies removed, `${...}` interpolations kept.

    LINE-PRESERVING: every removed span emits its own newlines back, so an offset here can
    be reported against the real file.
    """
    out: list = []
    _scan_code(src, 0, len(src), out)
    return "".join(out)


def function_bodies(src: str) -> dict[str, str]:
    """name -> body text, for top-level `function name(){}` declarations."""
    bodies = {}
    for m in _FUNC.finditer(src):
        start = src.find("{", m.end() - 1)
        if start < 0:
            continue
        depth, i = 0, start
        while i < len(src):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        bodies[m.group(1)] = src[start:i]
    return bodies


def main() -> int:
    html = INDEX.read_text()
    m = re.search(r"<script>([\s\S]*?)</script>", html)
    if not m:
        raise SystemExit(f"{INDEX.name}: no <script> block found")
    raw = m.group(1)
    line0 = html[: m.start(1)].count("\n")          # so reports use file line numbers
    src = strip_noise(raw)
    lines = src.split("\n")

    boot: list[tuple[int, str]] = []
    first_call = None
    for i, line in enumerate(lines):
        c = _CALL.match(line)
        if c and c.group(1) not in ("if", "for", "while", "switch", "catch", "function",
                                    "return", "typeof"):
            if first_call is None:
                first_call = i
            boot.append((i, c.group(1)))
    if first_call is None:
        print("no top-level calls — nothing runs at load; nothing to check")
        return 0

    # Both offsets are into `src`, which strip_noise keeps line-for-line with `raw`.
    late = {d.group(1): src[: d.start()].count("\n")
            for d in _DECL.finditer(src)
            if src[: d.start()].count("\n") > first_call}
    if not late:
        print("boot order OK — every top-level binding is declared before the first call")
        return 0

    bodies = function_bodies(src)

    reachable, stack = set(), [name for _, name in boot if name in bodies]
    while stack:
        fn = stack.pop()
        if fn in reachable:
            continue
        reachable.add(fn)
        stack += [w for w in _IDENT.findall(bodies[fn]) if w in bodies]

    bad = []
    for fn in sorted(reachable):
        for word in set(_IDENT.findall(bodies[fn])):
            if word in late:
                bad.append((fn, word, late[word]))

    if not bad:
        print(f"boot order OK — {len(late)} binding(s) declared after the first call "
              f"({', '.join(sorted(late))}), none reachable from the {len(reachable)} "
              f"function(s) that run at load")
        return 0

    for fn, word, decl_line in sorted(bad, key=lambda b: b[2]):
        print(f"{INDEX.name}:{line0 + decl_line + 1}: '{word}' is read by {fn}(), which "
              f"runs at load, but is declared here — below it.", file=sys.stderr)
    print(f"\nThis throws \"Cannot access '{bad[0][1]}' before initialization\" at load and "
          f"blanks the page.\nMove the declaration above the first top-level call.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

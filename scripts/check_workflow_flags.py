#!/usr/bin/env python3
"""Fail when a workflow calls a scripts/*.py flag that script does not define.

The workflows drive these scripts by command line, and nothing checked that the two agreed.
That is a silent-failure shape, not a loud one: every invocation in grid-drift.yml and
progress-log.yml is followed by `|| true` — deliberately, so a drift report or a missing
dispatch cannot fail a push — which means argparse's "unrecognized arguments" exit lands in a
step that shrugs and moves on. The job goes green, and whatever that step produced is empty.

It has already happened in the strings next door. grid-drift.yml sliced the lag section out of
`--markdown` with `awk '/^## Cells claiming LESS/{f=1} f'`, so a heading in check_grid_drift.py
was load-bearing for a pattern in the workflow with nothing asserting it; rewording the heading
would have emptied the job summary and said nothing. That coupling was removed by giving the
script a `--lag-markdown` flag — which replaces a string dependency with a CLI dependency, and
this is what guards the replacement.

Deliberately narrow. It checks that every long flag passed to a scripts/*.py in a workflow is
one that script's argparse defines. It does not check semantics — that `--apply` still applies,
or that the summary is worth reading. A script's own tests are the place for that; this only
catches the class of break where the caller and the callee stop speaking the same language.

Usage:
    python scripts/check_workflow_flags.py
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
SCRIPTS = ROOT / "scripts"

# `python3 scripts/foo.py ... --flag ...` up to the end of the line. Continuations (`\` at EOL)
# are joined first, so a wrapped invocation is read whole rather than truncated at the break —
# the wrapped --lag-markdown call is exactly that shape.
INVOKE = re.compile(r"python3?\s+(scripts/[A-Za-z0-9_]+\.py)([^\n|>&;]*)")
LONG_FLAG = re.compile(r"(--[A-Za-z][A-Za-z0-9-]*)")


def declared_flags(script: Path) -> set[str]:
    """Every long option the script's argparse defines, read from the AST.

    Parsed rather than executed: importing a script to ask it about itself runs its module body,
    and these scripts read index.html at import time.
    """
    tree = ast.parse(script.read_text())
    flags: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Attribute) and fn.attr == "add_argument"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                    and arg.value.startswith("--"):
                flags.add(arg.value)
    return flags


def main() -> int:
    problems: list[str] = []
    skipped: list[str] = []
    checked = 0
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text().replace("\\\n", " ")     # join line continuations
        for script_rel, tail in INVOKE.findall(text):
            script = ROOT / script_rel
            if not script.exists():
                # Not ours. grid-drift.yml and progress-log.yml both clone acp and run ITS
                # generators with `working-directory: /tmp/acp`, so `scripts/gen_*.py` there is
                # acp's file and acp's own CI checks it. Counted and reported rather than passed
                # over, so this guard cannot quietly check nothing and still print OK.
                skipped.append(f"{wf.name}: {script_rel} (not in this repo — assumed acp's)")
                continue
            declared = declared_flags(script)
            for flag in LONG_FLAG.findall(tail):
                checked += 1
                if flag not in declared:
                    problems.append(
                        f"{wf.name}: `{script_rel} {flag}` — that script defines "
                        f"{sorted(declared) or 'no long flags'}")
    if problems:
        print(f"{len(problems)} workflow/script flag mismatch(es):\n", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print("\nEvery workflow invocation is followed by `|| true`, so argparse's exit would "
              "be swallowed and the step would produce nothing, greenly.", file=sys.stderr)
        return 1
    if checked == 0:
        # A guard that checked nothing and reported OK is the exact failure this file exists
        # to catch, so it refuses to be that guard.
        print("checked ZERO flags — the invocation regex has stopped matching, so this guard "
              "is green for the wrong reason.", file=sys.stderr)
        return 1
    print(f"workflow flags OK — {checked} flag use(s) across "
          f"{len(list(WORKFLOWS.glob('*.yml')))} workflow(s), all declared")
    for note in skipped:
        print(f"  skipped: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

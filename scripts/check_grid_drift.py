#!/usr/bin/env python3
"""Compare the grid's claimed tiers against acp's code-derived capability ceiling.

Input is the JSON emitted by acp's `scripts/gen_matrix_coverage.py`, which reads the
round-trip-proven lane table (api/remediation_capability.py), the write-back applier surface
(api/handlers.py), the model-backed proposers (api/proposals.py) and the detector inventory,
and reports the STRONGEST tier each of the 80 cells could honestly claim.

    python scripts/check_grid_drift.py coverage.json            # report, exit 1 on drift
    python scripts/check_grid_drift.py coverage.json --apply    # also rewrite the cells
    python scripts/check_grid_drift.py coverage.json --markdown # PR-body report

ONLY OVER-CLAIMS ARE DRIFT. UNDER-CLAIMS ARE REPORTED.
------------------------------------------------------
A cell may always claim LESS than the code supports. Ground rule 3's honest-partial rule makes
a deliberate downgrade an editorial act — "XLSX contrast skips theme colours, so call it Guided
even though the lane says auto" is the matrix working correctly, not a defect. So an over-claim
is DRIFT: rewritten to the ceiling and proposed in a PR. An under-claim is not, and is never
rewritten by this script.

But "not a defect" was being read as "not worth mentioning", and those are different. An
under-claiming cell means shipped capability is invisible in the coverage percentages, with
nothing anywhere reporting that it is waiting to be claimed. On 2026-08-07 six cells lagged
through three acp merges — 1.3.3 and 3.1.2 write-backs and a docx 4.1.2 applier — and the
headline coverage figure did not move all day. They were found by a person going looking,
which is exactly the manual check the rest of this file exists to replace.

So under-claims are now LISTED — in the report, in the PR body, and as job annotations — and
still never applied. The judgment stays with a human; only the silence goes away.

WHY THIS OPENS A PR RATHER THAN PUSHING
---------------------------------------
Ground rule 1 says a tier is claimed only against verified shipped code, and ground rules 2-3
make a tier a judgment. A ceiling is not a judgment — it is a bound — so this script proposes
the bound as the new value and stops there. `.github/workflows/grid-drift.yml` puts that
proposal in a pull request for a human to accept, adjust downward, or reject with a note. The
grid is never edited by a machine alone; it is also never left silently over-claiming.

Cells whose claim is at or below the ceiling are left completely untouched, including their
drawer prose — this script only ever rewrites the `a:{...}` / `r:{...}` tier literals.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

FORMATS = ("docx", "xlsx", "pptx", "pdf")

# Weakest -> strongest claim. Mirrors gen_matrix_coverage's A_TIERS/R_TIERS; the coverage JSON
# carries its own copy and _rank_maps() asserts they agree, so a vocabulary change on either
# side is a loud failure rather than a silently wrong comparison.
A_TIERS = ("NA", "H", "Q", "C")
R_TIERS = ("NA", "N", "M", "AI", "AP", "AC", "A")

# ── Two vocabularies, and the bridge between them ────────────────────────────────────
# acp's gen_matrix_coverage.py still emits the ORIGINAL tier codes (C/Q/H, A/AP/AC/AI/M/N).
# The grid moved to the two-axis model (A4/A3/A2, R4/R3/R2/R1) and index.html carries the same
# LEGACY_A/LEGACY_R translation this mirrors. Comparing them directly is what broke: every run
# died on `unknown a tier 'A4'`, so the drift guard — the thing that catches the grid claiming
# more than the code supports — has been dead since the model changed, failing loudly into a
# workflow nobody was reading.
#
# Translation happens on READ, so ranks, labels and --apply all speak the grid's vocabulary.
# That last one matters most: apply() writes the ceiling straight back into ROWS, so an
# untranslated ceiling would rewrite live cells as "Q" and "AI" and corrupt the grid it exists
# to protect.
#
# Both maps are monotonic — H<Q<C maps to A2<A3<A4, and N<M<{AI,AC}<{AP,A} maps to
# R1<R2<R3<R4 — so ordering survives, which is all a rank comparison needs. The many-to-one
# pairs (AP and A both R4; AI and AC both R3) lose a distinction the grid does not draw.
FROM_LEGACY_A = {"C": "A4", "Q": "A3", "H": "A2", "NA": "NA"}
FROM_LEGACY_R = {"A": "R4", "AP": "R4", "AC": "R3", "AI": "R3",
                 "M": "R2", "N": "R1", "NA": "NA"}

# The grid's own vocabulary, weakest -> strongest. Ranks are computed in THIS one.
GRID_A_TIERS = ("NA", "A2", "A3", "A4")
GRID_R_TIERS = ("NA", "R1", "R2", "R3", "R4")

# Human-readable, matching index.html's AL/RL maps.
A_LABEL = {"A4": "Fully Assessed", "A3": "Potential Issue",
           "A2": "Human Assessment Required", "NA": "Not applicable"}
R_LABEL = {"R4": "Automatically Fixed", "R3": "AI Generated Fix",
           "R2": "Guided Remediation", "R1": "No Remediation", "NA": "Not applicable"}

# One ROWS entry's header. `a:` and `r:` are flat maps of short quoted codes and contain no
# nested braces, so a brace-free inner match is exact — and it stops well before the drawer
# prose, which this script must never touch.
ROW_RE = re.compile(
    r'\{sc:"(?P<sc>[\d.]+)",name:"(?P<name>(?:[^"\\]|\\.)*)",lvl:"(?P<lvl>[^"]*)",'
    r'flag:(?P<flag>true|false),a:\{(?P<a>[^{}]*)\},r:\{(?P<r>[^{}]*)\}')

CELL_RE = re.compile(r'(\w+):"([^"]*)"')


def parse_rows(html: str) -> list[dict]:
    """Every grid row's claimed tiers, with the span of its a:/r: literals for rewriting."""
    rows = []
    for m in ROW_RE.finditer(html):
        rows.append({
            "sc": m.group("sc"),
            "name": m.group("name"),
            "a": dict(CELL_RE.findall(m.group("a"))),
            "r": dict(CELL_RE.findall(m.group("r"))),
            "a_span": m.span("a"),
            "r_span": m.span("r"),
        })
    if not rows:
        raise SystemExit(f"{INDEX.name}: no ROWS entries matched — the row shape changed; "
                         f"update ROW_RE before trusting this check.")
    return rows


def _rank_maps(cov: dict) -> tuple[dict[str, int], dict[str, int]]:
    a_tiers = tuple(cov.get("a_tiers") or A_TIERS)
    r_tiers = tuple(cov.get("r_tiers") or R_TIERS)
    if a_tiers != A_TIERS or r_tiers != R_TIERS:
        raise SystemExit(
            "tier vocabulary disagrees with acp's gen_matrix_coverage.py:\n"
            f"  here  a={A_TIERS} r={R_TIERS}\n"
            f"  there a={a_tiers} r={r_tiers}\n"
            "Reconcile the two lists — a rank comparison across different vocabularies is "
            "meaningless, so this refuses to guess.")
    # Ranks are in the GRID's vocabulary; acp's tiers are translated into it before comparison.
    return ({t: i for i, t in enumerate(GRID_A_TIERS)},
            {t: i for i, t in enumerate(GRID_R_TIERS)})


def find_drift(rows: list[dict], cov: dict) -> list[dict]:
    """Cells claiming a stronger tier than acp's code supports."""
    a_rank, r_rank = _rank_maps(cov)
    cells = cov["cells"]
    out = []
    for row in rows:
        derived = cells.get(row["sc"])
        if derived is None:
            # A row acp has no coverage entry for. Not drift — gen_matrix_coverage's TRACKED_SCS
            # is asserted equal to gen_progress_log's, so this means the matrix grew a row first.
            print(f"note: {row['sc']} has no acp coverage entry — skipped", file=sys.stderr)
            continue
        for fmt in FORMATS:
            for axis, rank, label in (("a", a_rank, A_LABEL), ("r", r_rank, R_LABEL)):
                claimed = row[axis].get(fmt)
                raw = derived[fmt]["ceiling_a" if axis == "a" else "ceiling_r"]
                if claimed is None or raw is None:
                    continue
                # acp speaks the legacy vocabulary; translate before ranking or writing back.
                bridge = FROM_LEGACY_A if axis == "a" else FROM_LEGACY_R
                if raw not in bridge:
                    raise SystemExit(
                        f"{row['sc']}/{fmt}: acp emitted {axis} ceiling {raw!r}, which has no "
                        f"mapping into the grid's vocabulary. Add it to "
                        f"{'FROM_LEGACY_A' if axis == 'a' else 'FROM_LEGACY_R'} — refusing to "
                        f"guess, because a wrong mapping silently rewrites live cells.")
                ceiling = bridge[raw]
                if claimed not in rank:
                    raise SystemExit(
                        f"{row['sc']}/{fmt}: unknown {axis} tier {claimed!r} in the grid. "
                        f"Expected one of {GRID_A_TIERS if axis == 'a' else GRID_R_TIERS}.")
                if rank[claimed] > rank[ceiling]:
                    out.append({
                        "sc": row["sc"], "name": row["name"], "fmt": fmt, "axis": axis,
                        "claimed": claimed, "ceiling": ceiling,
                        "claimed_label": label.get(claimed, claimed),
                        "ceiling_label": label.get(ceiling, ceiling),
                        "cell": derived[fmt],
                    })
    return out


def find_lag(rows: list[dict], cov: dict) -> list[dict]:
    """(weaker-tier cells, cells claiming N/A where a detector emits).

    The mirror of find_drift, and deliberately NOT fed to apply(): a downgrade can be a
    considered editorial act, so raising one automatically would overwrite a judgment with a
    bound. This only makes the gap sayable — and it separates the two gaps, because "this tier
    is lower than the code supports" and "this rule is marked inapplicable but something
    detects it" are different claims a reader answers differently.
    """
    a_rank, r_rank = _rank_maps(cov)
    cells = cov["cells"]
    out: list[dict] = []
    na_out: list[dict] = []
    for row in rows:
        derived = cells.get(row["sc"])
        if derived is None:
            continue                      # already noted by find_drift; do not double-report
        for fmt in FORMATS:
            for axis, rank, label in (("a", a_rank, A_LABEL), ("r", r_rank, R_LABEL)):
                claimed = row[axis].get(fmt)
                raw = derived[fmt]["ceiling_a" if axis == "a" else "ceiling_r"]
                if claimed is None or raw is None:
                    continue
                bridge = FROM_LEGACY_A if axis == "a" else FROM_LEGACY_R
                # Unknown vocabulary is find_drift's error to raise, with its full message.
                # Skipping here keeps this function from failing the run on the same fault twice.
                if raw not in bridge or claimed not in rank:
                    continue
                ceiling = bridge[raw]
                if rank[claimed] < rank[ceiling]:
                    # A cell claiming NA is not claiming a weak TIER — it is claiming the rule
                    # cannot be broken in this format at all. That is an applicability judgment,
                    # and acp's ceiling says nothing about applicability: it reports what a
                    # detector could establish IF the rule applied. Ranking NA below A2 and
                    # calling the gap an under-claim is a category error, and a loud one — it
                    # buried the 7 real tier lags under 23 NA rows on the first run.
                    #
                    # Still surfaced, because it is a real question and one that has bitten:
                    # docx 1.3.2 / 1.4.10 / 1.4.12 sat NA on this page while shipped detectors
                    # emitted for them. Just asked separately, as "is this really inapplicable?"
                    # rather than "is this tier too low?".
                    (na_out if claimed == "NA" else out).append({
                        "sc": row["sc"], "name": row["name"], "fmt": fmt, "axis": axis,
                        "claimed": claimed, "ceiling": ceiling,
                        "claimed_label": label.get(claimed, claimed),
                        "ceiling_label": label.get(ceiling, ceiling),
                        "cell": derived[fmt],
                    })
    return out, na_out


def apply(html: str, rows: list[dict], drift: list[dict]) -> str:
    """Rewrite only the drifted tier literals, right-to-left so earlier spans stay valid."""
    by_row = {(d["sc"], d["axis"]): [] for d in drift}
    for d in drift:
        by_row[(d["sc"], d["axis"])].append(d)

    edits = []
    for row in rows:
        for axis in ("a", "r"):
            ds = by_row.get((row["sc"], axis))
            if not ds:
                continue
            new = dict(row[axis])
            for d in ds:
                new[d["fmt"]] = d["ceiling"]
            # Rebuild in the source's own key order so the diff shows only changed values.
            text = ",".join(f'{k}:"{new[k]}"' for k in row[axis])
            edits.append((row[f"{axis}_span"], text))

    for (start, end), text in sorted(edits, key=lambda e: e[0][0], reverse=True):
        html = html[:start] + text + html[end:]
    return html


def why(d: dict) -> str:
    """The reason a cell is over-claiming, in one line.

    A note beats the default: notes describe something specific and surprising (a missing
    applier, a catalog contradiction). When none fired, the cell is simply above its lane, so
    say which lane — "no code backing" would be wrong for a pair acp deliberately calls human.
    """
    if d["cell"]["notes"]:
        return d["cell"]["notes"][0]
    lane = d["cell"]["assessment_lane" if d["axis"] == "a" else "remediation_lane"]
    if lane is None:
        return ("acp does not evaluate this SC for this format, so it can back no automated "
                "claim here")
    return f"acp's round-trip-proven lane for this pair is `{lane}`"


def report_lag(lag: list[dict], na_lag: list[dict]) -> None:
    """Under-claims, on stdout and as GitHub annotations. Never fatal."""
    if na_lag:
        print(f"\n{len(na_lag)} cell(s) are marked N/A on the grid while acp has a detector "
              f"that emits for them — an applicability question, not a tier one:\n")
        for d in na_lag:
            axis = "assessment" if d["axis"] == "a" else "remediation"
            print(f"  {d['sc']} {d['fmt']} {axis}: N/A on the grid, "
                  f"code supports {d['ceiling']} ({d['ceiling_label']})")
    if not lag:
        print("\nno lag — no cell claims a weaker tier than acp's code supports")
        return
    print(f"\n{len(lag)} cell(s) claim LESS than acp's shipped code supports "
          f"(not drift — reported, never rewritten):\n")
    for d in lag:
        axis = "assessment" if d["axis"] == "a" else "remediation"
        line = (f"{d['sc']} {d['fmt']} {axis}: {d['claimed']} ({d['claimed_label']}) "
                f"but code supports {d['ceiling']} ({d['ceiling_label']})")
        print(f"  {line}")
        # ::notice:: so a green run still surfaces it on the summary rather than only in a log
        # nobody opens. The same reason the acp generator annotates its skips.
        print(f"::notice::grid lag — {line}", file=sys.stderr)
    print()


def report(drift: list[dict]) -> None:
    if not drift:
        print("no drift — every cell is at or below acp's code-derived ceiling")
        return
    print(f"{len(drift)} cell(s) claim more than acp's shipped code supports:\n")
    for d in drift:
        axis = "assessment" if d["axis"] == "a" else "remediation"
        print(f"  {d['sc']} {d['fmt']:<5} {axis:<12} "
              f"{d['claimed']} ({d['claimed_label']}) -> {d['ceiling']} ({d['ceiling_label']})")
        print(f"        why: {why(d)}")
        for note in d["cell"]["notes"][1:]:
            print(f"        and: {note}")
        for ev in d["cell"]["evidence"]:
            print(f"        ev:  {ev}")
        print()


def markdown_lag(lag: list[dict], na_lag: list[dict]) -> str:
    """The under-claim section. Informational — nothing in the PR changes these cells."""
    if not lag and not na_lag:
        return ""
    out = [
        "",
        "---",
        "",
        f"## Cells claiming LESS than the code supports ({len(lag)})",
        "",
        "**Nothing in this PR changes these.** An under-claim is not drift — ground rule 3 makes "
        "a deliberate downgrade an editorial act — so they are listed, never rewritten.",
        "",
        "They are listed because the alternative was silence: an under-claiming cell means "
        "shipped capability is missing from the coverage percentages, and until now nothing said "
        "so. Raise one only if the lower tier was not a deliberate call.",
        "",
        "| SC | Format | Axis | Claimed | Code supports |",
        "|---|---|---|---|---|",
    ]
    for d in lag:
        axis = "assessment" if d["axis"] == "a" else "remediation"
        out.append(f"| {d['sc']} | {d['fmt']} | {axis} | `{d['claimed']}` {d['claimed_label']} "
                   f"| `{d['ceiling']}` {d['ceiling_label']} |")
    if na_lag:
        out += [
            "",
            f"### Marked N/A, but a detector emits ({len(na_lag)})",
            "",
            "A different question from the table above: not \"is this tier too low\" but \"is "
            "this rule really inapplicable to this format\". The ceiling cannot settle it — it "
            "reports what a detector could establish IF the rule applied — so these are listed "
            "for a human to confirm, never changed.",
            "",
            "| SC | Format | Axis | Code supports |",
            "|---|---|---|---|",
        ]
        for d in na_lag:
            axis = "assessment" if d["axis"] == "a" else "remediation"
            out.append(f"| {d['sc']} | {d['fmt']} | {axis} | "
                       f"`{d['ceiling']}` {d['ceiling_label']} |")
    return "\n".join(out) + "\n"


def markdown(drift: list[dict]) -> str:
    if not drift:
        return "No drift — every cell is at or below acp's code-derived ceiling.\n"
    out = [
        "## Grid cells claiming more than acp's code supports",
        "",
        f"`scripts/check_grid_drift.py` compared all 80 cells against the ceiling derived by "
        f"acp's `scripts/gen_matrix_coverage.py` and found **{len(drift)}** over-claim(s).",
        "",
        "Only over-claims are rewritten. A cell claiming *less* than the ceiling is left alone "
        "— ground rule 3 makes a deliberate downgrade an editorial act, not a defect — but it is "
        "now LISTED below rather than passed over in silence.",
        "",
        "| SC | Format | Axis | Claimed | Proposed ceiling | Why |",
        "|---|---|---|---|---|---|",
    ]
    for d in drift:
        axis = "assessment" if d["axis"] == "a" else "remediation"
        out.append(f"| {d['sc']} | {d['fmt']} | {axis} | `{d['claimed']}` {d['claimed_label']} "
                   f"| `{d['ceiling']}` {d['ceiling_label']} | {why(d)} |")
    out += ["", "### Evidence", ""]
    for d in drift:
        out.append(f"**{d['sc']} · {d['fmt']} · "
                   f"{'assessment' if d['axis'] == 'a' else 'remediation'}**")
        for ev in d["cell"]["evidence"]:
            out.append(f"- {ev}")
        out.append("")
    out += [
        "---",
        "",
        "**This is a proposal, not a verdict.** The ceiling is a bound derived from code; the "
        "tier is still a human judgment (ground rules 1-3). Accept it, set something lower with "
        "a note in the cell's drawer, or close this PR if the derivation is wrong — and if it "
        "is wrong, fix `gen_matrix_coverage.py` in acp so the next run agrees.",
        "",
        "Drawer prose is untouched: any cell whose tier changes here needs its `ae`/`re` text "
        "re-read by hand before merging.",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("coverage", help="coverage JSON from acp's gen_matrix_coverage.py ('-' for stdin)")
    ap.add_argument("--apply", action="store_true", help="rewrite drifted tiers to the ceiling")
    ap.add_argument("--markdown", action="store_true", help="emit a PR-body report on stdout")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.coverage == "-" else Path(args.coverage).read_text()
    cov = json.loads(raw)

    html = INDEX.read_text()
    rows = parse_rows(html)
    drift = find_drift(rows, cov)
    lag, na_lag = find_lag(rows, cov)

    if args.markdown:
        sys.stdout.write(markdown(drift))
        sys.stdout.write(markdown_lag(lag, na_lag))
    else:
        report(drift)
        report_lag(lag, na_lag)

    if drift and args.apply:
        INDEX.write_text(apply(html, rows, drift))
        print(f"rewrote {len(drift)} cell(s) in {INDEX.name}", file=sys.stderr)

    # Exit code is unchanged ON PURPOSE: 1 means DRIFT, and grid-drift.yml keys its whole
    # PR-opening path off that. A lag is not a defect and must not turn a run red or open a PR
    # that changes nothing — it travels as output (stdout, ::notice::, the markdown section),
    # not as status. Making a lag exit 1 would have been the easy change and the wrong one.
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())

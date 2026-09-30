# WCAG Matrix — Delivery Log

Interactive WCAG 2.1 AA assessment & remediation matrix across DOCX / XLSX / PPTX / PDF, kept
honest against the ACP codebase. Grouped for Azure DevOps intake: each top-level heading maps
to a Feature, each bullet to a Task.

Repository: `jeremyyuAWS/wcag-matrix` · 26 files · 96 commits total
Live: `https://wcag-matrix.mova-io.app/`
**This log starts at 2026-08-01.** Earlier work is not covered. The `(#NN)` references are
GitHub PRs, not ADO work items.

ADO: `MovateAI-Foundry` / `AI-Foundry` · Task **#3656** ACP demo prep — WCAG assessment matrix and app

---

## Feature: Grid-drift guard

- **Fixed a guard that had never once done its job** (#28). The workflow's compare step opened
  with `set -uo pipefail` and relied on `rc=$?` to catch the script's exit 1 ("drift found"), but
  GitHub runs every `run:` block as `bash -e {0}` — errexit was already on, and `set -uo pipefail`
  only adds `-u` and pipefail rather than clearing it. The exit 1 therefore killed the step on
  the python line, `drift=yes` was never written to `$GITHUB_OUTPUT`, and the rewrite and
  pull-request steps were skipped by their own `if` guard. Net effect: the guard signalled drift
  only by turning the build red, and the PR it exists to open was never opened. Six consecutive
  runs failed exactly that way — 2026-07-30 (×4), 08-01, 08-03 — with zero PRs on the repo while
  a real over-claim sat unreported.
- Updated the guard's parse check, which still spoke the pre-2026-07-28 tier vocabulary (#29).
- **Extended the guard to report cells claiming *less* than the code supports** (#42). The
  asymmetry in how the two directions are *handled* is correct and stays: an over-claim is a
  correctness bug and gets rewritten, while an under-claim can be a considered editorial act.
  But "not a defect" had been read as "not worth mentioning", and those differ — an under-claiming
  cell means shipped capability is missing from the coverage percentages with nothing anywhere
  saying so. On 2026-08-07 six cells lagged through three ACP merges and the headline figure did
  not move all day; they were found by a person going looking, which is the manual check this
  guard exists to replace.
- Moved the lag report's boundary into the script and guarded the workflow/script contract (#43).
  The job summary had been built by `awk`-slicing the full report on a heading string, which made
  a heading in `check_grid_drift.py` load-bearing for a pattern in `grid-drift.yml` with nothing
  asserting the two agreed — reword the heading and the summary silently empties, which is the
  same quiet failure the lag report was added to remove. The coupling was introduced in #42 and
  removed rather than left standing.

## Feature: Reconciling the grid against ACP's shipped ceiling

- Lowered cells claiming more than ACP supports to the ceiling derived by
  `gen_matrix_coverage.py`, as a **proposal only** (#31) — ground rules 1–3 make the tier a human
  judgment, so the workflow opens a PR rather than pushing.
- Raised nine cells from R1 to R2 across 1.3.3 (all four formats), 1.4.5 (all four) and 2.4.6
  xlsx (#34). No ACP code changed. In seven of the nine the cell's own prose already described R2
  behaviour while the tier said R1 — "the finding routes to review with the matched phrasing"
  contradicts R1, which means No Remediation. 2.4.6 xlsx was stale rather than deliberate: it
  claimed nothing was detected when `XLSX_DEFAULT_LABELS`, `SheetNameRule` and
  `SheetNameUniquenessRule` all ship.
- Corrected three docx cells that said nothing inspects what ACP has detectors for (#35).
- Closed five open DOCX roadmap notes that answered "what shipped" rather than "what would close
  it" (#38), then the remaining ten carrying the same drift on xlsx/pptx/pdf (#39). **Six of those
  ten turned out to be one gap**: an ASSISTED lane ships and reaches the review queue, but
  `_apply_approved_values` covers alt text (1.1.1) and link text (2.4.4/2.4.9) only, so approving
  the card never reaches the file — capping 3.1.2 on xlsx/pptx/pdf and 2.4.6 on xlsx/pptx at
  Guided. Each note names its own format's write target rather than repeating the Word one.
- Raised six remediation cells (#41) and seven assessment cells (#44) to the shipped ceiling.
  **Checked before changed**, because ground rule 3 makes a lower tier a legitimate editorial act
  — an under-claim is only a defect if it was not a decision. In all seven the drawer prose
  already described the higher tier's behaviour, so these were lagging rather than conservative.
- Raised three cells marked Not Applicable whose stated reason had been overtaken by shipped
  code (#45), reclassified 2.1.2 as Human Assessment on OOXML rather than Not Applicable (#46),
  and aligned 4.1.2 with it so the rest of its row stopped being false (#47).
- Added ACP-derived detail for 1.3.3 and 2.1.2 (#37), and corrected a pptx technical note still
  arguing for a tier that #31 had removed (#32) plus a 1.3.1 cell calling pptx table headers
  manual when the fixer had moved (#33).

## Feature: Scope authority and the tracked rule set

- **Replaced the scope authority** (#36). `MOVA_SCOPE` — column G "Mova iO" of the AccessOps
  coverage file, 17 "Yes" rows — now drives the toggle, the coverage card and the roadmap in
  place of `V5_APPLICABLE`, so every number on the page counts one population. All 17 were
  already among the page's 20, so nothing had to be added, but the switch moves rules in both
  directions, which is why it is not cosmetic. Phase 1 leads with DOCX.
- Made the scope toggle **hide** untracked rules rather than hatching them (#40). Three greyed
  rows sitting mid-grid read as "ACP has a gap here" rather than "Mova iO doesn't track this" —
  the opposite of their meaning. This reverses the file's own "muted, never hidden" rule, and the
  reversal was recorded rather than quietly applied: four separate places said the opposite — the
  CSS comment, the JS comment in the toggle handler, the `MOVA_OUT_REASON` note, and the
  user-facing filterbar paragraph promising rules never disappear — and all four were corrected.
  Changing behaviour and leaving that text standing is how a file starts lying about itself.

## Feature: Progress Log and coverage reporting

- Kept the Progress Log and detection maturity synced from ACP through five automated runs.
- Carried across the finding that **44 of the 61 core-17 pairs can never certify a PASS**,
  derived from the engine's own tables and pinned by a test driving the real `_rule_outcome`
  across all 61 pairs and five finding-count combinations. Three reasons, all lanes this matrix
  already describes: a `REVIEW_FORMATS` pair resolves to REVIEW or NOT_EVALUATED; a pair whose
  assessment lane cannot certify stays REVIEW however thorough the detector; a registry pair with
  partial coverage answers REVIEW. Only 17 of 61 can return PASS on a clean file.
- Refreshed the backlog against reality (#48, #49): four items closed, one found to be wrong,
  three new ones opened.

- **The Progress Log pipeline ran unattended, twice** (`9d687ce`, `6884df5`, 2026-08-09). Both commits
  are **generated**, authored by `github-actions[bot]`: `.github/workflows/progress-log.yml` spliced
  acp's `Matrix-Note:` commit trailers into `index.html` via `repository_dispatch`, through
  `scripts/apply_progress_log.py` (+12/−3 lines across the two). Recorded as one line rather than two
  Tasks because no one wrote them — the value is the evidence that the pipeline fires on a real acp
  merge without a human in the loop, which is what the Feature was built to do.

- **Eight more unattended pipeline runs landed the docx header/footer campaign into the grid**
  (`8e8862b`…`bbcea96`, 2026-08-09 and 2026-08-10, all `github-actions[bot]`). Net effect on
  `index.html` is +41/−1: the `DOC_BUILD` stamp moved `2026.08.09.0723` → `2026.08.10.0731`,
  nine `PROGRESS_LOG` entries were prepended for acp PRs #202–#229, and four new `MATURITY`
  cells appeared — docx 1.1.1, 2.1.2, 2.4.4 and 3.1.2, each carrying the boundary text the
  detector states rather than a bare tier. Eight runs for one net build stamp is the splice
  working as designed: it only prepends entries whose hash is absent, so re-running is a no-op.
  One line rather than nine Tasks — no one wrote them.
- The synced entries record a consistent claim worth keeping visible at intake: every one of the
  docx header/footer fixes (#214, #226, #227, #229) reports **no (criterion, format) cell
  change**. They widen *which parts of a file* the existing detectors read — running headers,
  footers, foot/endnotes — rather than what the matrix claims to cover. A "click here" in a
  footer used to be silent and now fails 2.4.4 exactly as it would in the body.
- **These eight commits had been invisible to every prior standup for a month.** The delta helper
  resolves its tip from the local `origin/main` remote-tracking ref and never fetches, and this
  checkout had not been pulled since 2026-08-09 — so `origin/main` still read `6884df5` and the
  delta came back empty. Fetching first is what surfaced them. This is the third distinct way
  this repo has reported a false-empty delta, after the parked-branch bug (2026-09-04) and the
  sandbox `getcwd` failure (2026-08-31).

## Documentation

- `docs/` carries the tier methodology, drawer content spec and plain-language rewrite, and six
  Deva reconciliation documents (checklist, detector audit, assessment grid, automation tier,
  remediation comparison).

---

## Open items (backlog candidates)

- **The grid tracks a moving target.** Every ACP merge can put a cell out of date in either
  direction; the drift guard now reports both, but acting on the lag report is still manual.
- **Ground rule 3 keeps tier changes human.** The drift workflow opens a PR rather than pushing,
  so an unreviewed PR means the grid is knowingly stale.

- **This checkout is parked on `log-0808-core17`, and it has diverged from `main`.** HEAD carries three
  commits `origin/main` does not; `main` carries three HEAD does not. One pair is the same work under
  two shas — `29087fd` was squash-merged as `03e4ba2` (#50) — which patch-id correctly recognised as
  already covered. The other two are the bot's Progress Log syncs above. Nothing is lost, but the
  branch should be reconciled with `main` or retired; until then this repo's delta is only correct
  because `ado-sync.sh` now ranges over the union of trunk and HEAD rather than HEAD alone.

- **`ado-sync.sh` reads `origin/main` but never fetches it.** Ranging over the trunk fixed the
  parked-branch case, but only as far as the trunk the local `.git` happens to know about. A
  checkout nobody pulls has a frozen `origin/main`, and the delta is then empty for a correct
  reason that is nonetheless wrong — which is how eight commits stayed unreported here from
  2026-08-10 to 2026-09-11. The helper should either fetch before resolving the tip, or print the
  tip's age so a month-old ref is visible in the output rather than silently trusted.

---

## Sync log

- **2026-08-08** — Log created, covering 2026-08-01 onward (26 commits). Four Features written:
  the grid-drift guard, reconciliation against ACP's shipped ceiling, scope authority, and the
  Progress Log pipeline.
- **2026-09-04** — Standup sweep. These two commits had been **invisible to every prior run**: the
  checkout sits on `log-0808-core17` while the work landed on `origin/main`, and `ado-sync.sh`
  compared against HEAD, so the delta read empty. The helper was fixed the same day to range over the
  trunk unioned with HEAD; this repo was the second instance it surfaced, after `acp`. One Task
  appended under Progress Log and coverage reporting, and the branch divergence recorded as an Open
  item. Marker advanced from `c05f003` to the `origin/main` tip.
- **2026-09-11** — Standup sweep, mode `clean`. Eight commits (`8e8862b`…`bbcea96`, 2026-08-09/10)
  appeared for the first time because this run fetched before resolving the tip; the local
  `origin/main` had been frozen at `6884df5` since 2026-08-09, so every standup for a month read an
  empty delta and reported this repo as inactive. All eight are `github-actions[bot]` Progress Log
  syncs, folded into one Task plus one Task for what they carried, and the fetch gap opened as an
  Open item against `ado-sync.sh`. **No hours booked against the commits** — they are bot-authored
  and a month old. 0.5h booked to 2026-09-11 for this catch-up documentation pass (day 3.5h of 8h,
  not capped). Marker advanced from `6884df5` to `bbcea96`.

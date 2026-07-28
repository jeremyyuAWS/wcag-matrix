# ACP — WCAG 2.1 AA Assessment & Remediation Matrix

Interactive matrix of the 20 document-core WCAG rules across DOCX / XLSX / PPTX / PDF,
with per-cell drawers (rule explanation, assessment method, tier rationale, evidence).
Single self-contained `index.html` — no build step, no dependencies.

## Deploy to Netlify

**Option A — Netlify Drop (fastest, no account wiring):**
drag this folder onto https://app.netlify.com/drop → live URL in seconds.

**Option B — Git-connected (auto-redeploy on push):**
1. Push this repo to GitHub (see below).
2. Netlify → Add new site → Import an existing project → pick `JeremyYuAWS/wcag-matrix`.
3. Build command: none · Publish directory: `.` (already set in `netlify.toml`).

**Option C — CLI:** `npm i -g netlify-cli && netlify deploy --prod --dir .`

## Push to GitHub (JeremyYuAWS)

```bash
cd wcag-matrix
git init -b main && git add -A && git commit -m "WCAG matrix + methodology docs"
gh repo create JeremyYuAWS/wcag-matrix --public --source . --push
# or without gh: create the repo on github.com, then
# git remote add origin https://github.com/JeremyYuAWS/wcag-matrix.git && git push -u origin main
```

## Staying in sync with ACP

Two automated pipelines keep this matrix honest against [jeremyyuAWS/acp](https://github.com/jeremyyuAWS/acp):

| | writes | how it lands |
|---|---|---|
| `.github/workflows/progress-log.yml` | the Progress Log timeline | pushed to `main` — append-only changelog facts |
| `.github/workflows/grid-drift.yml` | the grid's tier cells | **opens a PR** — a tier is a human judgment |

The grid job derives each cell's *capability ceiling* from ACP's shipped code (the round-trip-proven
lane table, the review-lane scope table, write-back applier presence, and whether a model sits in the
decision path), then flags cells claiming **more** than that ceiling. Cells claiming less are left
alone — a deliberate downgrade is an editorial act, not drift. See `CLAUDE.md` for the full rules.

## Contents

- `index.html` — the interactive matrix (as-built, code-verified against the ACP repo)
- `scripts/check_grid_drift.py` — compares the grid against ACP's code-derived capability ceiling
- `scripts/apply_progress_log.py` — splices Progress Log entries generated from ACP commit trailers
- `docs/tier-methodology.md` — how Certified / Guided / Human / N-A and the remediation tiers are derived
- `docs/drawer-content-spec.md` — per-cell drawer schema + worked 1.3.2 PPTX example
- `docs/drawer-content-plain.md` — plain-language drawer rewrite (deterministic vs AI/ML vs human)
- `docs/deva-reconciliation.md` — per-rule reconciliation vs the customer conformance checklist, with canonical WCAG 2.2 links

Canonical reference: https://www.w3.org/TR/WCAG22/

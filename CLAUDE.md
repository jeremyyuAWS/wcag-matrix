# wcag-matrix — project context for Claude Code

## What this is
Interactive WCAG 2.1 AA assessment & remediation matrix for document formats (DOCX/XLSX/PPTX/PDF), built for the ACP (Accessibility Compliance Platform) GTM conversation with Deva. Single self-contained `index.html` (no build step) + methodology docs in `docs/`. Live at https://fabulous-crisp-14e424.netlify.app/ (Netlify Drop; redeploy by drag or `netlify deploy --prod --dir .`).

## Ground rules (non-negotiable)
1. **Every capability claim must be code-backed** against the ACP repo at `~/projects/acp` — a tier is claimed only if the detector/fixer is shipped and in the scan path. Catalog labels alone don't count.
2. **Determinism bar:** LLM in a decision path caps a rule at Guided/AI-Proposal. Certified/Automatic = same input → same output.
3. **Honest-partial rule:** detectors with common blind spots (e.g. XLSX contrast skips theme colors) are Guided, never Certified.
4. Known **catalog ≠ code drift** (disclose, don't hide): PPTX reading-order & contrast fixers implemented but catalog says human-only; DOCX/PDF bookmark + XLSX sheet-name fixers cataloged `auto` but NOT built; XLSX hidden-content auto-unhide implemented but cataloged human-only.

## Source-of-truth map (in ~/projects/acp)
- `config/rule-catalog.json` — shipped catalog rules + fix_mode (docx/pptx/xlsx/pdf)
- `api/office_structure.py`, `api/textchecks.py`, `api/ocr.py` — first-party detectors (2.4.6, 1.3.3, 3.1.2, 3.1.5, 1.4.5/1.4.9, 1.4.3 xlsx/pdf/pptx, 2.4.1 pdf, 3.3.2, 2.4.10, 1.4.8)
- `api/remediate_office.py`, `api/remediate_pdf.py`, `api/remediate.py` — implemented fixers
- `api/store.py` — RULE_CATALOG + RULE_FORMATS (per-format applicability)
- `docs/TODO.md` — backlog; detector gaps: 1.4.2 pptx autoplay (blocked on fixture), per-format applicability pass (1.4.1/1.3.5/2.5.3/4.1.2), 3.1.3 deliberately unbuilt
- `jeremy.xlsx` (Deva's checklist) — customer taxonomy: Automated / Automated+Agentic / Human-AT

## index.html data model
All content lives in one `<script>` block:
- `ROWS` — 20 SC rows; per row: `a`/`r` = assessment/remediation tier per format (C/Q/H/NA · A/AC/AP/AI/M/N/NA); `ae`/`re` = drawer content per format (`b` argument bullets, `c` concessions, `x` counterargument, `ev` evidence paths, `cat` drift note)
- `DEVA` — per-SC: Deva's verdict verbatim (`v`, `t`) + our conclusion (`k`: agree|augment|disagree, `ours`, `note`); rendered in Assessment drawers only
- `W3SLUG` — per-SC anchor into https://www.w3.org/TR/WCAG22/ (canonical) + W3C Understanding links
Drawer render: the `tb.addEventListener("click", ...)` handler near the bottom.

## docs/
- `tier-methodology.md` — how Certified/Guided/Human/N-A and remediation tiers are derived (5 placement rules; exec + tech layers)
- `drawer-content-spec.md` — 8-section drawer schema + worked 1.3.2 PPTX example
- `drawer-content-plain.md` — plain-language drawer rewrite (deterministic vs AI/ML vs human framing, per Deva's question)
- `deva-reconciliation.md` — per-rule agree/augment/disagree vs Deva's checklist (§7 = paste-ready drawer blocks; scorecard: 10 agree / 6 augment / 4 disagree, all disagreements = web-lens vs document-surface)

## Outstanding / next tasks
- Push to GitHub: `gh repo create JeremyYuAWS/wcag-matrix --public --source . --push`, then git-connect the Netlify site for push-to-deploy
- Optional matrix improvements: reflect first-party detectors fully; per-cell "upgrade path" notes; resolve the 4 catalog-drift items in the acp repo itself (retag or build fixers — PPTX table-header fixer is the one cheap deterministic build: `firstRow="1"`)
- Validate any index.html edit: extract the script block and eval ROWS/DEVA/W3SLUG (all 20 SCs must resolve in both maps)

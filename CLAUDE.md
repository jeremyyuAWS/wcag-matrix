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
- `ROWS` — 20 SC rows; per row: `a`/`r` = ACP's shipped assessment/remediation tier per format (C/Q/H/NA · A/AC/AP/AI/M/N/NA) — drives the table's cell colors/labels and drawer §5. `ae`/`re` = per-format mechanism detail (`b` argument bullets, `c` concessions, `x` counterargument, `ev` evidence paths, `cat` drift note) — rendered verbatim in drawer §6 (collapsed "Technical notes").
- `RUBRIC` — **the rule-inherent ceiling**, independent of ACP's shipped status (drawer §§1–4): per SC, `plain` (2-sentence rule statement) + per-format `{aClass, aWhy, fClass, fWhy}`. `aClass` ∈ DET/MA/HUM/NAx (assess ceiling: Deterministic/Machine-assisted/Human/Not-applicable), `fClass` ∈ MECH/GEN/REAUTH/NAx (fix ceiling: Mechanical-edit/Generated+approval/Re-authoring/Not-applicable). This is the taxonomy that should NOT churn as ACP ships more — only §5 (derived from `ROWS.a`/`ROWS.r`) changes over time. Grounded in `docs/deva-reconciliation.md` (assess ceiling reasoning) and `docs/tier-methodology.md` (fix ceiling reasoning, reframed without the "shipped" qualifier).
- `DEVA` — per-SC: Deva's verdict verbatim (`v`, `t`) + our conclusion (`k`: agree|augment|disagree, `ours`, `note`); rendered as an aside under drawer §3.
- `W3SLUG` — per-SC anchor into https://www.w3.org/TR/WCAG22/ (canonical), W3C Understanding, and W3C Techniques (quickref) links — all three now shown in drawer.
- `PRINCIPLE` — per-SC WCAG Principle→Guideline breadcrumb text (factual hierarchy, not the SC text itself) — shown under the h2.
- `QUOTE` — per-SC short (<15-word) excerpt of the SC's own normative wording, quotation-marked and attributed with a link back to the canonical text — NOT the full SC text (deliberately trimmed; don't expand these into full reproductions).
- `UPGRADE` — per-SC, one hand-authored sentence: the cheapest concrete build that would close the gap between ACP-today (§5) and the RUBRIC ceiling (§§2–4). Consumed by `buildFAQ()`, not shown standalone.

Drawer render: `renderDrawer(sc, f, trigger)` (called from both the table's click handler and cross-link clicks) builds a **unified 7-section drawer per (SC, format)** — clicking either the assess cell or the remediate cell for the same rule+format opens the identical drawer. Section 6 is a synthesized FAQ (`buildFAQ()`) — mostly derived from data already on `ROWS.ae`/`ROWS.re` (first argument bullet, concessions, counterargument, catalog drift) plus `UPGRADE`, so it doesn't require separate per-format authoring; §7 "Technical notes" no longer duplicates concessions/counterarguments/drift (moved to FAQ) — it's now just mechanism bullets + evidence. `linkify()` auto-links bare SC-code mentions (e.g. "1.3.2") inside plain/why/FAQ text to that SC's own drawer — don't hand-author cross-link markup, it's automatic from any text that mentions another SC's code. Ceiling tiles above the table (`#ceilingTiles`, `#acpTiles`) are computed at load time by iterating `ROWS`×`RUBRIC` — never hand-count these; the IIFE right after the table-build loop is the single source.

**Accessibility of the tool itself** (dogfooded, since it's a WCAG demo): table cells are real `<button>` elements (not click-handler `<td>`s) with descriptive `aria-label`s — natively keyboard-reachable. The drawer (`#panel`) has `role="dialog" aria-modal="true" aria-labelledby="panel-title"`, a focus trap (Tab cycles within it), Escape-to-close, and focus returns to the triggering button on close (`lastTrigger` tracks this — always pass `trigger` to `renderDrawer()`, including from cross-link clicks, or focus-return breaks). If you add new interactive elements to the drawer template, they need `:focus-visible` styling (already covers `button`/`a`/`.xlink` generically) and must be reachable within the existing focus-trap query (`button, a[href], [tabindex="0"]`).

Validate any index.html edit: extract the script block and eval ROWS/RUBRIC/DEVA/W3SLUG/PRINCIPLE/QUOTE/UPGRADE — every SC in ROWS must have a RUBRIC entry with all 4 formats populated, NA-consistency should hold (aClass NAx ⇒ fClass NAx), and `buildFAQ()` should return ≥1 item for every SC×format. A quick in-browser integrity check (paste into devtools or `javascript_tool`):
```js
for (const row of ROWS) { const r = RUBRIC[row.sc]; if (!r) console.error(row.sc, 'missing'); for (const f of ["docx","xlsx","pptx","pdf"]) { const e = r.formats[f]; if (!e || !e.aClass || !e.fClass) console.error(row.sc, f, 'incomplete'); if (buildFAQ(row, f, e).length === 0) console.error(row.sc, f, 'no FAQ'); } }
```

## docs/
- `tier-methodology.md` — ACP's shipped-status tiers (5 placement rules; exec + tech layers) — feeds drawer §5, NOT the RUBRIC ceiling
- `drawer-content-spec.md` — earlier 8-section drawer schema (superseded by the current 6-section RUBRIC-driven drawer, kept for its worked 1.3.2 PPTX example and authoring rules)
- `drawer-content-plain.md` — earlier plain-language rewrite; superseded by RUBRIC's §§1–4 but the plain-language voice/tone still applies
- `deva-reconciliation.md` — per-rule agree/augment/disagree vs Deva's checklist; **this is RUBRIC's primary grounding source** for assess-ceiling reasoning (§7 = paste-ready blocks already close to `aWhy` text)

## Outstanding / next tasks
- Repo already has a GitHub remote (`jeremyyuAWS/wcag-matrix`) and Netlify site (`fabulous-crisp-14e424`, Netlify Drop) — connect them for push-to-deploy if wanted; currently deploy is manual (`netlify deploy --prod --dir .`)
- Table cells still show ACP's shipped status only (not the RUBRIC ceiling) — the ceiling lives in the drawer + the tiles above the table. Consider adding a small ceiling-class indicator per table cell if the two views need to be visible without opening the drawer.
- Optional matrix improvements: per-cell "upgrade path" notes (what's the cheapest build to close the gap to ceiling); resolve the 4 catalog-drift items in the acp repo itself (retag or build fixers — PPTX table-header fixer already landed on acp `main`, see acp memory `pptx-131-table-header-parity`)

# Comparison — V3's Remediation tab vs. ACP's actual fixer code

Source: `accessibility-checklist-automation V3.xlsx`, "Remediation" tab (56 rows; 44 checklist
items once the "Governing rules" narrative rows are excluded — matches V3's own Coverage tab
count exactly). This is the remediation-side companion to `deva-assessment-grid-comparison.md`
(which covers the Assessment tab) — until 2026-07-21 this tab had never been audited against
ACP's actual fixer code at all; the matrix's own §4 remediation text was independently authored,
not cross-checked column by column against V3's own spec.

Audited by 4 parallel research passes (one per format), each reading V3's fix tier, mechanism,
model role, human role, and risk/caveat columns against the real code in
`api/remediate_office.py`, `api/remediate_pdf.py`, `api/proposals.py`, `api/apply_alt.py`,
`api/store.py`, `config/rule-catalog.json`, `docs/rules/*.md`, and `api/remediation_capability.py`
(the newer round-trip-proven source of truth, per its own docstring — cited over the catalog
when the two disagree).

## Verdict key

- 🟢 **MATCH** — ACP's fixer does what V3's spec describes: same mechanism, same tier, same
  safeguards.
- 🟡 **PARTIAL** — a fixer exists and is fundamentally right, but misses part of what V3
  describes (a safeguard skipped, a narrower scope, an approval gate V3 wants that ACP doesn't
  have or vice versa).
- 🟠 **GAP** — a fixer exists but a specific edge case or caveat V3 calls out isn't handled.
- 🔴 **DIFFERENT MECHANISM** — a fixer exists for this item but achieves it a genuinely
  different way, not a narrower version of V3's approach.
- ⚪ **NO FIXER** — nothing exists in ACP for this item at all — confirmed by grep, not assumed.
- 🔵 **CONFIRMED (source-only)** — V3 itself says this needs a human/source decision, not
  automation ("Source / author" tier); ACP agrees and doesn't attempt it. This is a *good*
  outcome, not a gap — the honest answer matches V3's own caveat.

## Scorecard

**44 items: 5 🟢 MATCH · 8 🟡 PARTIAL · 10 🟠 GAP · 8 🔴 DIFFERENT MECHANISM · 10 ⚪ NO FIXER · 3 🔵 CONFIRMED**

Read generously: MATCH + CONFIRMED (8/44, 18%) is fully honest agreement — either the mechanism
matches, or both sides agree it shouldn't be automated. PARTIAL + GAP (18/44, 41%) is a real
fixer that needs tightening. DIFFERENT MECHANISM + NO FIXER (18/44, 41%) is either a genuinely
different approach or nothing built — the honest remediation build list.

## The most consequential findings

This audit surfaced something more important than the V3-vs-ACP delta itself: **several places
where ACP's own catalog/docs disagree with ACP's own running code** — new instances of the
"known catalog ≠ code drift" problem this project's ground rules already name, not previously
documented at this level of detail.

1. **DOCX Color Contrast silently auto-recolors, contradicting ACP's own written policy.**
   `config/rule-catalog.json` and `docs/rules/DOCX-CONTRAST-001.md` both say `fix_mode: human-only`
   with an explicit rationale — *"choosing a replacement colour that meets contrast AND preserves
   brand identity is a design decision."* The live code
   (`api/remediate_office.py:1004-1041`) recolors `w:color` unconditionally, with no approval
   gate, and a passing test (`tests/test_remediate_structure.py:74-85`) locks that behavior in.
   `api/remediation_capability.py` (the newer source of truth) also labels it `AUTO`. V3's
   caveat — *"auto-recoloring breaks brand compliance; propose, do not apply"* — is the position
   ACP's own catalog already took and the code has since drifted away from.
2. **The same pattern repeats in PPTX**: `config/rule-catalog.json` calls `PPTX-ORDER-001`
   (reading order) and `PPTX-CONTRAST-001` (contrast) `human-only`, but both are applied
   unconditionally by `_remediate_pptx_slides` with zero approval step — the opposite direction
   of risk than a cautious reading of the catalog would suggest.
3. **Two proposal lanes exist with no write-back applier at all** — approving them in the HITL
   queue is currently a no-op on the file. PPTX/DOCX link-text proposals
   (`api/store.py:2508`: *"A link-purpose (2.4.4) approval has no applier yet, so it keeps the
   file out of Publish rather than being quietly dropped"*) and PPTX auto-play-audio proposals
   (same gap — `apply_alt.py` is the only applier in the codebase, and it writes alt text only).
4. **XLSX sheet-rename is far less built than the catalog claims.** `config/rule-catalog.json`
   XLSX-SHEET-001 and its doc both say `fix_mode: auto` with a deterministic rename that
   "updates references automatically." The real code is an AI-drafted, human-approval-only
   proposal (`api/proposals.py:868`) with **no applier at all** — nothing renames or deletes a
   sheet in ACP today, and no ref-tracking logic exists anywhere to protect cross-sheet formulas
   even if it did.
5. **PDF alt text overclaims in the opposite direction**: `docs/rules/pdf.missing-alt-text.md`
   and the catalog say `fix_mode: auto`, but the real behavior is grounded-vision-auto-with-
   human-fallback (correctly captured as `ASSISTED` in `remediation_capability.py`, not by the
   catalog).
6. **A stale rationale, not a stale conclusion**: `docs/rules/XLSX-LINK-001.md` says "XLSX
   doesn't have that lane built" for AI-drafted link text — but `api/handlers.py:199-200` shows
   the drafting lane genuinely is built and running. The doc's bottom-line ("nothing gets
   auto-applied") is still correct; only its stated reason is out of date.

None of this changes any `RUBRIC` classification in the matrix — `fClass`/`fWhy` describe the
rule-inherent *ceiling*, which doesn't move based on a catalog/code mismatch in what's
*currently* shipped. But it's the single most actionable list to come out of comparing V3's
spec against real code: every item above is a concrete PR, not a philosophical disagreement.

## Full comparison

### 1.1.1 Non-text Content

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Descriptive Alt Text for Images | Generate+approve — lxml sets `wp:docPr/@descr` after approval | `remediate_office.py:316-471,474-572` — same target attribute, but tier is split: a "faithful source" (title/caption/shape name) or OCR-grounded vision description writes immediately with NO approval; only an ungrounded vision guess is held for one-click approval (`:560-571`) | 🟡 PARTIAL |
| XLSX | Alt Text for Images | Generate+approve — zip/XML edit since openpyxl doesn't expose `xdr:cNvPr/@descr` | `remediate_office.py:585,324-467` — same zip/XML mechanism (openpyxl never imported in this file, so the round-trip-loss risk V3 warns about doesn't apply); same two-tier faithful-vs-AI split as DOCX | 🟢 MATCH |
| PPTX | Alt Text for Images | Generate+approve — set `descr` on `p:cNvPr`; never auto-write unreviewed alt | `remediate_office.py:316-572` — same target attribute; faithful-source and OCR-grounded cases auto-write with no approval, violating V3's blanket "never auto-write" rule by design (ACP treats those as non-invented) | 🟡 PARTIAL |
| PPTX | Decorative Images Marked Correctly | Generate+approve — set the `adec:decorative` extLst flag, or clear `descr` | Detection/proposal logic matches V3's intent and correctly never auto-marks (`:392-426`) — but no code anywhere sets an `adec:decorative` flag; the only applier (`apply_alt.py:64-81`) would write the literal proposal text into `descr=` instead of actually flagging the shape decorative | 🟠 GAP |
| PDF | Descriptive Alt Text for Images | Generate+approve — pikepdf sets `/Alt` on `/Figure` once approved | `remediate_pdf.py:775-872` — same write target, but auto-applies immediately when the vision description is "grounded" (`:852-861`), only deferring to human review when ungrounded (`:826`). Catalog/docs claim pure `auto`, understating the deferred path `remediation_capability.py` correctly labels ASSISTED | 🟡 PARTIAL |

### 1.3.1 Info and Relationships

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Uses Heading Styles | Structural rebuild — `p.style='Heading N'`, strip manual bold/size so style governs | `remediate_office.py:891-930` — writes `w:pStyle` but only promotes paragraphs an existing pseudo-heading heuristic flags, and never strips the run's manual `w:b`/`w:sz` overrides — V3's explicit safeguard isn't honored | 🟠 GAP |
| DOCX | Lists Use Proper Formatting | Structural rebuild — `p.style='List Bullet'/'List Number'`, strip literal bullet/number prefix | Nothing — confirmed by grep across `api/*.py`, `config/rule-catalog.json`, `remediation_capability.py`'s docx table | ⚪ NO FIXER |
| DOCX | Simple Tables with Headers | Auto-fix — `w:tblHeader` on row 0's `trPr` | `remediate_office.py:932-951` — exact mechanism match, AUTO — but V3's caveat ("un-merging merged cells is NOT auto-fixable, route to author") isn't honored: no `gridSpan`/`vMerge` check exists, so any multi-row table gets a header regardless | 🟠 GAP |
| DOCX | Table Captions or Descriptions | Generate+approve — insert a `Caption`-styled paragraph | Nothing — confirmed by grep for "table caption," `w:tblCaption`, `'Caption'` across fixer code and catalog | ⚪ NO FIXER |
| XLSX | Use Table Headers | Auto-fix — `headerRowCount=1` on the table definition | `remediate_office.py:1068-1090` — flips `headerRowCount` `0`→`1`, matching tier and mechanism — but doesn't honor V3's caveat ("if the first row is data, this mislabels it; verify before batch-applying") — no first-row-looks-like-data check exists, and the rule's own doc claims a "shift into header slot" behavior the code doesn't actually do | 🟡 PARTIAL |
| PPTX | Uses Slide Layouts | Source/author — moving content into placeholders isn't safely automatable | Nothing — confirmed by grep; ACP doesn't attempt this and doesn't claim to | 🔵 CONFIRMED |
| PPTX | Meaningful Table Headers | Auto-fix — `a:tblPr/@firstRow='1'`, deterministic, low risk | `remediate_office.py:674-707` — exact mechanism match, fails closed on ≤1 row, AUTO, no caveat V3 flags to miss | 🟢 MATCH |
| PDF | PDF is Tagged | Structural rebuild — Adobe Auto-Tag API or PDFix SDK; veraPDF validates, doesn't remediate | Nothing — confirmed by grep for "pdfix"/"auto-?tag" (0 hits) and no code path writes `/StructTreeRoot` or `/MarkInfo`. Catalog/docs already say `human-only`, matching V3's own "fix at source" caveat; ADR 0028 lists Adobe Auto-Tag as unbuilt future work | 🔵 CONFIRMED |
| PDF | Headings Tagged Properly | Structural rebuild — auto-tag assigns heading tags, correct levels via tag-tree edit | `remediate_pdf.py:296-330,183-214` — no tag-tree write happens at all; ACP derives candidate headings from font-size ranking and surfaces a human-confirmed "heading map" as authoring guidance, never writing to the tag tree | 🔴 DIFFERENT MECHANISM |
| PDF | Table Headers Tagged | Structural rebuild — pikepdf/PDFix sets `/TH` and `/Scope` in the tag tree | Nothing — confirmed by grep for `/TH`, `/Scope`, "table_header" scoped to PDF context (0 hits; the only match is PPTX's unrelated header-marking code) | ⚪ NO FIXER |

### 1.3.2 Meaningful Sequence

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PPTX | Logical Reading Order | Structural rebuild — reorder `spTree` nodes; V3 flags this "highest-risk… can alter appearance" | `remediate_office.py:753-788` — exact spTree reorder mechanism, but applied unconditionally with zero approval/preview, despite `config/rule-catalog.json` calling it `human-only` (contradicted by the live code and by `remediation_capability.py`, which says AUTO) | 🟠 GAP |
| PDF | Correct Reading Order | Structural rebuild — reorder the structure tree via PDFix/Acrobat/pikepdf | `remediate_pdf.py:144-180` — never reorders the structure tree; for an untagged PDF a local vision model proposes an order as a human-confirmed proposal (never auto-applied); for a tagged PDF it does nothing (order already comes from the structure tree) | 🔴 DIFFERENT MECHANISM |

### 1.4.3 Contrast (Minimum)

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Color Contrast | Source/author — writable, but palette choice is a design decision; propose, don't apply | `remediate_office.py:1004-1041` — auto-recolors `w:color` unconditionally, no approval gate, directly contradicting `config/rule-catalog.json`/`docs/rules/DOCX-CONTRAST-001.md`'s own `human-only` policy (see "Most consequential findings" above) | 🟠 GAP |
| XLSX | Color Contrast | Source/author — writable via styles, but a design decision; prefer a compliant built-in table style; keep conditional-formatting rules separate from static fills | `remediate_office.py:820-863` — auto-applies immediately, flattens the font to pure black/white rather than "switching to a compliant style" as V3 recommends. Does correctly keep `dxf`/`cfRule` (conditional-formatting) blocks untouched, honoring that one caveat, but the overall tier still contradicts V3's "needs a human" position | 🔴 DIFFERENT MECHANISM |
| PPTX | Color Contrast | Source/author — writable, palette is a design decision; algorithmic assist available | `remediate_office.py:721-751` — the algorithmic assist V3 describes does exist (hue-preserving min-contrast recolor), but ACP auto-applies it unconditionally (catalog says `human-only`, contradicted by code and `remediation_capability.py`), and never touches slide masters/templates as V3's caveat prefers | 🟠 GAP |
| PDF | Color Contrast | Source/author — not reliably fixable in PDF, colors are baked into content streams; not worth attempting | `remediate_pdf.py:97-141` — the sharpest disagreement in the whole audit: ACP does exactly what V3 says isn't worth attempting, parsing and rewriting content-stream text-fill operators to darken them, applied automatically. Scoped conservatively (text only, not shapes/backgrounds) but is real in-PDF recoloring V3's spec rejects | 🔴 DIFFERENT MECHANISM |

### 1.4.5 Images of Text

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | No Use of Images for Text Only | Source/author — no safe automated path; OCR gives a starting transcript, never auto-applied as alt | `api/ocr.py` + `proposals.py:542-580` — OCRs the baked-in text and proposes the transcript for a reviewer to paste as real text; never silently applied as alt text, matching V3's exact caveat | 🔵 CONFIRMED |
| PDF | No Scanned Images of Text (OCR) | Structural rebuild — run OCR (ocrmypdf/Tesseract/Acrobat) to add a real text layer | Nothing that adds a text layer — confirmed by grep for "ocrmypdf" (0 hits); ACP's only OCR usage is detection/evidence (extracting text to prove an image-of-text finding, handed to a human to re-key), never a text-layer injection | ⚪ NO FIXER |

### 2.1.1 Keyboard

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PPTX | Keyboard Accessible Navigation | Structural rebuild — same mechanism as reading order, fix shape order in `spTree` | `remediation_capability.py:150-157` explicitly marks this HUMAN, always, with its own rationale that a static .pptx "has no interactive/keyboard model to remediate" — ACP disagrees with V3's premise that fixing shape order also fixes 2.1.1, and never applies the reading-order fixer on 2.1.1's behalf | 🔴 DIFFERENT MECHANISM |

### 2.4.2 Page / Doc Titled

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Document Title Set (Metadata) | Generate+approve — `doc.core_properties.title = '...'` | `remediate_office.py:1239-1241` — same target property, filename-derived value, but writes unconditionally with no approval step (`remediation_capability.py` confirms AUTO, not ASSISTED) | 🟡 PARTIAL |
| XLSX | Unique Names for Worksheets | Auto-fix — `ws.title='...'`; `wb.remove(ws)` for blanks; V3 flags this MAJOR risk (breaks cross-sheet formula refs) | `proposals.py:868-926` — AI-drafted, human-approval-only proposal, and **no write-back applier exists at all** — nothing renames or deletes a sheet in ACP today, despite `config/rule-catalog.json` claiming `auto`. No formula-reference tracking exists anywhere, so V3's MAJOR-risk warning is currently moot only because the feature is unfinished, not because ACP built a safeguard for it | 🔴 DIFFERENT MECHANISM |
| PPTX | Unique Slide Titles | Generate+approve — set title text; add a placeholder from the layout if missing | `remediate_office.py:660-671,790-802` — adds a title placeholder + text, matching mechanism, but writes unconditionally (AUTO per `remediation_capability.py`) rather than approve-first, and fabricates a new off-slide placeholder rather than applying an existing layout with one, as V3's caveat prefers | 🟡 PARTIAL |
| PDF | Title and Metadata Set | Auto-fix — set docinfo `/Title` AND `ViewerPreferences.DisplayDocTitle=true`, both needed | `remediate_pdf.py:386-388,471-505` — writes both halves V3 calls out, deterministically, only when a title is genuinely absent (never overwrites a real one) | 🟢 MATCH |

### 2.4.3 Focus Order

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PDF | Logical Tab Order | Auto-fix — set each page's `/Tab` to `/S` (follow structure order), deterministic write | Nothing — confirmed by grep for `/Tab`, `TabOrder`, `tab_order` scoped to PDF (0 hits); not in the catalog's 7-item PDF list, no detector either. A genuine complete gap on V3's easiest structural item | ⚪ NO FIXER |

### 2.4.4 Link Purpose

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Descriptive Hyperlinks | Generate+approve — replace run text inside `w:hyperlink`, target unchanged | `proposals.py:612-696` drafts proposals correctly (matching mechanism + tier) — but **no write-back applier exists**: `handlers.py:1108-1112` states plainly only Office alt text has an applier today. Approving a link-text proposal produces no document change | 🟠 GAP |
| XLSX | Meaningful Hyperlink Text | Generate+approve — set cell display value, leave hyperlink target unchanged; low risk | `proposals.py:675-727` mirrors V3's approach exactly (display-text-only proposal) — but same missing-applier problem as DOCX/PPTX: approving never gets written into the file (`store.py:2504-2509` explains this deliberately keeps the file out of Publish). `docs/rules/XLSX-LINK-001.md`'s stated reason ("lane not built") is stale — the lane IS built, it just has no applier | 🟠 GAP |
| PPTX | Descriptive Hyperlinks | Generate+approve — set `run.text`, leave `hyperlink.address` unchanged; low risk | `proposals.py:675` — same drafting mechanism, same missing-applier gap as DOCX/XLSX | 🟠 GAP |
| PDF | Links Are Descriptive and Active | Generate+approve — descriptive-text edit + separate dead-link workflow (target must be found manually) | `remediate_pdf.py:221-294` covers the descriptive-text half well (deterministic/AI-drafted, human-confirm, never auto-applied) — but there is no dead-link/liveness-check workflow at all; V3's second, explicitly separate workflow is simply unbuilt | 🟡 PARTIAL |

### 3.1.1 Language of Page

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Document Language | Auto-fix — `w:lang/@val` in `styles.xml` docDefaults + on runs | `remediate_office.py:1236-1237` — never touches `w:lang` at all; instead writes the OPC package-level `dc:language` property, matching what the .NET rule reads, but a genuinely different target than V3 describes. Tier (auto, immediate) matches | 🔴 DIFFERENT MECHANISM |
| PPTX | Slide Language | Auto-fix — `a:rPr/@lang` on runs + `defaultTextStyle` in `presentation.xml` | `remediate_office.py:1236-1237` — same as DOCX: only writes `dc:language` metadata, never per-run `a:rPr/@lang` or `defaultTextStyle`. Still clears the finding because `DocumentLanguageRule.cs` accepts metadata OR any run-level lang as an OR condition — but the mechanism itself is different from what V3 describes | 🔴 DIFFERENT MECHANISM |
| PDF | Language Declared | Auto-fix — `pdf.Root.Lang = 'en-US'`, one-line deterministic write | `remediate_pdf.py:352-395` via the vendored `PdfLanguageFixer` — sets catalog `/Lang` deterministically, immediate write, no human step, exactly V3's description | 🟢 MATCH |

### 4.1.2 Name, Role, Value

| Format | Item | V3's fix tier + mechanism (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Accessible Form Fields | Generate+approve — `w:sdtPr/w:alias/@val` on the content control | `form_labels.py:214-227`, called from `remediate_office.py:1050-1058` — exact target match, but ACP files this under SC 3.3.2 (not 4.1.2) internally, and applies immediately whenever adjacent label text is found — V3's "generate+approve" gate isn't honored except for genuinely bare fields, which do route to review | 🟡 PARTIAL |
| PDF | Form Fields Have Labels | Generate+approve — pikepdf sets `/TU` on each AcroForm field, deterministic write once approved | `remediate_pdf.py:630-676,679-709` — exactly the two-tier split V3 implies: when the field's own `/T` reads as a real label, ACP writes `/TU` deterministically inline; when `/T` is a generic auto-name, it defers to a human-authored proposal. A genuinely gated match, not a silent guess | 🟢 MATCH |

## Items with no WCAG SC — not wired into the drawer

Consistent with `ASSESS_SPEC`'s own convention (see `docs/deva-assessment-grid-comparison.md`),
these don't map to one of the 20 tracked SCs and aren't force-fit into a drawer row:

| Format | Item | V3's fix tier | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Accessible Fonts Used | Auto-fix | Nothing — confirmed by grep for `rFonts`/"accessible font" | ⚪ NO FIXER |
| PPTX | Captioning for Multimedia (1.2.x, outside the 20) | Generate+approve | Nothing — 1.2.2 isn't even in `remediation_capability.py`'s pptx table | ⚪ NO FIXER |
| PPTX | No Auto-Playing Audio (1.4.2, outside the 20) | Auto-fix | Detection + proposal exist (`office_structure.py:1329`, `proposals.py:1072`), but **no applier** — same missing-write-back pattern as the link-text items | 🟠 GAP |
| XLSX | Name the Table | Generate+approve | Nothing — only a *read* of `displayName` exists (`proposals.py:930`), never a write | ⚪ NO FIXER |
| XLSX | Add Text to Cell A1 | Generate+approve | Nothing — confirmed by grep for `insert_rows`, no A1-title feature exists | ⚪ NO FIXER |
| XLSX | Name Cells and Ranges | Generate+approve | Nothing — confirmed by grep for `definedName`/`DefinedName`/`defined_names` | ⚪ NO FIXER |

## What this doesn't change

`RUBRIC`'s `fClass`/`fWhy` (the rule-inherent remediation ceiling) are unchanged — none of the
findings above are about what's *possible*, only about what's *built* and whether it matches
what ACP itself claims is built. The catalog/code mismatches in "Most consequential findings"
are the priority list; everything else is a normal build gap, not a policy violation.

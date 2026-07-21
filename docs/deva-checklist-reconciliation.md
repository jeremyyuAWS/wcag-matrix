# Reconciliation — Deva's manual review worksheet vs. ACP's actual capability

Source: `Accessibility Checklist.pdf` (4 pages: PowerPoint, Word, PDF, Excel) — the SOP a human
reviewer works through per file today, provided 2026-07-17. Unlike `jeremy.xlsx` (the earlier
customer checklist, SC-keyed, "Automated/Automated+Agentic/Human-AT" classifications — see
`deva-reconciliation.md`), this is a **process document**: plain-English criteria with concrete
"How to Check or Fix" steps in native Office/Acrobat tools, no WCAG SC numbers attached.

Every row below was verified against ACP's actual code (`~/projects/acp`), not inferred from this
matrix's own prior claims — see the discovery note at the bottom for why that mattered.

**Verdict key:** 🟢 **Full** — ACP covers this today, code-backed. 🟡 **Partial** — ACP covers part of
what the checklist item asks. 🔴 **Gap (in scope)** — maps to one of ACP's 20 core WCAG criteria but
unbuilt. ⚪ **Gap (not a WCAG SC)** — a genuine best practice, but not something any WCAG success
criterion actually requires; worth keeping distinct from a real gap.

## Scorecard

**44 items total: 23 🟢 Full · 5 🟡 Partial · 10 🔴 Gap (in scope) · 6 ⚪ Not a WCAG SC**

| Format | 🟢 | 🟡 | 🔴 | ⚪ |
|---|---|---|---|---|
| PowerPoint (12) | 5 | 3 | 1 | 3 |
| Word (12) | 8 | 1 | 2 | 1 |
| PDF (12) | 7 | 0 | 5 | 0 |
| Excel (8) | 3 | 1 | 2 | 2 |

PDF has the highest gap concentration — five of twelve checklist items map to real, unbuilt WCAG
work (form-field labels, tab order, link text, scanned-OCR, heading-hierarchy tagging), zero
partial credit either way. That's a useful prioritization signal on its own.

## PowerPoint

| Checklist item | Maps to | Verdict | Notes |
|---|---|---|---|
| Unique Slide Titles | 2.4.2 | 🟡 Partial | `SlideTitleRule` checks a title placeholder exists with non-empty text — deterministic, Certified. It does **not** check whether multiple slides share the same title text (verified: no cross-slide comparison anywhere in the 9 PPTX rules). |
| Logical Reading Order | 1.3.2 | 🟢 Full | `ReadingOrderRule` (Guided) + `_remediate_pptx_slides` reorder (Automatic fix). |
| Alt Text for Images | 1.1.1 | 🟢 Full* | Certified presence check, AI-assisted remediation ladder. *See the decorative-marker finding below — a real bug, not a documentation gap. |
| Decorative Images Marked Correctly | 1.1.1 | 🔴 Gap (in scope) | Confirmed: no rule anywhere checks or honors the OOXML decorative marker during assessment. Worse than a simple gap — see below. |
| Color Contrast | 1.4.3 | 🟢 Full | Deterministic, resolved through the theme chain; Automatic fix. |
| Uses Slide Layouts | — | ⚪ Not a WCAG SC | No detector for placeholder-based text vs. manually-drawn text boxes (verified: no rule references `p:ph`/layout placeholders structurally). Closest WCAG tie-in is 1.3.1 in spirit, but this specific authoring practice isn't itself a success criterion. |
| Descriptive Hyperlinks | 2.4.4 | 🟢 Full | Deny-list detection, AI-proposal remediation. |
| Meaningful Table Headers | 1.3.1 | 🟡 Partial | Header-row presence is Certified/Automatic; "meaningful" (descriptive) is the same presence/quality split as everywhere else in this matrix — unbuilt. |
| Captioning for Multimedia | 1.2.2 | ⚪ Not a WCAG SC *(in this matrix)* | 1.2.2 isn't one of ACP's 20 in-scope document-core rules. Confirmed no caption/multimedia detector exists anywhere in the PPTX pipeline. |
| No Auto-Playing Audio | 1.4.2 | ⚪ Not a WCAG SC *(in this matrix)* | Same as above — 1.4.2 isn't in ACP's 20-rule scope; no detector. |
| Keyboard Accessible Navigation | 2.1.1 | 🟡 Partial | `AnimationOrderRule` catches one narrow proxy (auto-advancing content after narration starts) — not general slideshow tab-order testing. |
| Slide Language Set | 3.1.1 | 🟢 Full | Deterministic, Automatic fix. |

## Word

| Checklist item | Maps to | Verdict | Notes |
|---|---|---|---|
| Uses Heading Styles | 1.3.1 / 2.4.6 | 🟢 Full | `HeadingStructureRule` catches skipped levels — a stronger check than "uses styles at all," and requires styles to be used to even evaluate. |
| Lists Use Proper Formatting | 1.3.1 | 🔴 Gap (in scope) | Confirmed: no rule checks `w:numPr` (real list markup) vs. manually-typed dashes/numbers. A legitimate 1.3.1 sub-check, unbuilt. |
| Descriptive Alt Text for Images | 1.1.1 | 🟢 Full* | *Same decorative-marker caveat as PowerPoint. |
| Simple Tables with Headers | 1.3.1 | 🟡 Partial | Header-row check exists (`TableHeaderRule`). Merged-cell detection does not — confirmed no `merge`/`gridSpan`/`vMerge` references in any DOCX rule (XLSX has this via `MergedCellsRule`; DOCX doesn't). |
| Table Captions or Descriptions | 1.3.1 | 🔴 Gap (in scope) | Confirmed: no rule checks for descriptive text before/after a table, distinct from the header-row check. |
| Descriptive Hyperlinks | 2.4.4 | 🟢 Full | |
| Color Contrast | 1.4.3 | 🟢 Full | |
| Document Language Set | 3.1.1 | 🟢 Full | |
| Accessible Fonts Used | — | ⚪ Not a WCAG SC | Sans-serif, 11pt+ is a readability best practice, not a WCAG success criterion — WCAG's actual text-size requirement (1.4.4 Resize Text) is about the *reader's* ability to resize, not the author's initial font choice. Correctly out of scope, not a gap. |
| Document Title Set (Metadata) | 2.4.2 | 🟢 Full | |
| No Use of Images for Text Only | 1.4.5 | 🟢 Full | OCR-based, machine-assisted. |
| Accessible Form Fields | 4.1.2 | 🟢 Full | Content-control field labels — filed under SC_3_3_2 in ACP's catalog rather than 4.1.2 (known, already-documented drift; the check itself is real). |

## PDF

| Checklist item | Maps to | Verdict | Notes |
|---|---|---|---|
| PDF is Tagged | 1.3.1 | 🟢 Full | `tagged_pdf.py` — MarkInfo + StructTreeRoot. |
| Correct Reading Order | 1.3.2 | 🟢 Full | `reading_order.py`, heuristic, Guided/Manual. |
| Headings Tagged Properly | 1.3.1 (extension) | 🔴 Gap (in scope) | Confirmed: nothing beyond `tagged_pdf.py`'s overall tag-tree presence check validates heading-level hierarchy (H1→H2→H3, no skips) the way DOCX's `HeadingStructureRule` does. Zero heading-level references anywhere in the PDF rule set. |
| Descriptive Alt Text for Images | 1.1.1 | 🟢 Full | Tagged PDFs only (by design — untagged PDFs fail 1.3.1 first). |
| Table Headers Tagged | 1.3.1 | 🟢 Full | `table_headers.py`. |
| Language Declared | 3.1.1 | 🟢 Full | |
| Title and Metadata Set | 2.4.2 | 🟢 Full | `document_title.py` + `display_title.py`. |
| Form Fields Have Labels | 4.1.2 | 🔴 Gap (in scope) — **but see the veraPDF spike** | Confirmed: zero AcroForm/Widget inspection anywhere in ACP's PDF pipeline. Directly relevant: the veraPDF spike (`docs/spikes/2026-07-17-verapdf-spike.md` in the acp repo) built a purpose-made form fixture and confirmed veraPDF's UA1 profile catches exactly this gap, correctly identifying the specific unlabeled field. |
| No Scanned Images of Text (OCR applied) | 1.1.1/1.3.1 adjacent | 🔴 Gap (in scope) — **in progress elsewhere** | No OCR-for-scanned-PDF detector on the current branch. `docs/adr/0027-gpu-assisted-scanned-pdf-assessment.md` exists on acp's `main` (Proposed, 2026-07-15) addressing exactly this — not yet merged/available where this was checked. |
| Color Contrast | 1.4.3 | 🟢 Full | Content-stream sampling, Guided (heuristic, not the true ratio — same honest-partial posture as XLSX). |
| Logical Tab Order | 2.4.3 | 🔴 Gap (in scope) | PDF forms expose an explicit `/Tabs` key — well-defined, unbuilt. Already flagged as the cheapest concrete PDF build in this matrix's own upgrade-path notes. |
| Links Are Descriptive and Active | 2.4.4 | 🔴 Gap (in scope) | Confirmed: no PDF link-annotation rule exists at all. The deny-list check other formats use is format-agnostic text matching — porting it is cheap, already noted as the upgrade path for this SC. |

## Excel

| Checklist item | Maps to | Verdict | Notes |
|---|---|---|---|
| Alt Text for Images | 1.1.1 | 🟢 Full* | *Same decorative-marker caveat. |
| Name the table | 2.4.2 (loosely) | 🔴 Gap (in scope) | Confirmed: `TableHeaderRule` reads the table's `DisplayName`/`Name` only to label *where* an issue is, never evaluates whether that name is meaningful vs. the Excel default ("Table1"). Distinct from `SheetNameRule`, which does check sheet **tab** names. |
| Use table headers | 1.3.1 | 🟢 Full | `headerRowCount` toggle, Certified/Automatic. |
| Add text to cell A1 | — | ⚪ Not a WCAG SC | A genuine screen-reader-landing-point best practice (Microsoft's own guidance), but not something any WCAG success criterion requires. Confirmed no A1-specific check exists. |
| Meaningful hyperlink text | 2.4.4 | 🔴 Gap (in scope) | Confirmed: no XLSX link rule exists. Same deny-list logic other formats use would port cheaply — already the noted upgrade path. |
| Use unique names for worksheets | 2.4.2 | 🟡 Partial | `SheetNameRule` catches default names (Sheet1, localized Tabelle1). It doesn't check whether custom names are actually unique from each other, or flag blank worksheets. |
| Name cells and ranges | — | ⚪ Not a WCAG SC | Confirmed no `DefinedName` references anywhere in the analyser tree. A power-user best practice, not a formal criterion. |
| Color Contrast | 1.4.3 | 🟢 Full | Luma-difference heuristic (declared honest-partial), Automatic fix. |

## The decorative-marker discovery

Cross-referencing "Decorative Images Marked Correctly" (PowerPoint) against ACP's actual code
surfaced something worse than a simple gap. This drawer previously (incorrectly) claimed the
docx/pptx assessment rules "honour" the OOXML decorative marker and that "Excel has no decorative
marker." Both claims were false — verified by reading all three `AltTextRule.cs` files directly:
none of them reference "decorative" in any form, in any of the three formats.

The real picture: **the fix side is correct, the detection side isn't.** `api/remediate_office.py`'s
`_inject_descr` function genuinely does check for the decorative marker and correctly skips images
that already carry it. But the assessment rules that decide pass/fail never learned that same
lesson — meaning a properly-marked decorative image is flagged as a false positive on every scan,
even though applying the auto-fix would correctly leave it alone. Corrected in this drawer's 1.1.1
technical notes (docx/xlsx/pptx), and flagged as a real code fix needed in ACP itself (tracked
separately, not fixed here — this repo doesn't touch acp's code).

## What this reconciliation is for

Same purpose as `deva-reconciliation.md`: the honest inventory a customer conversation can be built
on. Two distinct signals worth separating in that conversation:

1. **🔴 Gap (in scope), 10 items** — real, buildable work against ACP's own 20-criterion matrix.
   PDF concentrates five of these; several (Excel/PDF hyperlink text, PDF tab order) are already
   flagged elsewhere in this matrix as cheap, well-defined builds — this checklist independently
   corroborates the same priority list from a completely different source (a human team's own SOP,
   not this matrix's own analysis).
2. **⚪ Not a WCAG SC, 6 items** — genuine best practices Deva's team correctly checks manually, but
   not gaps in ACP's WCAG coverage. Worth naming explicitly so "ACP doesn't check font size" doesn't
   read as a shortcoming — no accessibility tool would, because WCAG doesn't require it.

## Drawer integration

The 28 🟢/🟡 matched items (23 + 5) are wired directly into the live drawer as `CHECKLIST2` in
`index.html`, keyed `sc → format → [{criteria, how-to-text}]` since this checklist is inherently
per-format (unlike `jeremy.xlsx`'s SC-level entries). They render in drawer §4 "Remediation" as
"HITL today — Deva's team's own manual step" — grounding the Current/Human-assisted mechanism in
the exact procedure V3's team already follows, rather than an abstract label. Deliberately excludes
the 10 🔴 and 6 ⚪ items — showing those as "today's manual step" would wrongly imply ACP has a cell
for them to correspond to.

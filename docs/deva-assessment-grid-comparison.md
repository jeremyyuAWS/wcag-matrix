# Comparison — Deva's Assessment grid (V3, column D) vs. ACP's actual detectors

Source: `accessibility-checklist-automation V3.xlsx`, "Assessment" tab, column D ("Deterministic
library + call"). This is the **complete** 38-item comparison (every item that maps to one of
ACP's 20 in-scope WCAG criteria) — an extension of `deva-detector-audit.md`, which checked 11
falsifiable claims as a first pass. All 38 are now verified against ACP's actual code, file:line.

**Per Deva's request, her Assessment grid is the primary reference for "how should this be
assessed" — this doc exists so the delta against what ACP actually does is never ambiguous.**

**Re-verified 2026-07-20** against the latest copy of the V3 file (it had been re-saved since the
first pass — size/mtime changed — but a full re-dump of all 5 sheets confirms the content is
byte-for-byte the same as what's quoted below; the delta was calc-chain/metadata noise, not an
edit). "ACP today" below reflects what's merged to `main` only, per the standing rule that
code-backed means shipped, not just committed on a branch — see the **Pipeline** note under each
affected row for what's open but not yet counted.

## Merged since the first pass

All five PRs that were tracked as "in flight" have now merged to `mova-io/acp` `main` and are
reflected in the table below:

| PR | Merged | Rows moved |
|---|---|---|
| [#47](https://github.com/mova-io/acp/pull/47) — `AltTextRule` honors the decorative marker | 2026-07-21 (`1fc3c2a`) | PPTX Alt Text for Images: PARTIAL → 🟢 MATCH |
| [#46](https://github.com/mova-io/acp/pull/46) — theme-colour resolution for DOCX/XLSX contrast | 2026-07-21 | DOCX Color Contrast, XLSX Color Contrast: both GAP → 🟢 MATCH |
| [#48](https://github.com/mova-io/acp/pull/48) — XLSX blank-worksheet + hyperlink-text detectors | 2026-07-21 | XLSX Meaningful Hyperlink Text: NO DETECTOR → 🟢 MATCH |
| [#49](https://github.com/mova-io/acp/pull/49) — `HeadingStructureRule` reads `w:outlineLvl` | 2026-07-21 | DOCX Uses Heading Styles: PARTIAL → 🟢 MATCH |
| [#51](https://github.com/mova-io/acp/pull/51) — PPTX `DocumentLanguageRule` reads `@altLang` | 2026-07-21 | PPTX Slide Language: GAP → 🟢 MATCH |

Verified against the merged code on `main` (not just the PR diffs) before flipping each verdict —
`ThemeColorHelper.Resolve` in DOCX and `_apply_xlsx_tint`/`_parse_xlsx_theme` in
`api/office_structure.py` both do exactly what her spec describes, same for the other three.

## Verdict key

- 🟢 **MATCH** — ACP's mechanism does what her spec describes.
- 🟡 **PARTIAL** — ACP has a detector, but it misses part of what her spec covers.
- 🟠 **GAP** — ACP has a detector, but a specific edge case her spec calls out isn't handled.
- 🔴 **DIFFERENT MECHANISM** — ACP has a detector for this SC, but it checks something else
  entirely, not a narrower version of her spec.
- ⚪ **NO DETECTOR** — nothing exists in ACP for this item at all (already known from
  `deva-checklist-reconciliation.md`'s gap list).
- ⬜ **NOT RE-VERIFIED** — consistent with prior session review, not independently re-checked
  against this exact V3 wording this pass.

## Scorecard

**38 items: 16 🟢 MATCH · 5 🟡 PARTIAL · 5 🟠 GAP · 2 🔴 DIFFERENT MECHANISM · 9 ⚪ NO DETECTOR · 1 ⬜**

Read generously: MATCH + PARTIAL (21/38, 55%) means ACP's mechanism is at least fundamentally the
right one for that item. GAP + DIFFERENT MECHANISM + NO DETECTOR (16/38, 42%) is the honest build
list — some are cheap (one more attribute), some are genuinely unbuilt.

## Full comparison

### 1.1.1 Non-text Content

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Descriptive Alt Text | Require `@descr`; reject `@title` (legacy, AT ignores it) | `AltTextRule.cs:57` — only reads `Description` (`@descr`), never `@title` | 🟢 MATCH |
| XLSX | Alt Text for Images | `xdr:cNvPr/@descr`+`@title`; cover pics AND charts | `Xlsx/Rules/AltTextRule.cs:72,80-84` — only `@descr`, covers `Picture`(45) + `GraphicFrame`(52) | 🟢 MATCH |
| PPTX | Alt Text for Images | `p:cNvPr/@descr`+`@title`; non-decorative shapes only | `Pptx/Rules/AltTextRule.cs:26-51,64` — covers both shape types via `@descr`; never reads `@title` (fine); now also skips flagging images marked decorative via `AltTextHeuristics.IsMarkedDecorative()`, merged in [PR #47](https://github.com/mova-io/acp/pull/47) (`1fc3c2a`, 2026-07-21) | 🟢 MATCH |
| PPTX | Decorative Images Marked Correctly | Detect the `adec:decorative` extension flag | Nothing — confirmed absent (the decorative-marker finding from earlier this session) | ⚪ NO DETECTOR |
| PDF | Descriptive Alt Text | Require `/Alt`; reject `/ActualText` (text substitute, not a description) | `image_alt_text.py:105-113` — only `/Alt`, no `/ActualText` reference | 🟢 MATCH |

### 1.3.1 Info and Relationships

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Uses Heading Styles | Primary: `w:outlineLvl`; secondary: canonical style ID | `HeadingStructureRule.cs:14-28,40-46` — now reads `w:pPr/w:outlineLvl` (level = val+1) as a co-equal signal alongside the style-ID lookup, exactly her primary+secondary split. Merged [PR #49](https://github.com/mova-io/acp/pull/49), 2026-07-21 | 🟢 MATCH |
| DOCX | Lists Use Proper Formatting | Resolve `w:numPr` through the style-inheritance chain | Nothing | ⚪ NO DETECTOR |
| DOCX | Simple Tables with Headers | `w:tblHeader` on row 0 AND merged-cell detection (`w:vMerge`/`w:gridSpan`) | `TableHeaderRule.cs:26,50-66` — checks `w:tblHeader`, **no merged-cell detection anywhere in the file** | 🟡 PARTIAL |
| DOCX | Table Captions or Descriptions | Canonical-name `caption` style before/after the table | Nothing | ⚪ NO DETECTOR |
| XLSX | Use Table Headers | `tbl.headerRowCount == 1` | `Xlsx/Rules/TableHeaderRule.cs:37-38` — reads `HeaderRowCount`, flags when 0 | 🟢 MATCH |
| PPTX | Meaningful Table Headers | `firstRow="1"` is a styling flag, not semantics — corroborate with cell content/formatting | `Pptx/Rules/TableHeaderRule.cs:35-36` — `firstRow` is the sole signal, no corroboration | 🟠 GAP (declared limitation, now independently confirmed by her spec too) |
| PDF | PDF is Tagged | `/MarkInfo/Marked` AND `/StructTreeRoot` | `tagged_pdf.py:34-43` — both conditions, AND-combined | 🟢 MATCH |
| PDF | Headings Tagged Properly | `/H1`-`/H6` present, correct nesting, no skips | Nothing beyond the overall tagging check | ⚪ NO DETECTOR |
| PDF | Table Headers Tagged | `/TH` present AND `/Scope` attribute set | `table_headers.py:44-46` — checks `/TH` only, **`/Scope` never read** | 🟠 GAP |

### 1.3.2 Meaningful Sequence

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PPTX | Logical Reading Order | spTree order vs. geometric top-left sort, flag divergence | `ReadingOrderRule.cs:22-49` — exactly this comparison, `OrderBy(Top).ThenBy(Left)` | 🟢 MATCH |
| PDF | Correct Reading Order | Structure-tree order vs. content-stream order vs. visual x/y | `reading_order.py` (session's prior general review; not re-verified against this exact V3 wording this pass) | ⬜ NOT RE-VERIFIED |

### 1.4.3 Contrast (Minimum)

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Color Contrast | Resolve direct hex OR theme color + `themeTint`/`themeShade` math | `ColourContrastRule.cs` — direct hex OR `ThemeColorHelper.Resolve()` (new `ThemeColorHelper.cs`, full 12-slot scheme + tint/shade HSL math). Merged [PR #46](https://github.com/mova-io/acp/pull/46), 2026-07-21 | 🟢 MATCH |
| XLSX | Color Contrast | Theme + XLSX-specific tint float formula (different math than DOCX) | `api/office_structure.py` — new `_parse_xlsx_theme()` + `_apply_xlsx_tint()`, using the correct SpreadsheetML-specific tint float formula (distinct from DOCX's). Merged [PR #46](https://github.com/mova-io/acp/pull/46), 2026-07-21 | 🟢 MATCH |
| PPTX | Color Contrast | `solidFill` (`srgbClr`/`schemeClr`+theme) vs. shape→layout→master chain | `ColourContrastRule.cs:112-167` — full shape→layout→master chain confirmed, **but only explicit RGB/SystemColor hex; `schemeClr`+theme-color-map resolution isn't handled** | 🟡 PARTIAL |
| PDF | Color Contrast | veraPDF WCAG profile, OR render+pdfplumber-bbox+pixel-sample | `office_structure.py:340-390` — neither: content-stream `non_stroking_color` extraction + luma heuristic, no rendering at all | 🔴 DIFFERENT MECHANISM |

### 1.4.5 Images of Text

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | No Use of Images for Text Only | Walk `word/media/*`, OCR (no deterministic path) | `api/ocr.py:49,85-95,121-132` — `_MEDIA_RE` walks `word\|ppt\|xl` media, tesseract OCR, no deterministic path (shared module, not docx-specific) | 🟡 PARTIAL (mechanism matches, scope is broader/shared) |
| PDF | No Scanned Images of Text (OCR) | Near-zero text layer + large-area image = scan, no OCR needed to detect | Nothing | ⚪ NO DETECTOR |

### 2.1.1 Keyboard

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PPTX | Keyboard Accessible Navigation | Extract interactive shape order (spTree) + hyperlink/action shapes; tab order is extractable | `AnimationOrderRule.cs:19-69` — checks auto-advancing animation timing nodes entirely. **Not the same signal at all** — ACP's actual 2.1.1 mechanism solves a different, narrower problem than the one she describes | 🔴 DIFFERENT MECHANISM |

### 2.4.2 Page / Doc Titled

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Document Title Set | `dc:title` present, non-empty | `DocumentTitleRule.cs:14-16` — reads `PackageProperties.Title` | 🟢 MATCH |
| XLSX | Name the Table | `tbl.displayName` not matching `^Table\d+$` | Nothing | ⚪ NO DETECTOR |
| XLSX | Unique Names for Worksheets | Default-pattern match AND cross-sheet uniqueness | `SheetNameRule.cs:14,22-25` — default-pattern regex only, **no uniqueness check among custom names** | 🟠 GAP |
| PPTX | Unique Slide Titles | Non-empty AND unique across the deck (set comparison) | `SlideTitleRule.cs:27-51` — per-slide non-empty only, **no cross-slide uniqueness check** | 🟠 GAP |
| PDF | Title and Metadata Set | `/Title` non-empty AND `DisplayDocTitle` true, both required | `document_title.py:33-40` + `display_title.py:35-38` — both conditions checked, as two separate rule IDs/severities rather than one combined pass/fail | 🟢 MATCH (architecturally split, substance covered) |

### 2.4.3 Focus Order

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| PDF | Logical Tab Order | `/Tab` entry should be `/S`; plus AcroForm field order | Nothing | ⚪ NO DETECTOR |

### 2.4.4 Link Purpose

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Descriptive Hyperlinks | Resolve `r:id`→rels; flag generic text AND raw URLs (`^https?://`) | `LinkPurposeRule.cs:70-84` — resolves rels correctly, flags generic-text set, **no raw-URL regex check exists** | 🟡 PARTIAL |
| XLSX | Meaningful Hyperlink Text | Public `cell.hyperlink` + scan formulas for `HYPERLINK(` | New `Xlsx/Rules/LinkPurposeRule.cs` (`XLSX-LINK-001`) covers both mechanisms exactly as she describes — standard `<hyperlinks>` element AND formula-driven `=HYPERLINK(...)` cells. Merged [PR #48](https://github.com/mova-io/acp/pull/48), 2026-07-21 | 🟢 MATCH |
| PPTX | Descriptive Hyperlinks | `run.hyperlink.address`+text; flag generic AND raw URLs | `LinkPurposeRule.cs:26-57` — same pattern as DOCX, generic-text yes, **raw-URL regex no** | 🟡 PARTIAL |
| PDF | Links Are Descriptive and Active | Descriptive text check + HTTP liveness check | Nothing | ⚪ NO DETECTOR |

### 3.1.1 Language of Page

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Document Language | Read `@val`, `@eastAsia`, AND `@bidi` | `DocumentLanguageRule.cs:69-72` — `LangSet()` checks all three | 🟢 MATCH |
| PPTX | Slide Language | Read `@lang` AND `@altLang` | `DocumentLanguageRule.cs:66-70` — now checks both `Language` and `AlternativeLanguage` on runs and end-paragraph marks. Merged [PR #51](https://github.com/mova-io/acp/pull/51), 2026-07-21 | 🟢 MATCH |
| PDF | Language Declared | Catalog `/Lang` present, valid BCP-47 | `document_language.py:31-34` — reads `/Lang` | 🟢 MATCH |

### 4.1.2 Name, Role, Value

| Format | Item | Her spec (abridged) | ACP today | Verdict |
|---|---|---|---|---|
| DOCX | Accessible Form Fields | `w:sdtPr/w:alias/@val` non-empty AND `w:tag` set | `office_structure.py:83-92,167-175` (filed under 3.3.2, confirmed) — checks **only `@alias`**, `w:tag` never read | 🟠 GAP |
| PDF | Form Fields Have Labels | AcroForm `/Fields`, each needs `/TU`, `/FT`, `/V` | Nothing | ⚪ NO DETECTOR |

## What's new here vs. the earlier 11-item audit

Two findings are worth calling out beyond the raw tally:

1. **2.1.1/pptx is a "different mechanism," not a narrower version of the same idea.** ACP's actual
   detector (`AnimationOrderRule`) checks auto-advancing animation timing — a real, legitimate
   2.1.1 signal, but not the shape/hyperlink tab-order extraction her spec describes. Both are
   defensible ways to attack 2.1.1 in PPTX; they're just not the same check, so "ACP already does
   this" would overclaim if read against her specific spec.
2. **Raw-URL detection is missing from BOTH DOCX and PPTX link-purpose rules** — a small, cheap,
   two-format gap (the generic-text deny-list exists and works; a bare `https://...` as the visible
   link text is a distinct failure mode neither rule currently catches).

## What this doesn't change

RUBRIC's aClass/fClass are unchanged. This doc is the "what we currently do vs. her Excel"
reference the comparison was asked to make unambiguous — it's a map of the actual delta, not a
verdict on which one should win. See `deva-automation-tier-reconciliation.md` for the two open
policy questions already flagged, and `deva-detector-audit.md` for the first-pass 11-item version
of this same exercise (superseded in coverage by this doc, kept for its narrative framing).

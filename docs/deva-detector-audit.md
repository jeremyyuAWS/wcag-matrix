# Audit — Deva's technical spec (column D) vs. ACP's actual detector code

Source: `accessibility-checklist-automation V3.xlsx`, provided 2026-07-20 — the "Item Map" sheet
from `accessibility-checklist-automation V1.xlsx` (reconciled in
`deva-automation-tier-reconciliation.md`) renamed **"Assessment"** and substantially upgraded in
column D ("Deterministic library + call"): where V1 gave high-level implementation sketches, V3
gives specific, falsifiable technical claims about edge cases — exact XML attributes, formula
differences between formats, and things a naive implementation gets wrong.

Unlike the automation-tier reconciliation (a corroboration exercise, no code changes), this is a
**direct code audit**: for each falsifiable claim in column D, we read ACP's actual detector
source and verified MATCH, GAP, or PARTIAL. Same method that caught the decorative-marker bug —
read the real code, don't trust prior documentation.

## Results: 4 MATCH · 1 PARTIAL · 6 GAP (of 11 checked)

| # | Claim | Detector | Verdict | Evidence |
|---|---|---|---|---|
| 1 | DOCX language must read `@w:val`, `@w:eastAsia`, AND `@w:bidi` — checking `@val` alone misses CJK/RTL | `Docx/Rules/DocumentLanguageRule.cs:69-72` | 🟢 **MATCH** | `LangSet()` checks all three attributes, true if any is set. |
| 2 | DOCX heading detection should primarily use `w:pPr/w:outlineLvl` (language-independent), with canonical (non-localized) style name as secondary signal | `Docx/Rules/HeadingStructureRule.cs:14-28,40-46` | 🟡 **PARTIAL** | Matches via `ParagraphStyleId.Val` (already non-localized — good) but never reads `w:outlineLvl` at all. A custom-styled paragraph with an outline level set but a non-`HeadingN` style ID is invisible to this rule. |
| 3 | DOCX alt text must NOT accept `@title` as satisfying it (legacy field, AT doesn't read it) | `Docx/Rules/AltTextRule.cs:57` | 🟢 **MATCH** | Only reads `Description?.Value` (`@descr`); no `@title` reference anywhere. |
| 4 | DOCX contrast must resolve theme color + apply `themeTint`/`themeShade` math, not just direct hex | `Docx/Rules/ColourContrastRule.cs:44-49` | 🔴 **GAP** | Reads only direct `w:color/@val`; `continue`s (skips entirely) on null/`auto`. No `ThemeColor`/`ThemeTint`/`ThemeShade` reference anywhere in `Docx/`. Worse than "missing tint math" — **theme-colored runs aren't resolved at all**, so contrast issues on themed text (the common case) are silently missed, not mis-computed. |
| 5 | XLSX tint formula is DIFFERENT math than DOCX (`lum*(1±tint)`, not `themeTint`/`themeShade`) — using the DOCX formula gives wrong ratios | No `Xlsx/Rules/ColourContrastRule.cs` exists; `api/office_structure.py:537-543,566-568` | 🔴 **GAP** | No XLSX engine-level contrast rule at all. The Python fallback resolves only direct `rgb=` colors by explicit design (theme/indexed return `None`, documented as "guessing at a theme/indexed color is exactly the false-positive risk"). Not using the wrong formula — using **no** formula; tint resolution doesn't exist for XLSX anywhere. |
| 6 | Blank-worksheet detection must NOT use `max_row`-style stored-dimension properties (stay inflated after clearing) — must iterate cells and check charts/images | `Xlsx/Rules/SheetNameRule.cs:19-26` | 🔴 **GAP** | Only a default-name regex (`^Sheet\d+$`). No blank-sheet detection logic exists in this file, or anywhere in the XLSX rules / `office_structure.py`. |
| 7 | PDF alt text must NOT accept `/ActualText` as satisfying `/Alt` (ActualText is a text substitute for ligatures, not an image description) | `worker-python/.../pdf/image_alt_text.py:105-113` | 🟢 **MATCH** | `_get_alt()` reads only `/Alt`; no `/ActualText` reference. A Figure with only `/ActualText` correctly still gets flagged. |
| 8 | PPTX `firstRow="1"` is a style-banding flag, not true header semantics (PPTX has no `<TH>`) — should corroborate with additional signals | `Pptx/Rules/TableHeaderRule.cs:35-36` | 🔴 **GAP** (documented limitation, now code-confirmed) | `firstRow` is the sole signal — no cell-content, formatting, or `@descr` corroboration. This matches what this matrix's own drawer already discloses as a declared limitation for 1.3.1/pptx; the audit confirms it's accurate, not stale. |
| 9 | XLSX `=HYPERLINK()` formula cells are invisible to `cell.hyperlink` — a detector checking only that property misses them entirely | No XLSX hyperlink rule exists anywhere | 🔴 **GAP** (reconfirmed) | Same conclusion as `deva-checklist-reconciliation.md`'s earlier finding ("No link rule for spreadsheets... unclaimed") — re-verified still accurate, and the formula-cell case would be missed by *any* naive `cell.hyperlink`-only implementation, not just ACP's absent one. |
| 10 | PDF language just needs catalog `/Lang`, no multi-attribute complexity | `worker-python/.../pdf/document_language.py:31-34` | 🟢 **MATCH** | Reads `/Lang` correctly. Sanity check, no finding expected or found. |
| 11 | PPTX language must read BOTH `a:rPr/@lang` AND `@altLang` (the DrawingML CJK equivalent) | `Pptx/Rules/DocumentLanguageRule.cs:66-70` | 🔴 **GAP** | `HasContentLanguage()` checks only `Language` (`@lang`); no `AlternativeLanguage`/`@altLang` reference despite the OpenXml SDK exposing it. CJK runs marked only via `@altLang` in a Latin-default deck would be missed. |

## What this means

Six confirmed gaps, none of them documentation errors this time — real detector limitations,
verified against the actual C#/Python source with file:line citations. Two categories:

1. **Silent skip, not silent wrong-answer** (items 4, 5, 6, 9): theme-colored contrast and XLSX
   blank/hyperlink detection don't exist at all in these paths — the honest-partial posture this
   matrix already applies elsewhere (declared blind spots, capped at Guided rather than falsely
   Certified) already accounts for this in the *contrast* cells' aClass, but the *scope* of what's
   silently skipped is broader than previously spelled out in the technical notes.
2. **Known limitation, now independently confirmed** (item 8): the PPTX table-header proxy was
   already disclosed in this matrix; Deva's spec arriving at the same conclusion independently is
   corroboration, not a new finding.
3. **Real, narrow multi-attribute gaps** (items 2, 11): DOCX heading detection misses non-standard-
   styled headings with an explicit outline level; PPTX language detection misses `@altLang`-only
   CJK runs. Both are cheap, well-scoped fixes — read one more attribute.

## Not done here

RUBRIC's `aClass`/`fClass` weren't changed. These are code gaps in ACP, not errors in this
matrix's *description* of ACP — the honest move is a code fix in `acp` (tracked separately) plus a
note in the relevant drawer cells' technical notes, not a ceiling reclassification. The existing
aClass values (e.g., DOCX/PPTX/XLSX 1.4.3 = Deterministic) already scope the claim to "where colors
resolve" — these findings sharpen *how much* doesn't resolve, they don't invalidate the ceiling
claim itself.

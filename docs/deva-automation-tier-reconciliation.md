# Reconciliation — Deva's automation-tier analysis vs. our RUBRIC ceiling

Source: `accessibility-checklist-automation V1.xlsx`, provided 2026-07-20 — an independent
automation-tier classification of the same 44-item checklist reconciled in
`deva-checklist-reconciliation.md`. Five sheets: Coverage (aggregate stats), Item Map (per-item
tier + specific detection logic + WCAG SC), Remediation (per-item fix tier + risk notes), Local
Models (recommended open-weight models per task), Gaps vs WCAG (checklist-vs-criteria mismatches).

This doc compares her per-item **Tier** (Deterministic / Det+model / Model-primary / Det+human)
and **Fix tier** (Auto-fix / Generate+approve / Structural rebuild / Source+author) against our
`RUBRIC`'s `aClass`/`fClass` for the same 28 matched SC×format cells — using the equivalence
Deterministic↔DET, {Det+model, Model-primary}↔MA, Det+human↔HUM for assessment, and
Auto-fix↔MECH, Generate+approve↔GEN, {Structural rebuild, Source/author}↔REAUTH for remediation.

**This is a corroboration exercise, not a bug hunt.** Unlike the decorative-marker find (a
confirmed code error), every disagreement below is a genuine, debatable difference in scoping or
risk philosophy — nothing here is silently changed in `RUBRIC`. Two named patterns account for
almost all of it.

## Scorecard

**28 items: 18 (64%) full agreement · 21/28 (75%) assessment ceiling agrees · 20/28 (71%) fix
ceiling agrees**

## Pattern 1 — she scores the checklist item's literal scope; we score the whole SC

Five disagreements share one shape: our `RUBRIC` ceiling reflects the **full WCAG criterion**
(which usually has a presence half and a quality/descriptiveness half — the same split this
matrix uses everywhere, e.g. 1.1.1's "presence is deterministic, equivalence is agentic"). Her
checklist item is narrower — often *just* the presence half — so she correctly scores it as more
deterministic than our SC-level ceiling, then lists descriptiveness as a **separate, optional**
model check layered on top rather than folded into one ceiling.

| Item | Us (SC ceiling) | Her (item-scoped) | Her reasoning |
|---|---|---|---|
| 2.4.2/pptx "Unique Slide Titles" | MA | **DET** for uniqueness | "Check non-empty AND unique across the deck (set comparison). Fully deterministic." Descriptiveness is a separate optional check she notes but doesn't fold in. |
| 2.4.2/pdf "Title and Metadata Set" | MA/GEN | **DET/Auto-fix** | Presence of `/Title` + `DisplayDocTitle` is the literal checklist item; descriptiveness is optional and separate. |
| 2.4.2/xlsx "Use unique names for worksheets" | MA/GEN | **DET/Auto-fix**, and — separately — **no WCAG SC behind it at all** | Two disagreements stacked: scope (uniqueness is mechanical) AND whether ACP's own catalog is even right to file `SheetNameRule` under 2.4.2. WCAG 2.4.2 is about the *document* having a title; worksheet-tab uniqueness is arguably a navigation-labeling practice with no literal SC text behind it. Worth a real decision, not a silent pick — see below. |
| 4.1.2/docx "Accessible Form Fields" | DET | **MA** (reversed direction) | Here the disagreement runs the OTHER way: whether a content control has a name at all is a file fact (our DET), but she scores the checklist item as asking whether the label is *meaningful* — "Is the label meaningful for the field's purpose? Local: Qwen3-8B" — the quality half, not presence. |
| 1.3.1/docx "Uses Heading Styles" | DET/MECH | **MA/REAUTH** (reversed) | Same reversal: her item includes catching *pseudo*-headings (bold/large manual paragraphs with no real heading style) via a model. This is a genuine, useful catch — ACP's own `HeadingStructureRule` has a **declared false-negative** on exactly this case ("fake headings... carry no outline level and are invisible to the heading rule"), noted in this matrix's own technical notes for 1.3.1/docx. Her item-level ceiling is arguably the more honest one for "uses heading styles correctly," even though our narrower skip-check is genuinely deterministic for what it does check. |

**Recommendation:** don't change `RUBRIC` — the SC-level ceiling is still the right thing for this
matrix to report. But her narrower framing is a legitimate additional layer worth citing in the
relevant `aWhy` text (especially 1.3.1/docx, where she's independently pointing at a gap this
matrix already knows about). The 2.4.2/xlsx catalog question (does "unique worksheet names" belong
under 2.4.2 at all?) is the one item here that isn't just a scoping difference — it's worth
actually deciding, not just noting.

## Pattern 2 — she's more conservative on "deterministic but consequential" fixes

Four disagreements are all **fix-side only** (assessment agrees), all about the same underlying
question: does a deterministic *algorithm* producing a deterministic *edit* still count as
"Mechanical" when the edit has real design/layout consequences a person should approve?

| Item | Us | Her | Her reasoning |
|---|---|---|---|
| 1.4.3/docx, xlsx, pptx "Color Contrast" fix | MECH (auto-recolor to black/white) | **Source/author** | "Writable... but the choice is a design decision... Auto-recoloring breaks brand compliance. Propose, do not apply." |
| 1.3.2/pptx "Logical Reading Order" fix | MECH (deterministic reorder algorithm) | **Structural rebuild** | "Highest-risk fix in the deck. Reordering changes z-order and can alter appearance." |
| 2.1.1/pptx "Keyboard Accessible Navigation" | MA/MECH | **Det+human / Structural rebuild** | Shares the reading-order mechanism and risk; she also scores the *assessment* side stricter — "operability is behavioral," not machine-assisted — a genuine, not just scope-based, disagreement. |

This matrix's own existing text for the docx contrast fix already half-concedes her point ("auto-
recolour trades brand palette for compliance... design review recommended") without it changing
the `fClass` — the classification landed on MECH because the *algorithm* is deterministic, while
her fix-tier is scoring the *consequence* of applying it unreviewed. Both are defensible; they're
answering slightly different questions ("is the edit mechanism deterministic" vs "is it safe to
apply without a human approving the specific instance").

**Recommendation:** this is the one place worth a real conversation rather than a note. If this
matrix's `fClass` is meant to answer "what's the cheapest defensible mechanism," MECH stands. If
it's meant to answer "would ACP ever auto-apply this without a human in the loop," her REAUTH is
probably right — and notably, **ACP's own actual behavior already agrees with her**: the docx/xlsx/
pptx contrast fixers apply automatically today (tier `A`/`Certified` in this matrix's ACP-today
status), but the drawer's own FAQ for that cell already surfaces the design-palette caveat as a
known objection. Worth deciding whether that caveat should cap the ceiling itself, not just live in
the FAQ.

## Full agreement (18 of 28 — the majority)

All four 1.1.1 formats, three of four 1.3.1 table/tag-header checks, both 1.3.2/pdf, three of
three 3.1.1 language checks, 2.4.2/docx, both 2.4.4 hyperlink checks, 1.4.5/docx, and 1.4.3/pdf all
agree on both assessment and fix ceiling — independent corroboration from a completely different
analysis method (hers: code-level implementation planning; ours: WCAG-text-plus-format-properties
reasoning) landing in the same place.

## What this doesn't change

No `RUBRIC` values were altered by this reconciliation — every disagreement above is a legitimate,
named difference in scope or risk philosophy, not a confirmed error the way the decorative-marker
finding was. The one genuinely open question (does "unique worksheet names" belong under 2.4.2)
and the one genuinely open policy question (should design-consequential-but-deterministic fixes
cap at REAUTH) are flagged for an actual decision, not resolved here.

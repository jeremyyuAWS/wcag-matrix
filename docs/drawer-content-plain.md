# Drawer Content — Plain-Language Rewrite (Deva's framing)

The drawer now answers one question, in this order: **What does this rule mean → Can ACP assess it — deterministically, with AI/ML, or neither → How → What ACP can't tell → (technical detail, tucked at the bottom).**

Rule of thumb: the top half must be readable by someone who has never heard of WCAG or XML. No element names, no file paths, no acronyms above the fold. The technical reader gets everything they have today — moved into a collapsed "Technical detail" section.

---

## The three answers to Deva's question (drawer badge, replaces the tier jargon)

Every Assessment drawer opens with one of three plain sentences, directly under the rule name:

| Badge | Plain answer shown | When it applies |
|---|---|---|
| **Certified** | "**Yes — ACP assesses this deterministically.** The answer is a fact in the file; the same file always gets the same result. No human needed." | Rule-based check reads the fact directly (title set? language declared? header row marked? contrast ratio math). |
| **Guided** | "**Yes — ACP detects this with AI/ML (or smart pattern analysis) and a person confirms.** ACP finds the likely problem and shows its evidence; the final call is human." | Machine finds strong evidence but can't be certain alone: OCR reading text inside images, language identification, layout-order analysis. |
| **Human** | "**Not yet by machine.** This takes human judgment — ACP routes it to a reviewer with a checklist so it's never skipped." | No reliable machine signal exists for this format. |
| **N/A** | "**This rule can't be broken in this file type**, so it doesn't count for or against the score." | The failure mode requires something the format doesn't have. |

This IS the deterministic-vs-AI/ML answer: green = deterministic, blue = machine-detected (deterministic heuristics or AI/ML) + human confirmation, orange = human, grey = not applicable. One extra sentence in the legend makes the AI boundary explicit: **"AI never decides pass/fail on its own — it gathers evidence; verdicts are either deterministic or human-confirmed."**

---

## Drawer template (per cell)

**1. What this rule means** *(2 sentences, plain)*
What the rule requires + who is harmed when it's broken. Written like you'd explain it to a new employee, not an auditor.

**2. Can ACP assess this?** *(the badge sentence from the table above)*

**3. How ACP does it** *(2–4 plain steps)*
Describe the check as an action a person could picture. Allowed vocabulary: "opens the file the way a screen reader would," "checks whether a description is attached," "compares the announced order to the visual order." Numbers and thresholds stay (they build trust); code names don't.

**4. What ACP can't tell** *(1–2 plain concessions)*
The honest limit, phrased as a capability boundary, not an apology — and what happens instead (routed to a reviewer).

**5. Technical detail** *(collapsed by default)*
Everything from the current drawer: exact attributes read, decision logic, declared false-positive/negative modes, evidence file paths, catalog entry, drift notes.

---

## Worked example 1 — 1.1.1 Non-text Content · DOCX · Assessment

### What this rule means
Every image in a document needs a short written description ("alt text") so a blind reader using a screen reader knows what the image shows. Without it, they hear "image" — and nothing else — where sighted readers see a chart, a photo, or a diagram.

### Can ACP assess this?
**Yes — deterministically.** Whether a description is attached to an image is a fact stored in the file. ACP reads it directly; the same file always gets the same answer, with no AI guesswork in the verdict.

### How ACP does it
1. ACP opens the document the same way a screen reader would and finds every image.
2. For each one, it checks whether a real description is attached — a filename like "image1.png" or an auto-generated label doesn't count.
3. Images the author marked as decorative are correctly skipped, exactly as a screen reader would skip them.

### What ACP can't tell
ACP verifies a description **exists** — not that it's a *good* description. "Chart" attached to a revenue chart passes this check; judging quality is routed to a reviewer. Embedded objects from other programs (like pasted Excel charts) are declared out of scope.

### Technical detail *(collapsed)*
- .NET `AltTextRule` reads `descr=` on every `wp:docPr` — deterministic XML attribute check; bare filenames and generic auto-names count as missing; `decorative` flag exempts.
- Certification requires a clean ANALYSED run (`scripts/rubric.py`); an errored rule makes the score an upper bound.
- Evidence: `engine/office-analysers/.../Docx/Rules/AltTextRule.cs` · `docs/rules/DOCX-ALT-001.md` · catalog `DOCX-ALT-001` (SC 1.1.1, CRITICAL, auto).

---

## Worked example 2 — 1.3.2 Meaningful Sequence · PPTX · Assessment

### What this rule means
A slide has to make sense when read aloud in order — title first, then the points, in the sequence the author intended. Screen readers ignore the visual layout and read shapes in the file's internal order; if that order is scrambled, a blind listener hears the slide as word salad while it looks perfectly fine on screen.

### Can ACP assess this?
**Yes — ACP detects it with layout analysis, and a person confirms.** ACP finds slides where the spoken order likely won't match the visual order and shows its evidence; a reviewer makes the final call.

### How ACP does it
1. ACP reads the order a screen reader would announce the shapes in.
2. It computes the order a sighted person would read them in — top to bottom, left to right.
3. When a shape lands more than one position away from where the eye expects it, the slide is flagged, and the whole deck gets one advisory: "verify the reading order."

### What ACP can't tell
Some legitimate designs — two-column layouts, diagrams with callouts — have no single "correct" order, so a well-built deck can get flagged. That's why this is machine-detected but human-confirmed, never auto-failed.

### Technical detail *(collapsed)*
- `ReadingOrderRule.cs`: `<p:spTree>` index (= tab order) vs. geometric sort of `<a:off>` offsets; displacement ≤ 1 tolerated; <2 positioned shapes skipped; per-slide hits collapsed to one file advisory (`scanner.py :: _collapse_reading_order`).
- Drift note: catalog `PPTX-ORDER-001` = human-only remediation; `_remediate_pptx_slides` implements an auto-reorder. Resolve before presenting the remediation cell.

---

## Worked example 3 — 1.4.1 Use of Color · DOCX · Assessment

### What this rule means
Color can't be the only way information is communicated — "items in red are overdue" fails for anyone who can't distinguish the colors, including roughly 1 in 12 men with color-vision deficiency and anyone printing in black and white.

### Can ACP assess this?
**Not yet by machine.** Whether color is the *only* carrier of meaning depends on understanding what the document is saying — that's judgment. ACP routes it to a reviewer with a checklist so the rule is never silently skipped.

### How ACP does it
ACP can't decide this one, but it doesn't drop it either: the criterion appears in every file's review checklist as a human item, with sign-off tracked, so an auditor can see it was checked and by whom.

### What ACP can't tell
Everything, for now — there is no reliable machine signal for "meaning carried by color alone" in a document. (On web pages, a partial detector exists; documents are the gap.)

### Technical detail *(collapsed)*
- No document detector by design; surfaced HUMAN-tier via the per-file coverage manifest (`RULE_FORMATS`, `api/store.py`). HTML has a partial check (`HTML_LINK_COLOR_ONLY`, `scanner.py`).

---

## Legend copy for the panel (replaces the current definitions)

> **How ACP decides — three ways, honestly labeled.**
> **Deterministic (green):** the answer is a fact in the file. ACP reads it; same file, same verdict, every time. Audit-proof by construction.
> **Machine-detected + human-confirmed (blue):** ACP's analyzers — pattern analysis, text-language identification, OCR that reads text inside images — find the likely problem and attach the evidence. A person makes the call. AI gathers evidence here; it never issues a verdict.
> **Human (orange):** judgment calls. ACP's job is making sure they happen: routed, checklisted, signed off.
> **N/A (grey):** the rule can't be broken in this file type, so it's excluded from the score rather than padding it.

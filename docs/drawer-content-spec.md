# Drawer Content Spec — per-cell detail (v2)

Goal: every cell's drawer answers five questions in order — **what the rule means → what ACP actually checks → how it decides → why this tier → what happens next.** Two reading depths: the first line of each section is exec-readable; the indented detail is for the technical reader. All claims trace to a file path.

---

## Recommended drawer schema (8 sections)

### 1. WHAT THIS RULE MEANS (new — plain-language definition)
Two sentences, no jargon: what the WCAG criterion requires, and who is harmed when it fails. Written for the exec.

### 2. WHAT ACP CHECKS (new — the rule, concretely)
The specific, narrower thing the shipped detector examines — never claim the full SC. Name the exact file structure read (XML element, PDF dictionary key). This is where the honest gap between "the SC" and "our rule" is visible by design.

### 3. HOW DETECTION WORKS (new — mechanism, high level)
3–5 steps from file to finding: what is parsed, what is compared, what threshold trips a finding. Include the tolerance/floor values — they are the difference between a defensible heuristic and a black box.

### 4. THE ARGUMENT (existing — keep)
Why this signal is real: the causal story linking the measured property to actual user harm.

### 5. CONCEDE UP FRONT (existing — keep, expand)
Declared false-positive AND false-negative modes, each traced to a code decision (skip-conditions, unresolved cases). This section is why the tier claim survives an audit.

### 6. TIER RATIONALE (new)
One line applying the placement rules: which rule of the methodology (determinism bar, honest-partial, code-backed) put this cell in this tier — and what upgrade, if any, would move it up a tier.

### 7. REMEDIATION PATH (new)
What happens after detection: auto-fix (and its provenance stamp), AI draft → approval, or HITL routing with the guidance text shown to the reviewer. Links assessment to the remediation column so the two dimensions read as one story.

### 8. EVIDENCE (existing — keep, extend)
Source paths for detector, collapse/aggregation logic, fixer (if any), and test fixture. Add the catalog entry (`rule-catalog.json` id) and, where drift exists, note it explicitly.

---

## How detection works — the platform-level story (for the "how does it detect" question)

One pipeline, four evidence classes. Every document is unpacked to its true structure — OOXML files are ZIP archives of XML parts; PDFs are object graphs with a catalog and (if tagged) a structure tree. Detection never looks at pixels first; it reads what assistive technology reads.

1. **Structural reads (deterministic).** The rule engine reads the governing property directly: `dc:title`, `w:lang`, `w:tblHeader`, `/Lang`, `StructTreeRoot`. Presence/absence or arithmetic (contrast ratio) decides Pass/Fail. → Certified tier.
2. **Structural heuristics (deterministic, proxy).** The engine compares two structures that *should* agree — e.g., XML shape order vs. geometric position (reading order), animation trigger conditions. Divergence is evidence, not proof. → Guided tier.
3. **Content analysis (deterministic NLP/OCR).** Extracted text is run through seeded, reproducible analyzers: regex patterns (1.3.3 sensory instructions), seeded langdetect (3.1.2), tesseract OCR word-counts (1.4.5). No LLM in the decision path — same file, same findings, every run. → Guided tier.
4. **Human routing.** Anything requiring judgment ships to the HITL queue with whatever evidence tiers 1–3 gathered. → Human tier.

Vision/LLM models appear only on the **remediation** side (drafting alt text, link text) — never in the Pass/Fail decision. That split is the audit story: verdicts are reproducible; generative AI output is always human-approved or re-validated.

---

## Worked example — 1.3.2 Meaningful Sequence (Level A) · PPTX · Assessment

**Verdict: Guided review**

**WHAT THIS RULE MEANS**
When content is read aloud, the order must preserve the meaning — a slide that visually reads title → point 1 → point 2 must be announced in that order. A screen reader ignores the visual layout entirely: it announces shapes in the file's internal order. If that order is scrambled, a blind user hears the slide as word salad while the sighted author sees nothing wrong.

**WHAT ACP CHECKS**
Not the full SC — one strong, machine-visible failure mode: whether each slide's **shape tree order** (`<p:spTree>`, which *is* the tab/reading order AT uses) matches the shapes' **visual top-to-bottom, left-to-right order** computed from their XY offsets (`<a:off>` in each shape's transform).

**HOW DETECTION WORKS**
1. Parse each slide's shape tree; record every positioned shape's XML index (= tab order) and its X/Y offset. Shapes without coordinates are excluded rather than guessed.
2. Sort shapes geometrically: top → bottom, then left → right. This is the expected reading sequence.
3. Compare each shape's tab position against its geometric rank. **Tolerance: displacement ≤ 1 position is ignored** — side-by-side elements legitimately jitter by one slot.
4. Any shape displaced by more than 1 → one SERIOUS finding for that slide, with computed vs. expected order as evidence. Slides with fewer than 2 positioned shapes are skipped.
5. Per-slide hits are **collapsed to a single per-file advisory** (`_collapse_reading_order`, `api/scanner.py`) — the reviewer verifies the deck's reading order once, not slide-by-slide.

**THE ARGUMENT**
The shape tree order is not a proxy for what AT does — it is *literally* what AT reads. Divergence between it and visual order is invisible to the author (the slide looks fine) and fully audible to the screen-reader user. That asymmetry is exactly the class of defect automated checking exists for.

**CONCEDE UP FRONT**
- *False positives:* two-column layouts and diagram-with-callouts slides have legitimately ambiguous geometric order — a correct deck can trip the geometric sort.
- *False negatives:* only `<p:sp>` shapes with explicit transforms are ranked; pictures, group shapes, and placeholder-inherited positions are outside the comparison.
- The detector says "**may** not match" and the platform treats it that way: detect-and-route, never auto-fail.

**TIER RATIONALE**
Guided, by the determinism bar's counterpart — the check is deterministic but the *criterion* isn't decidable from geometry alone (rule 3, honest-partial: ambiguous layouts are a declared false-positive mode). Guided is the code's own posture (`RemediationType.HUMAN_REQUIRED`), not a downgrade. No upgrade path to Certified exists without understanding content semantics.

**REMEDIATION PATH**
Catalog: `human-only` — reviewer gets the guidance string ("Open the Selection Pane… reorder shapes"). ⚠️ Drift note: `remediate_office.py` (`_remediate_pptx_slides`) implements an automatic reorder; catalog and code disagree. Resolve before this cell's remediation column is presented.

**EVIDENCE**
- Detector: `engine/office-analysers/.../Pptx/Rules/ReadingOrderRule.cs`
- Collapse: `api/scanner.py :: _collapse_reading_order` (`_READING_ORDER_RULES`)
- Catalog: `config/rule-catalog.json → PPTX-ORDER-001` (SC 1.3.2, SERIOUS, human-only)
- Fixer (drift): `api/remediate_office.py :: _remediate_pptx_slides`

---

## Authoring rules for filling the other cells

- Section 1 never mentions XML; section 3 always names elements/keys and thresholds. If a threshold exists in code (`>1 position`, `≥12 words`, `≥0.90 confidence`, `≥10 OCR words`, `4.5:1`), it appears in the drawer — thresholds are the credibility.
- Section 5 must contain at least one real concession per cell. A drawer with no concession reads as marketing and invites the audit to find the concession for you.
- Every Certified cell's section 3 must show the property read and the decision rule in one line each. If that takes more than two lines, the cell probably isn't Certified.
- Where catalog ≠ code, the drawer says so (as above). One source of truth per claim, drift disclosed.

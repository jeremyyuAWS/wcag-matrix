# ACP Capability Tiers — Methodology

**How a cell earns its tier.** Companion to "WCAG 2.1 AA — Assessment & Remediation by Document Format."
Basis: `config/rule-catalog.json` + first-party detectors (`office_structure.py`, `textchecks.py`, `ocr.py`) + implemented fixers (`remediate_office.py`, `remediate_pdf.py`). A tier is only claimed when the code is shipped and in the scan path.

---

## The five placement rules (applied to every cell)

1. **Code-backed only.** A tier requires a shipped detector/fixer, not a catalog label. Rules declared `auto` without an implemented fixer (DOCX/PDF bookmarks, XLSX sheet-name) do not earn Automatic.
2. **Determinism bar.** Any LLM in the *decision* path caps a rule at Guided (assessment) or AI Proposal (remediation). Certified and Automatic are reserved for same-input → same-output logic — the audit-defensibility requirement.
3. **Honest-partial rule.** If a detector's blind spots are common in real files (e.g., XLSX contrast skips theme colors), a PASS may mean "couldn't evaluate," so the rule is capped at Guided rather than Certified.
4. **Assessment ≠ Remediation.** Independent axes. ACP can certify a failure it cannot fix (untagged PDF) and fix an issue it cannot detect (XLSX contrast recolour predates its detector).
5. **Per-format applicability.** Decided rule-by-rule (`RULE_FORMATS` in `api/store.py`), never blanket — Reflow is N/A for a paginated DOCX but a real (human) question for PDF.

---

## Assessment tiers

### 🟢 Certified (Auto Assessment)

**Exec:** ACP alone makes the Pass/Fail call. The result is reproducible, evidence-backed, and defensible in an audit without a human in the loop. Zero marginal reviewer cost.

**Tech — all four must hold:**
- The detector reads the governing property **directly from file structure**: OOXML parts (`dc:title`, `w:lang`, `w:tblHeader`, `firstRow`) or the PDF catalog (`/Lang`, `/Title`, `DisplayDocTitle`, `StructTreeRoot`).
- The WCAG criterion is **fully decidable** from that property — presence/absence or an arithmetic threshold (WCAG relative-luminance contrast ratio).
- **Deterministic:** no model inference, no randomness; identical file → identical finding every run.
- **Known blind spots are rare or documented;** otherwise the rule drops to Guided (rule 3).

**Examples:** 2.4.2 (title properties, all four formats), 3.1.1 (language declaration, all four), 1.3.1 table-header flags (DOCX/XLSX/PPTX).
**Evidence recorded:** rule ID, file location, extracted value — enough to reproduce the verdict.

### 🔵 Guided Review (Detected Problem)

**Exec:** ACP finds the likely violation, attaches evidence and a confidence signal; a human makes the final call. Reviewer effort drops from "read the whole document" to "confirm this specific finding." Cost: minutes per finding, not hours per document.

**Tech — the detector is a proxy; three sub-classes:**
- **Structural heuristic:** signal correlates with violation but can't decide it — PPTX reading order (z-order vs. visual position, "*may* not match"), PPTX animation triggers (2.1.1).
- **Deterministic content analysis:** regex/NLP over extracted text — 1.3.3 sensory-instruction pattern (verb + shape/position within 45 chars), 3.1.2 seeded `langdetect` (≥12-word segments, ≥0.90 confidence). Deliberately non-LLM so findings are reproducible.
- **Measurement with a semantic remainder:** 1.4.5 OCR (tesseract; ≥10 words, ≥20k px) detects text-in-image but cannot judge the "essential" exception — a human closes that gap.

**Invariant:** Guided findings are detect-and-route — never auto-passed, never auto-failed. They land in the HITL queue with evidence attached.

### 🟠 Human Assessment

**Exec:** no machine signal exists today. The criterion requires judgment, context, or behavioral testing with assistive technology. ACP's value here is the managed workflow — routing, evidence capture, sign-off trail — not detection. This is a recurring reviewer-minutes operating cost, priced into the per-document effort estimate.

**Tech:** the SC depends on semantics the file format does not encode (1.4.1 — is color the *only* carrier of meaning?) or on runtime behavior a static file doesn't have (2.4.3 focus order). Surfaced as HUMAN-tier in the per-file coverage manifest so the criterion is never silently skipped.

### ⚪ Not Applicable

**Exec:** the criterion cannot be violated in this format, so it is removed from the denominator — it neither passes nor fails.

**Tech:** the failure mode requires a capability the format lacks — 1.4.10 Reflow presupposes a resizable viewport; paginated DOCX/XLSX/PPTX have none. N/A is a **justified exclusion recorded per rule-and-format**, distinct from "untested" (which would be a coverage gap, not an exemption). Each N/A carries its rationale.

---

## Remediation tiers

### ⚡ Automatic

**Exec:** ACP writes the fix into the file and re-validates it. Zero human minutes; the re-scan is the proof.

**Tech — qualifying criteria:** deterministic edit to file internals involving **no content judgment** — set `dc:language`/`dc:title`, write `/Lang` + `DisplayDocTitle`, mark header rows, unhide data-bearing rows/columns. Every fix is applied to a copy (`remediated-*`), provenance-stamped (OOXML custom properties / PDF docinfo: tool, date, WCAG target, fixes applied), and confirmed by re-scan.

**Disclosed boundary case:** 1.1.1 alt text is *conditional* automatic — vision-model-generated and auto-applied only when a vision model or faithful source is available (PDF additionally requires a tagged structure tree; ≤25 figures/doc); everything else defers to review. Footnoted on the matrix because it straddles Automatic and AI Proposal.

### 🟣 AI Proposal

**Exec:** AI drafts the fix; a human approves before anything touches the file. AI speed with human accountability.

**Tech:** the fix requires **generating content** whose correctness is not machine-verifiable — descriptive link text (2.4.4 DOCX/PPTX, `fix_mode: ai-assisted`). The draft routes to the HITL queue; with AI off it degrades to human-only. Approved fixes apply server-side with the same provenance stamping as Automatic.

### 🟠 Manual (Human)

**Exec:** ACP tells the human exactly what to fix, where, and how; the human performs it. Guidance plus tracking, not automation.

**Tech:** the fix is judgment-laden (choosing compliant colors inside a brand palette — 1.4.3 DOCX) or carries destructive risk (unmerging cells reflows a worksheet). ACP supplies per-rule remediation guidance (`RuleMetadataRegistry`), the finding location, and closes the loop via re-scan.

### 🔴 No Automated Remediation

**Exec:** ACP can report the finding, but the fix is a re-authoring effort. These feed the estate action plan with effort estimates (including "archive instead of remediate" where that's cheaper).

**Tech:** the fix requires document understanding no deterministic edit can supply — generating a correct PDF tag tree for an untagged document (1.3.1), or heading-inferred bookmarks on untagged PDFs (rejected as garbage-risk; documented decision in the backlog).

---

## Why the tiers are shaped this way (exec framing)

The tiers are a **cost model**, not just a taxonomy. Certified + Automatic = zero marginal human cost, scales with compute. Guided + AI Proposal = minutes per finding, scales with finding count. Human + Manual = reviewer time, scales with document count — the number that dominates an estate plan. N/A removes formats from the denominator so coverage percentages stay honest. Every roll-up figure ("≈22.6 hrs across 98 documents, 46% fully automatic") is computed from these tier assignments — which is why a cell is never promoted past what shipped code can defend.

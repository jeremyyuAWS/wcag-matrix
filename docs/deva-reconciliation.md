# Reconciliation — Deva's Validation Approach vs. the Document-Format Drawer

Source: `jeremy.xlsx` — WCAG 2.1 + 2.2 Conformance Checklist (87 SC; 32 Automated / 7 Automated + Agentic / 48 Human-AT).
Scope here: the 20 document-core rules in the matrix. Verdicts: **Agree · Augment · Disagree (context)**.

---

## 1. Taxonomy mapping — the two schemes are the same scheme

| Deva's class | Drawer tier | Same meaning |
|---|---|---|
| Automated ("deterministic scripts / ML / rendering — no LLM cost") | Certified / Deterministic | Machine decides |
| Automated + Agentic ("+ targeted LLM semantic judgment") | Guided / Machine-detected + human-confirmed | Machine evidences, judgment closes |
| Human / AT | Human | Person decides |

Adopt her language where it's better: "**agentic intervention is applied surgically**" is exactly the drawer's determinism-first posture. And her global note — *"for any Required criterion, human validation provides the legal assurance layer regardless of detection method"* — should be added to the legend: even Certified rows get human assurance sampling for legal defensibility. That is an augmentation the drawer currently lacks.

## 2. The one structural disagreement: her column classifies **web content**

Every "How to Test" is a web technique — browser zoom, DOM order, axe, bookmarklets, `<html lang>`. The classification is correct *for web* but does not transfer 1:1 to documents. Six of the 20 rules change class when the surface is a file instead of a page. The drawer should say this explicitly rather than silently overriding her: **same taxonomy, different surface.**

## 3. Per-rule verdicts (20 document-core rules)

| SC | Deva says | Verdict | Document-format reality (and why) |
|---|---|---|---|
| 1.1.1 Non-text Content | Automated + Agentic | **Agree** | Exactly right, and worth splitting in the drawer: alt *presence* is deterministic (stored in the file); alt *quality* is the agentic/human half. Code matches (deterministic `AltTextRule` + generic-name heuristics; vision only on the fix side). |
| 1.3.1 Info & Relationships | Automated + Agentic | **Agree** | Structural presence (header rows, heading skips, tagged PDF) deterministic; whether relationships are *correctly* expressed is the agentic remainder. |
| 1.3.2 Meaningful Sequence | Human / AT | **Disagree (context)** | True for the web (DOM + screen reader). For documents the reading order is *explicit in the file* — PPTX shape order, PDF structure tree, XLSX merge/hide state — so machines can do better than human-only: deterministic for XLSX, machine-assisted (order-comparison heuristic, shipped) for PPTX/PDF. Her class undersells documents here. |
| 1.3.3 Sensory Characteristics | Automated + Agentic | **Agree + augment** | Agree it's machine-detectable. Augment: an LLM isn't required — a deterministic pattern detector (shipped) finds instruction-verb + shape/position phrasing reproducibly; agentic judgment is optional, human confirms. Better for audit than LLM-dependent detection. |
| 2.4.6 Headings & Labels | Automated + Agentic | **Agree** | The canonical split rule: skipped levels / empty headings deterministic; *descriptiveness* agentic. Drawer already models it this way. |
| 3.1.1 Language of Page | Automated | **Agree** | Fully deterministic in all four formats; shipped detect + fix. No caveats. |
| 3.1.2 Language of Parts | Automated | **Disagree (nuance)** | Her test ("inspect lang on foreign content") only verifies passages the author already marked. The real compliance question — finding *unmarked* language changes — requires language identification (ML, probabilistic). Verifying declared parts: deterministic. Detecting missing ones: machine-assisted + human confirm (shipped as seeded langdetect ≥0.90 → review). Should be Automated + Agentic by her own definitions. |
| 1.4.4 Resize Text | Automated | **Disagree (context)** | Automated *on the web* (zoom the browser). Documents have no author-controlled zoom failure mode — viewers zoom natively. N/A for document formats; keep her class for the web surface. |
| 1.4.5 Images of Text | Automated | **Augment** | Detection is automatable — but via OCR (ML) with thresholds, and the "essential exception" (logos, screenshots) is judgment. Machine-assisted + human confirm, not hands-off Automated. Shipped that way. |
| 1.4.10 Reflow | Automated | **Disagree (context)** | Web technique (320px viewport). Fixed-layout OOXML: N/A. PDF: the honest proxy is tagged-structure presence (enables reflow in AT) — machine-assisted at best, human otherwise. |
| 1.4.12 Text Spacing | Automated | **Disagree (context)** | Bookmarklet test is web-only. No document equivalent — user spacing overrides aren't a document author obligation. N/A for documents. |
| 1.4.1 Use of Color | Human / AT | **Agree + augment** | Agree for today. Augment with a roadmap note: grayscale-render diffing and color-only-run detection could lift this to machine-assisted later; a partial HTML check already exists. |
| 1.4.3 Contrast (Minimum) | Automated | **Agree + augment** | The math is deterministic — agree. Augment with the honest limit: in documents the hard part is resolving *effective* colors (theme inheritance, fills, text over images). Where colors resolve → certified; where they don't (e.g., XLSX theme colors) → must degrade to review, never silently pass. |
| 1.4.11 Non-text Contrast | Automated | **Augment** | On web, an analyzer reads computed styles. In documents, shapes/charts/borders need render-and-measure (ML/vision) — machine-assisted in principle, nothing shipped today (Human on the matrix). Her class is the ceiling, not the current state. |
| 2.4.2 Page / Doc Titled | Automated | **Agree + note** | Deterministic in all four formats, shipped both directions. Small inconsistency in her own sheet: 2.4.2 requires *descriptive* titles (judgment) while 2.4.6 descriptiveness earns Agentic — the drawer keeps presence = certified, descriptiveness = agentic remainder. |
| 2.4.3 Focus Order | Human / AT | **Agree + augment** | Agree for web and for interactive content. Augment: OOXML has no focus order (N/A), but PDF *forms* have an explicit tab-order key (`/Tabs`) that is deterministically checkable — a cheap detector Deva's web lens misses. |
| 2.4.4 Link Purpose | Automated + Agentic | **Agree** | Generic-text detection deterministic ("click here" fails, her own example); purpose-in-context agentic. Shipped as exactly that split (detector + ai-assisted fix). |
| 2.1.1 Keyboard | Human / AT | **Agree + augment** | Agree — behavioral, needs AT testing where it applies. Augment per format: static DOCX/XLSX → N/A (nothing to operate); PPTX has one machine-assisted proxy (auto-advancing animation triggers, shipped); PDF with forms/scripts → human. |
| 2.1.2 No Keyboard Trap | Human / AT | **Agree** | Same logic; documents mostly N/A, PDF-with-scripts human. |
| 4.1.2 Name, Role, Value | Human / AT | **Agree + augment** | Agree for the full SC. Augment: the document-scope slice — do form fields expose a name — is deterministically checkable (the DOCX content-control label check shipped under 3.3.2 is that pattern; PDF AcroForm `/T`/`/TU` is the same check waiting to be written). |

## 4. Scorecard

**Agree: 10 · Agree + augment: 6 · Disagree: 4** (3.1.2 nuance; 1.3.2, 1.4.4, 1.4.10, 1.4.12 as web-lens transfers — the 1.3.2 disagreement favors *more* automation for documents, the others less).

Net effect on the matrix: zero cells change tier because of this reconciliation — the disagreements are all places where the drawer's per-format view is already ahead of the checklist's web view. What changes is the *narrative*: the drawer can now cite the customer's own taxonomy as the shared frame.

## 5. Drawer integration — add one section per drawer

Insert between "What ACP can't tell" and "Technical detail":

> **vs. the conformance checklist (Deva)**
> One line: her class for this SC, verdict (agree / augment / disagree-for-documents), and the one-sentence reason from the table above.
> Example — 1.3.2 PPTX: *"The checklist rates this Human/AT — correct for web pages, where reading order lives in the rendered DOM. In a .pptx the reading order is written into the file, so machines can detect mismatches and a person confirms: better than human-only."*

And two legend additions, both hers: agentic intervention is surgical (LLM only where rules can't assess meaning), and every Required criterion keeps a human assurance layer regardless of detection method.

## 6. Canonical reference link (every drawer)

Each drawer's "What this rule means" section ends with a link to the canonical W3C spec — the normative text, so no drawer paraphrase is ever the authority: **[WCAG 2.2 (W3C Recommendation)](https://www.w3.org/TR/WCAG22/)**, deep-linked to the criterion's own anchor. Optionally pair it with the W3C *Understanding* page (plain-language intent + examples) — a natural fit for the exec reader:
`https://www.w3.org/WAI/WCAG22/Understanding/<slug>.html`

Per-SC anchors for the 20 matrix rules:

| SC | Canonical link |
|---|---|
| 1.1.1 | https://www.w3.org/TR/WCAG22/#non-text-content |
| 1.3.1 | https://www.w3.org/TR/WCAG22/#info-and-relationships |
| 1.3.2 | https://www.w3.org/TR/WCAG22/#meaningful-sequence |
| 1.3.3 | https://www.w3.org/TR/WCAG22/#sensory-characteristics |
| 2.4.6 | https://www.w3.org/TR/WCAG22/#headings-and-labels |
| 3.1.1 | https://www.w3.org/TR/WCAG22/#language-of-page |
| 3.1.2 | https://www.w3.org/TR/WCAG22/#language-of-parts |
| 1.4.4 | https://www.w3.org/TR/WCAG22/#resize-text |
| 1.4.5 | https://www.w3.org/TR/WCAG22/#images-of-text |
| 1.4.10 | https://www.w3.org/TR/WCAG22/#reflow |
| 1.4.12 | https://www.w3.org/TR/WCAG22/#text-spacing |
| 1.4.1 | https://www.w3.org/TR/WCAG22/#use-of-color |
| 1.4.3 | https://www.w3.org/TR/WCAG22/#contrast-minimum |
| 1.4.11 | https://www.w3.org/TR/WCAG22/#non-text-contrast |
| 2.4.2 | https://www.w3.org/TR/WCAG22/#page-titled |
| 2.4.3 | https://www.w3.org/TR/WCAG22/#focus-order |
| 2.4.4 | https://www.w3.org/TR/WCAG22/#link-purpose-in-context |
| 2.1.1 | https://www.w3.org/TR/WCAG22/#keyboard |
| 2.1.2 | https://www.w3.org/TR/WCAG22/#no-keyboard-trap |
| 4.1.2 | https://www.w3.org/TR/WCAG22/#name-role-value |

Note: since the deck says "WCAG 2.1 AA," linking to the 2.2 TR as canonical is still correct — 2.2 is backward-compatible and contains every 2.1 criterion at the same anchors (only 4.1.1 Parsing was removed, and it isn't in the matrix). Deva's checklist is already 2.1+2.2 scoped, so this also aligns the deck with her sheet.

## 7. Drawer comparison blocks — Deva's Excel verdict vs. ours, per rule (paste-ready)

Format in every drawer, directly under the badge sentence — her words first, verbatim from the checklist, then ours:

> **Deva's checklist:** `<Validation Approach>` · "<her How-to-Test note>"
> **Our conclusion:** `<Agree / Augment / Disagree (documents)>` — one-line reason.

**1.1.1 Non-text Content**
Deva: **Automated + Agentic** · "Check alt text; verify with a screen reader (NVDA/VoiceOver); confirm decorative images use null alt / aria-hidden."
Ours: **Agree** — alt *presence* is deterministic in the file; alt *quality* is the agentic half, exactly her split.

**1.3.1 Info and Relationships**
Deva: **Automated + Agentic** · "Inspect semantic markup/ARIA; screen-reader test; automated scan (axe)."
Ours: **Agree** — document translation: header rows / heading skips / PDF tags deterministic; correctness of relationships is the agentic remainder.

**1.3.2 Meaningful Sequence**
Deva: **Human / AT** · "Disable CSS or use a screen reader to verify order."
Ours: **Disagree (documents)** — right for web (order lives in the rendered DOM); in PPTX/PDF/XLSX the reading order is written into the file, so machines detect mismatches and a person confirms. Documents beat her class here.

**1.3.3 Sensory Characteristics**
Deva: **Automated + Agentic** · "Manual review of instructional text."
Ours: **Agree + augment** — detectable without an LLM: deterministic pattern check (shipped) finds "click the round button"-style phrasing reproducibly; human confirms.

**2.4.6 Headings and Labels**
Deva: **Automated + Agentic** · "Review heading/label text."
Ours: **Agree** — structure (skips, empties) deterministic; *descriptiveness* agentic. The canonical split rule.

**3.1.1 Language of Page**
Deva: **Automated** · "Inspect <html lang>."
Ours: **Agree** — deterministic in all four document formats (core-properties / settings / PDF /Lang). No caveats.

**3.1.2 Language of Parts**
Deva: **Automated** · "Inspect lang on foreign-language content."
Ours: **Disagree (nuance)** — her test only verifies passages already marked. Finding *unmarked* language changes needs ML language-ID + human confirm — her own Automated + Agentic class, not Automated.

**1.4.4 Resize Text**
Deva: **Automated** · "Zoom browser to 200%; check for clipping/overlap."
Ours: **Disagree (documents)** — browser technique with no document equivalent; viewers zoom natively. N/A for files; her class stands for web.

**1.4.5 Images of Text**
Deva: **Automated** · "Identify text rendered as images."
Ours: **Augment** — automatable, but via OCR (ML) with thresholds, and the "essential" exception (logos) is judgment → machine-detected + human-confirmed.

**1.4.10 Reflow**
Deva: **Automated** · "Zoom to 400% / 320px viewport; check for horizontal scroll."
Ours: **Disagree (documents)** — viewport test is web-only. Fixed-layout OOXML: N/A. PDF: tagged-structure presence is the honest machine proxy.

**1.4.12 Text Spacing**
Deva: **Automated** · "Apply text-spacing bookmarklet; check for clipping."
Ours: **Disagree (documents)** — bookmarklet is web-only; user spacing overrides aren't a document-author obligation. N/A for files.

**1.4.1 Use of Color**
Deva: **Human / AT** · "Manual review; grayscale check."
Ours: **Agree + augment** — agree today; her grayscale check is exactly the future machine assist (render-and-diff), which would lift this to machine-detected later.

**1.4.3 Contrast (Minimum)**
Deva: **Automated** · "Use a contrast analyzer on text/background pairs."
Ours: **Agree + augment** — the ratio math is deterministic; in documents the hard part is resolving *effective* colors (themes, fills). Where colors resolve → certified; where not → review, never a silent pass.

**1.4.11 Non-text Contrast**
Deva: **Automated** · "Contrast analyzer on buttons, borders, icons, focus rings."
Ours: **Augment** — on web the analyzer reads computed styles; document shapes/charts need render-and-measure (ML/vision). Her class is the ceiling; today it's human for files.

**2.4.2 Page / Doc Titled**
Deva: **Automated** · "Inspect the <title> element."
Ours: **Agree** — deterministic in all four formats, shipped both directions. (Note: "descriptive" titles are judgment — same remainder she assigns 2.4.6.)

**2.4.3 Focus Order**
Deva: **Human / AT** · "Tab through; verify logical order."
Ours: **Agree + augment** — agree for anything interactive. OOXML has no focus order (N/A); PDF *forms* expose a tab-order key (/Tabs) that is deterministically checkable — a cheap detector her web lens misses.

**2.4.4 Link Purpose (In Context)**
Deva: **Automated + Agentic** · "Review link text ('click here' fails)."
Ours: **Agree** — generic-text detection deterministic (her own example); purpose-in-context agentic. Shipped as exactly that split.

**2.1.1 Keyboard**
Deva: **Human / AT** · "Tab/arrow through all controls with no mouse."
Ours: **Agree + augment** — behavioral where content is interactive. Static DOCX/XLSX: N/A. PPTX: one machine proxy (auto-advancing animations, shipped). PDF forms/scripts: human.

**2.1.2 No Keyboard Trap**
Deva: **Human / AT** · "Tab into and out of every widget/modal."
Ours: **Agree** — documents mostly N/A; PDF-with-scripts human.

**4.1.2 Name, Role, Value**
Deva: **Human / AT** · "Screen-reader test; inspect ARIA; automated scan."
Ours: **Agree + augment** — agree for the full SC; the document slice (do form fields expose a name?) is deterministically checkable (DOCX content-control labels shipped; PDF AcroForm /T · /TU is the same check waiting to be written).

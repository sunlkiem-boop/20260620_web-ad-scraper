# Beliefs Doc Structure — Phase 3 Reference

Save as `<save-path>/<Brand>_<Product>_Beliefs.md` (+ matching `.pdf`).

**Target length:** 10–15 PDF pages (roughly 300–400 lines / 30–35KB).

**Core principle to internalize before drafting:**

> Stop crafting copy, start crafting arguments. The fundamental difference between effective and ineffective marketing isn't power-word choice — it's the magnificence of the argument. Every campaign leads the prospect to a specific belief they must hold before the offer makes sense. That belief becomes your North Star. Word choice matters only when layered on top of a rock-solid logical and emotional argument.

The Beliefs Doc is the argument architecture every ad creative will lean on. Get it right and everything downstream gets easier.

---

## Preflight (run this before writing anything)

```bash
for f in <Brand>_<Product>_VOC_Dossier.md <Brand>_<Product>_Avatar_Sheets.md <Brand>_<Product>_Offer_Brief.md; do
  [ -s "<save-path>/$f" ] && echo "OK: $f" || echo "MISSING: $f"
  grep -c "INCOMPLETE" "<save-path>/$f"   # must be 0
done
```

If any prior file is missing or has `INCOMPLETE` markers, **STOP** and tell the user which one to fix. The Beliefs doc depends on the avatar names from the Avatar Sheets and the 10-step belief chain from the Offer Brief.

---

## Top-of-file boilerplate

```markdown
# <Brand> <Product> — The 6 Beliefs the Prospect Must Hold to Buy

**Source materials:** `<Brand>_<Product>_VOC_Dossier.md` (N verbatim quotes + contextual), `<Brand>_<Product>_Avatar_Sheets.md` (Avatars 1, 2, 3), `<Brand>_<Product>_Offer_Brief.md` (10-step granular belief chain, compressed below into 6 meta-beliefs).

**Brand-approved language anchors used throughout** (preserve verbatim in any installation copy):
- [carry the anchors verbatim from VOC §0.6]

The six beliefs below are the prospect's belief architecture for <Product> specifically. Each independently necessary, in logical-dependency order. If any one collapses, the purchase doesn't happen. The beliefs are universal across the [N] avatars; only the proof points and entry-point belief differ per avatar.

The belief chain reconciles with the Offer Brief's 10-step granular chain — the 6 below are the **meta-architecture**, the Offer Brief's 10 are the **granular installation steps**. See §Reconciliation table at the end.
```

---

## The 6 beliefs — structure for each

Produce **exactly 6 "I believe that..." statements** in logical-dependency order. Each gets the following structure.

### Belief N — [Belief name]

```markdown
> ***"I believe that [the customer-voice version of the belief]."***
```

A 1–2 paragraph introduction explaining what this belief gates and why it's where it is in the dependency order.

Then a per-avatar block:

```markdown
- **Avatar 1 (primary):** [1 paragraph — what version of this belief they hold or partially hold; what the upgrade looks like]. The relevant quote(s) from the VOC dossier:
  > *"verbatim VOC quote"* ([cite link](url))

- **Avatar 2:** [same structure]

- **Avatar 3:** [same structure]
```

Then a brand-approved installation language block:

```markdown
**Brand-approved installation language:**
> *"[Verbatim brand language — the H1 candidate / Dr. Jason Mitchell quote / Senada origin frame / etc. — that installs this belief]"*

Avoid: [verbatim list of phrases not to use here]
```

Optional closing note specific to the belief — e.g. "Why this belief is comparatively easy for [product]" or "Why this belief is the hardest to install."

---

## Architecture default — 6 beliefs in logical-dependency order

A defensible default ordering. **Verify from the VOC data and adjust before locking.** Other categories may need a different ordering.

1. **Belief 1 — Category necessity:** *"I believe that [the convenient / clean / efficient version of this category] is non-negotiable for the goals I have."*
2. **Belief 2 — Current-solution inadequacy:** *"I believe that what I'm currently using isn't actually [clean / effective / safe / sustainable], and the [problem] isn't going to fix itself."*
3. **Belief 3 — A real alternative is structurally possible:** *"I believe that a product solving [problem X] without [bad thing Y] CAN exist — without my [stomach / macros / standards / wallet] paying the price."*
4. **Belief 4 — This product IS that alternative** *(the North Star belief):* *"I believe that [<Product>] delivers what a [clean / efficient / better] [category] should — [the cornerstone spec line] with [the credibility-stack proof points]. Scientifically studied dosages. No pixie-dusting."*
5. **Belief 5 — The price / format / risk-reversal policy is worth it:** *"I believe that [price point + format quirk + guarantee framing] is the right trade — because what I've been paying for so far has cost me more in [pain points] than the price gap."*
6. **Belief 6 — Now is the right time to switch / start:** *"I believe that the cost of continuing what I'm doing is greater than the cost of trying [<Product>] today."*

---

## Reconciliation table — these 6 vs. the Offer Brief's 10

A markdown table mapping the Offer Brief's 10-step granular belief chain to the 6 meta-beliefs above. Example structure:

```markdown
| Offer Brief's granular belief | Meta-belief |
|---|---|
| 1. [Step 1 from Offer Brief belief chain] | **Belief 1** (category necessity) |
| 2. [Step 2] | **Belief 1** (continued) → **Belief 2** (current solution inadequate) |
| 3. [Step 3] | **Belief 2** |
| ... | ... |
| 10. [Step 10] | **Belief 6** |
```

Most granular beliefs map to one meta-belief. A few span the boundary between two — note both.

---

## Copy flow by avatar — where to start the belief chain

The beliefs are installed in **different orders** depending on what the prospect already believes when they arrive. Three sections (one per avatar):

### Avatar 1 — [Name] (PRIMARY)

Beliefs [N, N] are mostly installed when this avatar arrives. The work is concentrated on **Beliefs [N, N]**.

**Copy order:**
1. **Open at Belief [N]** — [validation / math / mechanism — what entry point matches this avatar's mindset]. [Specific creative move.]
2. **Bridge to Belief [N]** — [argument step]
3. **Install Belief [N]** — [proof points specific to this avatar]
4. **Address Belief [N]** — [trade-off resolution]
5. **Close on Belief [N]** — [activation trigger]

**Strongest single belief for this avatar:** Belief [N]. [1-sentence explanation.]

### Avatar 2 — [Name]
[Same structure]

### Avatar 3 — [Name]
[Same structure]

---

## What a single piece of copy needs to do

A closing section that anchors the brand team:

```markdown
## What a single piece of copy needs to do

**A single piece of copy doesn't need to install all 6 beliefs.** Most short-form ads do one. A full long-form sales page or VSL does all six in sequence.

**Belief [N] is the North Star.** Beliefs [N–N] are the dependency tree. Belief [N] is the trade-off resolution. Belief [N] is the trigger. Every sentence in any piece of <Brand> <Product> copy should be testable against *"which of these 6 beliefs am I installing right now?"* If a sentence doesn't move the reader toward one of these 6, it's decoration — and decoration is the "magnificent words" trap the brand explicitly wants to avoid.

**The order each avatar enters the chain at is the single most important creative-routing decision** the brand will make:

- **[Avatar 1]** enters at Belief [N] — and [N]%+ of paid creative budget should serve this avatar at this entry point.
- **[Avatar 2]** enters at Belief [N] — and gets a different headline rotation entirely.
- **[Avatar 3]** enters at Belief [N] — and gets a different creative angle (doctor-led, math-led, lifestyle-led — based on the avatar's psychology).

Mixing these creative routes (e.g., showing [Avatar 2] the [Avatar 1] lifestyle ad) wastes impressions. Sub-creative segmentation matters.
```

---

## Brand-required language anchors block

Close the file with a non-negotiable language reminder block:

```markdown
## A note on the brand-required language anchors

These are non-negotiable. Every belief-installation copy unit MUST preserve these verbatim:

- [carry the verbatim list from VOC §0.6]

And these are red lines — copy that violates them is non-shippable:

- [carry the red-line list from VOC §7]
```

---

## Closing line

```markdown
— End of beliefs document —
```

---

## Final wrap-up after Phase 3

The Phase 3 message MUST surface (in one assistant message at the end):

```
## 1. Deliverables
[4-row table — md path + pdf path + page count for each of the 4 deliverables]

## 2. Total quote count
N numbered verbatim quotes + ~M contextual in the VOC Dossier.

## 3. The 6 locked beliefs (one line each)
1. Belief 1 — [Belief name]: "[the belief statement]"
2. Belief 2 — [name]: "[statement]"
3. Belief 3 — [name]: "[statement]"
4. Belief 4 — [name]: "[statement]" (the North Star)
5. Belief 5 — [name]: "[statement]"
6. Belief 6 — [name]: "[statement]"

## 4. Flagged for brand verification
[Numbered list — Discovery Story specifics, ingredient discrepancies, subscription pricing, retail roadmap, on-camera asset availability, etc.]

Research sprint complete. Standing by.
```

If §0.4/§0.5 of the VOC dossier flagged a contradiction between brand brief and actual product label, that contradiction MUST appear in §4 of the wrap-up.

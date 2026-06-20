# VOC Dossier Structure — Phase 1 Reference

Save as `<save-path>/<Brand>_<Product>_VOC_Dossier.md` (+ matching `.pdf`).

**Target length:** minimum 6 dense pages (aim for 40+ PDF pages / ~15,000 words / 900+ lines of markdown). Hit that depth.

**Target quote count:** 200+ verbatim attributed quotes, numbered sequentially in §3.

---

## Top-of-file boilerplate

```markdown
# <Brand> <Product> — Voice-of-Customer Dossier

**Product:** [one-line spec — flavor, format, macros]
**Macros:** [paste from product page — verify against actual ingredient list]
**Flavors:** [list]
**Source link (brand site):** [URL]
**Methodology:** [one paragraph naming the research streams — direct competitors, adjacent solutions, dietitian roundups, Reddit aggregators, named bloggers, Trustpilot, Amazon 1-star + 5-star, brand testimonial pages, expert rankings, regulatory / advocacy bodies]

**A note on Reddit:** Direct reddit.com fetches may be blocked. Reddit voice cited below is sourced via named aggregators that quote Reddit users with subreddit + username attribution, or via Reddit-equivalent forums.

**Total verbatim quotes captured in this dossier:** 200+ with full attribution.
```

---

## §0 Product Reality Addendum — read this first

This is the **brand-canonical facts layer.** Where the rest of the dossier contradicts §0, §0 wins. §0 is where you document the truth — including any cases where the brand brief contradicts the actual product label.

### §0.1 Brand-approved product facts

- Category descriptor (verbatim brand language)
- Launch date
- Format (size, container material — aluminum vs plastic vs Tetra Pak)
- Macros per unit (verify against label)
- Price ($/unit on sale, full)
- Protein/active ingredient source (verify against label)
- Sweetener system (verify against label — flag any discrepancy with brand claims)
- Stabilizer / inactive ingredients (verify against label — flag any discrepancy with brand claims)
- Flavors at launch
- Channel (D2C, Amazon, retail)
- Source URLs for verification (brand site + OpenFoodFacts + Amazon listing)

### §0.2 The product benefit stack

The 3–5 cornerstone benefits the brand will defend. Phrase each in 1–2 sentences using brand-approved language.

### §0.3 The credibility stack (shared across all SKUs in the brand line)

- Founders / advisors with credentials (names, titles, public-figure following / book authorship / institutional affiliation)
- Press coverage (Forbes / People / Yahoo Life / AthleTech News / etc.)
- Guarantee framing (brand uses "We-Use-It-Ourselves Guarantee"? "30-day money-back"? "Try-it-and-keep-it"?)
- Required brand language anchors ("Scientifically studied dosages" / "No pixie-dusting" / etc.)
- Origin story sentence (the brand's one-liner about how / where it started)
- The "N Principles" / values framework if the brand has one

### §0.4 The 3–5 wedges the product can defend

For each wedge: (1) the verbatim customer-voice that proves the pain exists, (2) why this product wins it.

**Critical:** All wedges must be audited against the verified ingredient list / spec. If a wedge you planned to use turns out to be invalidated by the actual label (e.g. you were going to attack an ingredient your product also contains), document this in §0.5 and substitute a defensible alternative wedge.

### §0.5 What is NOT a wedge — and why

This section saves the brand from itself. List the would-be wedges that the data shows you cannot defend. For each, document the reason.

Example format:
- ❌ NOT [wedge X] — [reason: product contains the ingredient, claim is contested, etc.]
- ❌ NOT [wedge Y] — [reason: too close to competitor's existing positioning]

### §0.6 Required language anchors — preserve verbatim

The exact phrasings the brand uses and the alternatives Claude must NEVER substitute.

---

## §1 Executive Summary — Top 10 insights ranked by copy-actionability

Each insight is a paragraph. Each paragraph:
1. Names the insight in bold
2. Quotes 2–4 verbatim customer-voice supports with citation links
3. Suggests a headline test or copy direction

Rank by **copy-actionability**, not by sentiment. The top insight should produce a testable headline — that's the quality bar.

This section is the brief the brand's CMO reads if they only read 1 page. Make it count.

---

## §2 Persona Snapshots

**2–3 personas.** Each has 5–6 quote panels:

1. **Core belief in one sentence.** *"If I can hit 180g of protein a day without thinking about it, I can stop thinking about it."*
2. **Demographic.** Age band, gender, income range, profession, geographic skew, current product-spend, identities.
3. **Verbatim panel — how they describe their current stack.** 5–8 quotes from the corpus.
4. **Verbatim panel — what they buy [this category] for, specifically.** 5–8 quotes.
5. **Verbatim panel — their objections to ANY product in this category.** 5–8 quotes.
6. **Verbatim panel — their mechanism story (why they would believe this product works).** 3–5 quotes from authority sources / expert framings.
7. **What this means for copy targeting this persona.** 3–4 sentences.

Aim for 10–12 pages of depth across the persona section.

---

## §3 Pain points — the verbatim quote corpus, organized by complaint cluster

**This is where the 200+ quotes live.** Number each quote sequentially. Group by complaint cluster (3A, 3B, 3C...).

Typical cluster groupings:
- §3A The sucralose / artificial-sweetener / aftertaste cluster (THE WEDGE, if applicable)
- §3B The chalkiness / texture / mouthfeel cluster
- §3C The carrageenan / additive / "ultra-processed" cluster
- §3D The lactose / bloating / "made me sick" cluster
- §3E The price-per-unit / "subscription tax" cluster
- §3F The "hidden sugar" / label-vs-claim cluster
- §3G The "adjacent solution fatigue" cluster (what customers do INSTEAD)
- §3H Category-specific cluster (e.g. a trend or format cluster relevant to this product category)
- §3I The "morning ritual / commute" cluster (when / where the product is consumed)
- §3J The competitor-praise corpus (what loyalists actually love — the bar)
- §3K The expert-framework cluster (named expert rankings + commentary)

Each quote follows the format:

```markdown
N. *"verbatim quote"* — Source name + platform ([cite link](url))
```

Example format:

```markdown
17. *"[verbatim quote from customer or review]"* — [Source name + platform](url)
```

---

## §4 Mechanism story — the curiosity + corruption layer

Two sub-sections.

### §4A Lost discovery — where this category came from
Use the Layer 3 framework from `research-framework.md`. One rich story, factually true. Anchor it with named figures and dates — a historical invention, a surprising origin, a forgotten pioneer. The story should make the reader feel like they've been let in on something.

### §4B Fall-from-Eden — how the category got corrupted
The Layer 4 framework. Multi-act story, factually true, named figures and dates. Trace how the category started with promise, then got captured by cheap ingredients, regulatory shortcuts, or commercial compromise.

End each story with a **mechanism narrative paragraph** the brand's long-form copy can lift directly — a 100-word spine that connects the historical arc to the brand's positioning today.

---

## §5 Competitive teardown — by brand

A markdown table with columns:

| Competitor | Main on-pack claim | Primary differentiator | Top 1-star complaint (verbatim) | Top 5-star praise (verbatim) | Price/unit | This product's wedge |

One row per direct competitor. Tertiary mentions get a 1–2 sentence note at the bottom of the table.

**Critical:** the "wedge" column reflects the §0 audit. If your product contains [ingredient X], you cannot claim "no [ingredient X]" as a wedge here.

---

## §6 Trigger event timeline — when does someone start buying

Walk the customer journey from "drifting" to "subscribed loyalist":

- **T-minus 12+ months — Slow drift:** baseline. Customer has the pain but hasn't recognized it.
- **T-minus 6–12 months — First sharp signal:** what's the moment they NOTICE the pain? Per persona.
- **T-minus 3–6 months — Active research:** what's the buyer's Google / TikTok / Reddit pattern?
- **T-minus 1–3 months — Product trial:** what's the buyer's first product attempt? (Usually a competitor.)
- **T-minus 0–30 days — Disappointment OR conversion:** what's the buyer's evaluation framework?
- **T+30–90 days — Subscription decision / price math hits:** at what point does the loyalist or churner pattern lock?
- **T+90+ days — Loyalist conversion:** what does the long-term customer voice look like?
- **Seasonality:** which months are the strongest entry points? Which months are noise (Halloween / December)?

---

## §7 Compliance flags — language the brand must NOT echo

A table with columns:

| Tempting language captured | Where it appeared | Why it's risky | Safer reframe |

Mine the corpus for verbatim customer phrases that the brand will be tempted to echo — but that the FTC, FDA, or competitor legal teams could action. Cover:
- Disease / cure / treat / prevent language
- Conspiracy framing ("Big Pharma is hiding...")
- Specific drug / supplement naming the brand can't claim
- Money-back guarantee framing if the brand doesn't offer refunds
- Tasting / texture claims that over-promise

Target 15–20 rows for a well-researched product.

---

## §8 Source list (consolidated)

Organize by stream. One sub-section per major source category. Every URL the dossier references should appear here, grouped:

- §A Direct competitor stream — [Competitor 1]
- §B Direct competitor stream — [Competitor 2]
- ... (one sub-section per competitor)
- §L Dietitian / journalist / expert-ranking stream
- §M Curiosity + Corruption stream
- §N Persona-specific stream (e.g., GLP-1, perimenopause, postpartum)
- §O Adjacent solutions stream
- §P Forum / Reddit-equivalent stream
- §Q Product-specific (validation of brand claims) — brand site, OpenFoodFacts, Amazon listing, launch press
- §R Cross-referenced from sister-brand dossier (where the credibility stack carries)

---

## Closing line

```markdown
**Total verbatim quotes captured and attributed in this dossier: N+** across §3A–§3K, plus the curiosity/corruption layer in §4, plus the §5 competitive teardown table. Each carries a real attribution URL or named-source citation.
```

Replace N with the actual count — aim for 200+.

---

## Surfacing the summary after Phase 1

After the file and PDF are on disk, surface to the user (in one assistant message):

```
Dossier complete. N verbatim quotes + ~30 contextual across <X> pages.
Top-5 sources: [source 1], [source 2], [source 3], [source 4], [source 5].
File path: <save-path>/<Brand>_<Product>_VOC_Dossier.md (+ .pdf).
```

If §0.4/§0.5 surfaced a contradiction between brand brief and actual product label, FLAG IT in the summary — the brand needs to know before downstream documents lock in the wedge architecture.

Then proceed to Phase 2.

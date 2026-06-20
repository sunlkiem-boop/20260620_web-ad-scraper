---
name: brand-research-sprint
description: Use this skill when the user wants to produce a complete foundational marketing-research package for a consumer product (VOC Dossier + Avatar Sheets + Offer Brief + Beliefs doc — four .md files plus four matching .pdf files). Triggers on phrases like "run a research sprint for [Product]", "create the foundational docs for [Product]", "do the same thing you did for Aonic Fuel for [new product]", "build VOC + avatars + offer brief + beliefs for [Brand]", "research sprint", "foundational marketing research", or when the user pastes a product page / brand brief and asks for a deep VOC + avatar + offer + beliefs workup. The skill produces 4 markdown files + 4 matching PDFs, with 200+ attributed verbatim customer quotes, in a strictly enforced 3-phase sequence (Phase 1 VOC → Phase 2 Avatars+Offer → Phase 3 Beliefs) with file-on-disk-early protocols, hard quote-count minimums, and brand-voice preservation. Do NOT trigger for single-deliverable requests like "just write a VOC dossier", short copy reviews, refinements to existing docs, or anything that isn't a full foundational research sprint.
---

# Brand Research Sprint — VOC + Avatars + Offer + Beliefs

Produce the complete foundational marketing-research package for a consumer product in one sitting: **VOC Dossier → Avatar Sheets + Offer Brief → Beliefs doc**, with matching PDFs. Four deliverables, three phases, one product.

## When to invoke

The skill description above (in YAML frontmatter) is the discovery layer. Once invoked, **always run Phase 0 first** (preflight — gather inputs and non-negotiables), then run Phases 1–3 end-to-end in a single conversation unless context is running low.

If the user has only given a brand name (e.g. "do this for Aonic Race"), Phase 0 confirms: (1) where to save the output, (2) the product spec (or a URL to scrape), (3) which existing brand in `brands/` to use as the format-and-depth quality bar, (4) **any non-negotiables** (legal disclaimers, brand-voice rules, mandatory campaign elements). **Default save location:** `~/meta-scraper/brands/<brand>-<product>/documents/` (kebab-case). **Default quality-bar reference:** `~/meta-scraper/brands/aonic-fuel/documents/` — the bundled Aonic Fuel docs are your format-and-depth quality bar.

## Mental model

The user is building automated ad-creative pipelines per brand. The four foundational documents become the brand-context layer that every downstream ad / email / landing-page generation pulls from. So:

- **VOC Dossier** = the spine. Every quote in every downstream deliverable traces back to a numbered entry here.
- **Avatar Sheets** = the customer atlas. 2–3 avatars, each quote-field cell verbatim from the VOC dossier.
- **Offer Brief** = the campaign architecture (Big Idea, UMP/UMS, headlines, objections, belief chain, funnel, swipes).
- **Beliefs Doc** = the argument architecture. Six "I believe that..." statements in logical-dependency order. Every ad creative leans on this.

Get the VOC right and everything downstream gets easier. Get the VOC wrong and the avatar/offer/beliefs will compound the error.

## Phase 0 — Preflight (ASK FIRST, before any research)

**Always run this phase before Phase 1.** Skipping it is the single most common cause of a deliverable that has to be partially rewritten because the brand's compliance / naming / discount rules surfaced too late.

### Step 0A — Surface inputs + non-negotiables in one `AskUserQuestion` call

Use a single `AskUserQuestion` call with up to 4 questions covering whatever is missing. Always include the non-negotiables question — even if the user volunteered some rules in their invocation prompt, ask explicitly to catch anything else.

Suggested question set (pick the 2–4 that fit the situation):

1. **Save location** — `brands/<brand>-<product>/documents/` (default) or custom path?
2. **Product source of truth** — paste the product URL, or upload the spec sheet, or "use what's in brand.json"
3. **Quality-bar reference** — which existing brand in `brands/` should I mirror for format and depth? (Default: `aonic-complete`)
4. **Non-negotiables** — Are there mandatory rules every ad must follow? (Free-text expected; the user will list them. Examples to prime them: *"FDA structure-function disclaimer, exact brand-name casing, mandatory discount code, EU Health Claims wording, forbidden words"*)

### Step 0B — Categories of non-negotiable to probe for if the user is vague

If the user says "no, nothing special" or gives a thin list, **probe explicitly** for these categories before accepting "none" as the answer — most brands have at least 2–3 hiding in plain sight:

- **Regulatory disclaimers**
  - FDA structure-function disclaimer (US dietary supplements): *"These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease."*
  - EU Health Claims Verordnung (HCVO) — only authorized claims at exact wording (e.g. *"Glucomannan trägt im Rahmen einer kalorienarmen Ernährung zu Gewichtsverlust bei"*)
  - ASA/CAP rules (UK fitness/health) — no "miracle / instant / guaranteed" weight-loss claims
  - TGA (Australia), Health Canada NHP, MHRA wellness claims
- **Brand naming / typography rules** — Almost every brand has one. (e.g. "rocka" lowercase, not "Rocka Nutrition"; "iPhone" not "IPhone"; specific tagline punctuation.)
- **Forbidden words** — *zuckerfrei* when product has natural sugar; *clinically effective* when claims aren't trial-backed; *cures*; *guarantees results*; competitor brand names in paid copy.
- **Soft-claim rewrites** — pairs like *"sättigt 4 Stunden"* → *"Sättigungs-Upgrade"*, *"verbrennt Fett"* → *"unterstützt im Rahmen einer kalorienarmen Ernährung"*, *"clinically effective"* → *"scientifically studied dosages"*.
- **Mandatory campaign elements** — Discount code that must appear on every ad (e.g. "Code NC20" + "-20%"); specific influencer endorsement; mandatory anchor phrase ("Daily Weight Loss Support", "End Fake Health"); legally required footnote (e.g. "with sufficient fluid intake — Glucomannan choking warning").
- **Influencer / paid disclosure** — `#werbung` (DE), `#ad` (UK/US), `Anzeige`, partner-link disclosures.
- **Language / market rules** — DE-first / EN okay sparingly; specific tonalities per market; regional price/discount variation.
- **Avatar exclusions** — populations the brand legally cannot or commercially won't target (children, pregnant women, specific medical conditions).

### Step 0C — Confirm and save

Once the user has answered:

1. Echo the captured rules back as a tight bulleted list (5–12 lines) under the heading *"Non-negotiables I'll thread through every deliverable:"*
2. Ask one final yes/no: *"Anything missing or to remove?"* — Wait for confirmation. (Accept "go" / "looks good" / "yes proceed" as confirmation.)
3. Save to `brands/<brand>-<product>/brand.json` under a top-level `non_negotiables` key (array of strings) and a `compliance_red_lines` key (array of forbidden phrasings with approved replacements). Create `brand.json` if it doesn't exist.
4. If the rules are brand-wide (apply to every product of this brand, not just this SKU), also offer to save a memory file at `~/.claude/projects/-Users-danie-meta-scraper/memory/project_<brand>_brand_rules.md` so future runs auto-inherit them.

### Step 0D — Where the non-negotiables land in each deliverable

Every downstream phase MUST surface these rules. Use this map:

| Deliverable | Section(s) where non-negotiables appear |
|---|---|
| **VOC Dossier** | §0.1 (Product Reality Addendum — top), §0.2 (Non-negotiable language rules — a clearly labeled subsection), §0.6 (Required language anchors — verbatim), §7 (Compliance flags & red lines — full list with approved alternatives) |
| **Avatar Sheets** | Header preamble (sprach-anker block), per-avatar "Trust-anker" bullets, Cross-Avatar table footer with discount/disclaimer hooks |
| **Offer Brief** | Top preamble (Marken-genehmigte Sprach-Anker), Discount-Stack block, every Headline candidate (must show how the non-negotiable threads through), Compliance Red Lines section, "Things to verify with the brand" footer |
| **Beliefs doc** | Top preamble, every belief installation-language block (the verbatim copy must respect the non-negotiables), final "Required language anchors" + "Red lines" pair-list |

If a non-negotiable is a mandatory discount code or claim that must appear on **every** ad, also explicitly add a *"How the [code/disclaimer] lands in every belief installation"* table at the end of the Beliefs doc — like the rocka NC20 example.

### Step 0E — Phase 0 exit criteria

Before proceeding to Phase 1, all of the following must be true:
- [ ] Save location confirmed
- [ ] Product source of truth confirmed (URL or spec)
- [ ] Quality-bar reference brand confirmed
- [ ] Non-negotiables captured (or explicitly confirmed as "none")
- [ ] User has confirmed the echo-back list
- [ ] `brand.json` written with `non_negotiables` + `compliance_red_lines` keys (or updated if it existed)

Only then proceed to Phase 1.

## The three phases — execute in order

**Each phase has its own preflight, work cycle, and file-on-disk discipline. Do not skip phases. Do not collapse phases. Phase 2 needs Phase 1; Phase 3 needs Phases 1 and 2.**

### Phase 1 — VOC Dossier

Read `reference/voc-dossier-structure.md` for the §0–§8 structure and quality bar.
Read `reference/research-framework.md` for the research questions (demographic, attitudes, hopes/dreams, victories/failures, outside forces, prejudices, core beliefs; existing solutions, like/dislike, horror stories; curiosity / lost-discovery; corruption / Fall-from-Eden).

**Anti-laziness contract:**
- Plan for **40+ targeted web searches** and **200+ verbatim attributed customer quotes**. Do not compress.
- Every quote needs a real source URL or named attribution. **Never invent quotes.**
- No hedging language ("often", "many say"). Verbatim is the entire value.
- Depth > polish.

**File-on-disk-early protocol** (this is the most-violated rule — pay attention):
1. As soon as you have enough raw material for §0 (Product Reality Addendum) and §1 (Executive Summary), **immediately call `Write` to create the file**. Do not wait until you have §2/§3 drafted in working memory.
2. Then extend with §2 (persona snapshots), §3 (pain-point corpus), §4 (mechanism / curiosity / corruption), §5 (competitive teardown), §6 (trigger event timeline), §7 (compliance flags), §8 (source list). Save after every meaningful chunk.
3. Generate the matching `.pdf` (see "PDF generation" below).
4. Surface a one-line summary: quote count, top-5 sources, file path.

**End-of-turn protocol:** If your turn is winding down (long tool runs, large outputs, fatigue), STOP writing new content, SAVE what you have with an `INCOMPLETE — §X missing` header note, exit cleanly. A partial file on disk is recoverable; a turn that ends with nothing on disk is not.

**Auto-continue handling:** A system "Continue from where you left off" ping = the user asking you to keep going. Don't respond "no response requested" and stop — that abandons the work.

**Verify the product is real before quoting:** Before writing §0, fetch the actual product page (`aoniclife.com` / brand site / Amazon listing / OpenFoodFacts) and validate the ingredient list, price, format. If the brand-brief claims contradict the public ingredient list (e.g. "no artificial sweeteners" but the label shows sucralose, or "no carrageenan" but the stabilizer blend contains it), **document the contradiction in §0.5 and adjust the competitive wedges accordingly.** This is the single most-important guardrail — getting the wedge architecture wrong here means the brand's ad copy will self-own.

### Phase 2 — Avatar Sheets + Offer Brief

**Preflight check:**
```bash
ls -la <save-path>/<Brand>_<Product>_VOC_Dossier.md
grep -c "INCOMPLETE" <save-path>/<Brand>_<Product>_VOC_Dossier.md  # must be 0
grep -c "^[0-9]\+\. \*\"" <save-path>/<Brand>_<Product>_VOC_Dossier.md  # should be 150+
```

If the VOC dossier is missing, incomplete, or has fewer than 150 numbered quotes, STOP and tell the user which deliverable to back up to. Do NOT proceed without a complete VOC.

Read `reference/avatar-sheet-template.md` and `reference/offer-brief-template.md` for the structure of each deliverable.

**Anti-laziness contract:**
- 2–3 avatars. Pick the ones the VOC data actually supports. Don't force ones the data doesn't back.
- Every quote-field cell in every Avatar Sheet is **verbatim from the VOC dossier with traceable attribution**. If a field's quote isn't in the dossier, do a top-up search rather than invent.
- The Offer Brief must fill **every template field** — Big Idea, Metaphor, UMP, UMS, Guru, Discovery Story (flag uncertain), Product spec, 8–12 headlines, ALL objections with answer scripts, 10-step belief chain, 3-tier funnel architecture, 5–8 domain candidates, real-ad swipes, brand-voice red lines.
- Preserve the brand's verbatim language anchors throughout (carry from VOC §0).

**File-on-disk-early protocol:**
1. Write the Avatar Sheets first (depends on VOC personas, not on Offer Brief).
2. Generate the Avatar Sheets PDF.
3. Write the Offer Brief.
4. Generate the Offer Brief PDF.
5. Surface a one-line summary per deliverable: page count, avatars chosen, top-3 headline candidates.

### Phase 3 — Beliefs Doc

**Preflight check:**
```bash
for f in <Brand>_<Product>_VOC_Dossier.md <Brand>_<Product>_Avatar_Sheets.md <Brand>_<Product>_Offer_Brief.md; do
  [ -s "<save-path>/$f" ] || echo "MISSING: $f"
  grep -c "INCOMPLETE" "<save-path>/$f"   # must be 0 for each
done
```

If any prior file is missing or incomplete, STOP and tell the user which one. Do NOT proceed.

Read `reference/beliefs-doc-structure.md`.

**Anti-laziness contract:**
- Produce exactly **6 "I believe that..." statements** in logical-dependency order.
- For each belief: customer voice → which avatar hasn't accepted it → brand-approved installation language → per-avatar copy-order flows.
- Pull quotes from the VOC dossier to evidence each belief. Use the actual avatar names from the Avatar Sheets.
- Build the reconciliation table mapping the 6 meta-beliefs to the Offer Brief's 10 granular belief-chain steps.
- Build the per-avatar copy-flow sections — where each avatar enters the chain, which beliefs they already hold, which are the conversion gates.

**Architecture guidance (verify from the data — VOC research might point to a different ordering):**
1. Category necessity — convenient clean version of the category is non-negotiable for the goals I have
2. Current-solution inadequacy — what I'm currently using isn't actually clean / isn't working
3. A real alternative is structurally possible (without the bad-thing)
4. **Product IS that alternative** (the North Star belief)
5. The price / format / risk-reversal policy is worth it
6. Now is the right time to switch / start

**Final wrap-up after Phase 3:**
1. All 4 deliverables and their paths (md + pdf)
2. Total quote count across the dossier
3. The 6 locked beliefs in one line each
4. Anything flagged for verification (e.g. uncertain Discovery Story, contradictions between brand brief and public ingredient list, missing assets to confirm with brand)

## Brand-voice preservation — non-negotiable

Every brand has verbatim language anchors that must be preserved across all four deliverables. These come from two sources, in priority order:

1. **Phase 0 captured non-negotiables** (highest authority — the user supplied them this session). Stored in `brand.json` under `non_negotiables` and `compliance_red_lines`.
2. **Brand-existing reference docs** (the user's "quality-bar reference") — extract additional language anchors at the start of Phase 1 to complement Phase 0.

Examples from the Aonic line:

- *Scientifically studied dosages* (NEVER "clinically effective")
- *No pixie-dusting*
- *We-Use-It-Ourselves Guarantee* (brand does NOT offer refunds — risk-reversal substitute)
- *Zero artificial sweeteners* / *Zero grams added sugar*
- *Real cocoa* / *real vanilla* (NEVER "natural flavor")
- *Complete protein* / *complete amino acid profile*
- *Made in USA with globally sourced ingredients*
- *End Fake Health* (Senada Greca's mission framing)
- *From our small space in San Francisco, we're redefining the health and wellness space...*

Extract the equivalent anchors for the new brand from `brand.json`, the brand site, prior press releases, and reference docs. Document them in VOC §0.6 and reuse verbatim in §7 (compliance flags), in every Offer Brief headline, and in every Beliefs-doc installation-language block.

## Research protocol — how to actually hit 200+ quotes

You will not hit the quota by doing 10 wide searches. Hit it by doing 40+ narrow searches in parallel waves.

**Wave 1 — Direct category competitors (each gets its own narrow search):**
- For each direct competitor: "[Brand] reviews complaints reddit", "[Brand] [specific-ingredient] aftertaste", "[Brand] 1-star Amazon reviews", "[Brand] vs [Brand-2]", "[Brand] dietitian roundup".
- WebFetch the brand's testimonial page and the top three review aggregators.
- Capture both 5-star praise (the bar Aonic Fuel must clear) AND 1-star complaints (the wedge ammunition).

**Wave 2 — Adjacent solutions** — what the customer is doing INSTEAD of buying the product. For protein shakes: Greek yogurt, cottage cheese, eggs, bars, smoothies. For supplements: pill stacks, food-first approaches. Each adjacent solution gets its own search wave.

**Wave 3 — Named expert / dietitian rankings** — Mike Israetel, Abbey Sharp, NYT/Wirecutter, Healthline, Today's Dietitian, Forbes Health. The framing these experts use is the framing your audience inherits.

**Wave 4 — Reddit / forum aggregators** — direct `reddit.com` fetches may be blocked. Use named aggregators that quote Reddit users with subreddit + username attribution (Useful Vitamins, RedditRecs, Daily Meal, Yahoo Lifestyle "via r/[sub]"), and Reddit-equivalent forums (BodyBuilding.com, AnandTech, Ketogenic Forums, ResetEra).

**Wave 5 — Curiosity / Lost-discovery layer** — at least one rich story. For protein: cosmonaut rations, Metrecal, Carnation Instant Breakfast. For supplements: Linus Pauling, ancient herbal traditions, the multivitamin's origin. Use Wikipedia + named medical-history blogs.

**Wave 6 — Corruption / Fall-from-Eden layer** — at least one rich story. For protein: sucralose's accidental discovery + FDA approval path, carrageenan's GRAS history, ultra-processed creep, the GRAS loophole. The story must be true; the editorial frame is yours.

**Wave 7 — Trigger-event color** — the moment a customer quits the incumbent and starts shopping. Search "I quit [Brand]" / "stopped drinking [Brand]" / "[Brand] gave me [symptom]". These are the canonical persona-voice quotes.

If a fetch is blocked, switch to a named aggregator that quotes the same content. If aggregators are also blocked, document the gap honestly in the source map (`§8`) — don't fabricate.

## PDF generation

Each `.md` gets a matching `.pdf`. The renderer is at `scripts/render_pdf.py` — uses `markdown_pdf` (a Python lib that wraps PyMuPDF). It is preinstalled in the bundled virtual environment at `~/.meta-scraper-venv`.

Invocation pattern:
```bash
~/.meta-scraper-venv/bin/python <skill-dir>/scripts/render_pdf.py \
  <save-path>/<Brand>_<Product>_VOC_Dossier.md \
  <save-path>/<Brand>_<Product>_VOC_Dossier.pdf \
  --title "<Brand> <Product> — Voice-of-Customer Dossier"
```

If `markdown_pdf` is not installed, the script falls back to producing an HTML rendering and tells the user to install `markdown_pdf` via `~/.meta-scraper-venv/bin/python -m pip install markdown_pdf`. Other PDF tools (`pandoc`, `wkhtmltopdf`, headless Chrome) are NOT reliably installed on the user's machine — don't reach for them by default.

## Anti-laziness rules — read these every time

These are violations Claude has been observed committing during the Aonic Fuel sprint that produced this skill. Each is listed with the corrective discipline:

1. **"Doing the research without writing the file."** — Write §0 + §1 as soon as the executive summary is sketchable, BEFORE finishing §3/§4. The corrective discipline is: every meaningful chunk of research → save to disk → continue.
2. **"Compressing 200 quotes into 50 with vague sources."** — The quota is 200+ attributed quotes. Vague sources are not attribution. The corrective discipline is: every quote must have a source URL or named attribution, full stop.
3. **"Inventing quotes that fit the narrative."** — Never. If you need a quote for a specific argument and the data doesn't have one, do a top-up search OR flag the gap.
4. **"Generalizing from the wrong category."** — Aonic Complete is a supplement; Aonic Fuel is an RTD protein. AG1 is NOT a Fuel competitor. Check that the competitive teardown reflects the actual category before writing it.
5. **"Echoing the brand's own positioning back as customer voice."** — Brand-approved language goes in §0 and §7. Customer voice in §2 / §3 must be verbatim from real customers — never paraphrase the brand's positioning into a "customer-style quote."
6. **"Self-owning by attacking a competitor on a complaint your product also has."** — Read the actual product page / OpenFoodFacts ingredient list BEFORE writing the competitive wedges. If your product also contains [ingredient X], you cannot attack a competitor on [ingredient X].
7. **"Skipping the compliance flags section."** — §7 is the section that prevents the brand from getting an FTC letter. Always populate it.
8. **"Stopping after Phase 1 with an apologetic 'standing by'."** — The skill is invoked to produce all four deliverables. Continue to Phase 2 and Phase 3 in the same conversation unless the user explicitly stops you.
9. **"Skipping Phase 0 because the user 'seemed clear enough'."** — Always run Phase 0. Even if the user volunteered some rules in their invocation prompt, ask explicitly — the most expensive bug pattern is a deliverable that breaches a non-negotiable (FDA disclaimer missing, wrong brand-name casing, mandatory code absent) and has to be partially rewritten. 90 seconds of asking saves 30 minutes of rewriting.

## TodoWrite discipline

Use `TodoWrite` aggressively. The sprint has 15–20 discrete tasks across the three phases. Track them. Update status as you go. The user will scan the todo list to see what's done — keep it clean.

A starter todo list (adapt per product):
1. **Phase 0** — Ask for inputs + non-negotiables via `AskUserQuestion`, echo back, save to `brand.json`
2. Read brand quality-bar reference docs (skim only, format/depth pattern)
3. Read Research Framework (research-framework.md in skill reference dir)
4. Verify product's actual ingredient list / specs (brand site + OpenFoodFacts + Amazon listing)
5. VOC research Wave 1 — direct competitor reviews
6. VOC research Wave 2 — adjacent solutions
7. VOC research Wave 3 — dietitian / expert rankings
8. VOC research Wave 4 — Reddit / forum aggregators
9. VOC research Wave 5 — curiosity / lost-discovery
10. VOC research Wave 6 — corruption / Fall-from-Eden
11. Write §0 + §1 (file-on-disk-early!) — **§0 must reflect Phase 0 non-negotiables verbatim**
12. Extend with §2 personas
13. Extend with §3 pain points
14. Extend with §4–§8 (compliance section §7 lists every Phase 0 red line)
15. Generate VOC Dossier PDF
16. Phase 2 preflight + Avatar Sheets (Phase 0 anchors threaded through header + per-avatar bullets)
17. Generate Avatar Sheets PDF
18. Offer Brief — every field; Phase 0 anchors in every headline + Red Lines section
19. Generate Offer Brief PDF
20. Phase 3 preflight + Beliefs Doc (Phase 0 anchors in every belief installation block)
21. Generate Beliefs PDF + final wrap-up

## Output discipline

When you finish, surface (in one assistant message):
1. **4 deliverables** — relative paths to all 8 files (4 md + 4 pdf)
2. **Total quote count** — the headline number for §3 of the dossier
3. **6 locked beliefs** — one line each
4. **Verification flags** — anything you scaffolded with a best-guess that the brand should validate

Then stop. The user will move on to the ad-creative pipeline that consumes these documents.

---

## Skill files

- `SKILL.md` — this file (orchestration instructions)
- `reference/research-framework.md` — the research-question framework (demographic / hopes-and-dreams / existing-solutions / curiosity / corruption)
- `reference/voc-dossier-structure.md` — §0–§8 structure with quality-bar examples
- `reference/avatar-sheet-template.md` — the avatar-sheet structure with every required field
- `reference/offer-brief-template.md` — the offer-brief structure with every required field
- `reference/beliefs-doc-structure.md` — the beliefs-doc structure (6 statements + reconciliation + per-avatar flows)
- `scripts/render_pdf.py` — markdown → PDF renderer

Read the reference files only when you reach that phase. Don't pre-load them all into context — they're long.

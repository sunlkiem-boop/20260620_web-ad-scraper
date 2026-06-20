---
name: scrape-meta-ads
description: Use this skill whenever the user pastes a Meta Ad Library URL (any URL containing "facebook.com/ads/library") or asks to scrape, audit, or analyze a brand's currently-active Meta / Facebook / Instagram ads. Triggers on phrases like "analyze these Meta ads", "what ads is [brand] running right now", "pull the ads from this Ad Library link", "scrape this brand's ads", or just a bare facebook.com/ads/library URL with no other instruction. The skill captures every active ad as a PNG, writes a detailed visual analysis of each (color palette with hex codes, typography, layout, copy verbatim, CTA, mood, style), and produces a self-contained Uplane-branded HTML report ready to upload to Netlify / S3 / GitHub Pages. Do NOT trigger for TikTok, Google, or LinkedIn ads, generic Facebook page analysis without an Ad Library URL, or analysis of static image files that aren't from the Meta Ad Library.
---

# Scrape Meta Ads → Visual Analysis → Brand-Adapted Generation Prompts → Uplane Report

Capture a competitor's currently-active Meta ads, analyze each one, and — for every static ad — produce a ready-to-paste image-generation prompt tailored to a customer brand. Output a portable, Uplane-branded HTML report.

## Mental model

The user is an agency / creative team. For each of their **customers** they have a brand profile + 4 foundational documents (strategy, copy, audience, creative direction). The workflow is: scrape a competitor → analyze → for each competitor static ad, write a prompt that recreates the same visual concept but fully branded for the user's customer.

The user pastes the resulting prompt into a text-to-image model along with two attached images: (a) the competitor ad as a layout/style reference, and (b) the customer's product photo. So each generation prompt must be written assuming both attachments will be present.

You contribute the part only a multimodal model can do well: looking at each ad, understanding the brand profile + foundational docs, and writing a concrete, useful prompt that adapts the competitor's creative concept for the customer.

Don't reinvent the scraping logic. Don't build a server. Don't add intermediate UI. Just: scrape → analyze → write prompts → render.

## Workflow

### 0. Identify or set up the customer brand

Customer profiles live at `~/meta-scraper/brands/<slug>/`. Each contains:

```
~/meta-scraper/brands/<slug>/
├── brand.json                   metadata (name, niche, product, language, etc.)
├── current_state.md             OPTIONAL — live, fast-changing facts (price, current promos, scarcity)
├── documents/                   the 4 foundational docs (PDF / md / txt)
├── <product_image_filename>     high-quality product photo
├── <logo_light_bg_filename>     OPTIONAL — brand logo for light backgrounds
└── <logo_dark_bg_filename>      OPTIONAL — brand logo for dark backgrounds
```

`brand.json` fields for the optional reference assets:

```json
{
  "product_image_filename": "aonic-fuel-rich-chocolate.png",
  "logo_light_bg_filename": "aonic-logo-light-bg.png",
  "logo_dark_bg_filename":  "aonic-logo-dark-bg.png"
}
```

Both logo fields are optional. When set and the files exist in the brand folder, `build_report.py` embeds each as a base64 data URL and renders it as its own tile in the customer-context card at the top of the report, with a per-tile "Copy" button. The dark-bg tile draws on a deep navy background so a white-on-transparent logo stays legible. Tiles for missing files are silently skipped.

### `current_state.md` (optional, lightweight)

A free-form markdown file for facts that change too often to live in `brand.json` or in the foundational docs: current price, an active promo / discount, a limited drop, a temporary scarcity note, brand-asset reference notes (logo, packaging, secondary marks), anything else that should be woven into every prompt for the next few weeks. Update it inline; the foundational docs stay untouched.

When this file exists, **read it after `brand.json` and treat any "Always include in every prompt" instructions in it as binding for every recreate and reimagine prompt you write**. Typical contents look like:

```markdown
# Brand — current state (2026-05-18)

## Current promo
30% off first order, no code required (live until 2026-06-15).

## Always include in every prompt

### 1. The 30 percent off promo
Weave "Get 30% off today" (or a brand-voiced equivalent) somewhere visible in the ad, sized so it reads at thumbnail scale without crowding the product.

### 2. The brand logo reference
The user attaches the brand's parent logo as an extra reference image alongside the competitor ad and product photo. Every prompt must instruct the model to use it. Phrasing for this brand:
> Add the {brand} logo (just {parent mark}, not {sub-mark}) from the reference image somewhere suitable.
```

A `current_state.md` directive typically covers one of two patterns:

- **An overlay element** (a promo chip, a scarcity badge, a launch sticker). Describe what to add as on-image text and roughly where it should sit.
- **A reference-image directive** (a brand logo, a packaging cue, a secondary mark). Phrase it so the prompt tells the image model which attached reference to pull from. Use the wording "from the reference image" so it stays distinct from the product photo reference, and place it right before "All overlay text in English." in every prompt.

If the file is missing or empty, just skip this step.

Resolution order — **always try these in order** before giving up:

1. **User named an existing customer.** If the user mentions a customer slug or name that matches a folder under `~/meta-scraper/brands/`, use it.
2. **Only one profile exists.** If there's just one folder under `~/meta-scraper/brands/`, use it as the default.
3. **User wants to set up a new customer.** Triggers like *"set up customer X"*, *"add a new customer"*, *"this is for Brand X, here's their site: <url>"*, or just naming a customer that doesn't exist yet — you should handle the entire setup inline. Do not ask the user to run `init_brand.py` themselves. See [§ Setting up a new customer](#setting-up-a-new-customer) below.
4. **No profiles exist and no customer named.** Ask the user who this is for. Once they answer, fall through to step 3.

Once you've resolved the customer slug, **read `brand.json` and ALL files in `documents/`** into context using the `Read` tool. PDFs are supported natively. For multi-page PDFs over 10 pages use the `pages` parameter to read in chunks.

This step is critical: the foundational documents shape the audience targeting, tone, and credibility claims that go into every generation prompt. Don't skip them.

If the user explicitly says they don't have a customer profile yet and just want a pure competitor analysis, you can still run the skill — the report will skip the per-ad prompt section. Tell them that's what's happening so they're not surprised.

#### Setting up a new customer

When the user wants to onboard a new customer (or implies it), do this **automatically** — don't dump instructions on them, just do it.

**Step A. Get the website URL.** If the user gave you a URL ("set up customer Aonic, https://aoniclife.com"), great. If not, ask once: "Got a website URL for them? I'll pull the brand details from there." If they don't have one, ask them for: brand name, niche, what they sell + to whom, flagship product name, product format, and language — then skip Step B.

**Step B. Fetch the site.** Use the `WebFetch` tool on the customer's URL with this prompt:

> Extract for a creative-intelligence brief: (1) brand name with exact spelling, (2) niche / category in 2–4 words, (3) one-sentence description of what they sell and to whom, (4) flagship product name(s) and product format, (5) primary language, (6) brand tone descriptors, (7) any visible claims / proof points / press mentions / scientific or medical advisors, (8) DTC / B2B / B2C model. Be concrete and quote exact product names.

**Step C. Scaffold the folder.** Pick a slug from the brand name (lowercase, hyphenated, ASCII). Run:

```bash
~/.meta-scraper-venv/bin/python ~/.claude/skills/scrape-meta-ads/scripts/init_brand.py <slug> --name "<Display Name>"
```

**Step D. Populate `brand.json`.** Use the `Write` tool to overwrite `~/meta-scraper/brands/<slug>/brand.json` with the full populated profile, including `tone`, `proof_points`, and `product_line` arrays you derived from the WebFetch result. Leave `product_image_filename` empty — the user will drop the file later.

The expected populated shape:

```json
{
  "brand_name": "...",
  "brand_slug": "...",
  "niche": "...",
  "what_you_sell_and_to_whom": "...",
  "product_name": "...",
  "product_type": "...",
  "language": "English",
  "product_image_filename": "",
  "documents_folder": "documents",
  "tone": "...",
  "proof_points": ["...", "..."],
  "product_line": ["...", "..."]
}
```

**Step E. Tell the user what they still need to do.** Two things only:
1. Drop their **4 foundational documents** (PDF / md / txt) into `~/meta-scraper/brands/<slug>/documents/`.
2. Drop a **high-quality product image** into `~/meta-scraper/brands/<slug>/` and tell you the filename so you can update `product_image_filename`.

Don't ask them to edit `brand.json` themselves — you've already populated it. They can edit if they want, but the default should be ready to use.

If after Step E the user immediately wants to scrape something, proceed to step 1 of the main workflow with this customer slug loaded.

### 1. Confirm the URL

The user should give you a Meta Ad Library URL that contains `view_all_page_id=...` in the query string. If it's missing, ask once: "Open the brand's *Pages* result in the Meta Ad Library and copy that URL — I need the one with `view_all_page_id=...`."

If they paste a URL with extra tracking params or different `active_status`, that's fine — the underlying scraper normalizes it to `active_status=active` automatically.

### 2. Run the scraper wrapper

Run this exactly:

```bash
~/.meta-scraper-venv/bin/python ~/.claude/skills/scrape-meta-ads/scripts/run_scrape.py "<URL>"
```

Stream the output to the user — Playwright takes 20–60 seconds and seeing progress is reassuring. The wrapper's last line is:

```
RUN_DIR=<your-home>/meta-scraper/runs/<page_id>-<timestamp>
```

**Capture that path.** Everything else in this workflow lives inside it.

The run dir contains:
- `screenshots/ad-*.png` — full Meta Ad Library card screenshot per ad (Meta UI chrome included). Use this for the verbatim-copy / Library-ID extraction in step 3.
- `screenshots/creative-*.{jpg,png,webp,gif}` — **just the ad creative image**, with no Meta chrome. Downloaded directly from Meta's CDN at native resolution (typically 338×600 JPEG for IG-format static ads — Meta signs the `stp=dst-jpg_sNNN` size hint, so this is the largest size available without Meta auth). Falls back to a rendered element screenshot if the CDN fetch fails. This is what the report displays. **The scraper deduplicates** — when the same creative runs as multiple ad IDs (audience-split testing), the bytes are written once and later manifest entries reuse the same path.
- `manifest.json` — array of `{index, card_png, creative_png, creative_hash, is_video, dest_url}`. `creative_png` may be `""` if extraction failed. `creative_hash` is a 16-char SHA-256 prefix of the creative bytes — entries with the same hash are duplicates of one creative. `is_video` is `true` when the card contains a `<video>` element (the largest `<img>` is then the video poster frame, sans play-button overlay).
- `run.json` — `{page_id, source_url, scraped_at, ad_count}`
- `scraper.log` — full scraper output (for debugging)

If the wrapper exits non-zero, surface the error verbatim. Common modes:
- **"URL is missing view_all_page_id"** — user pasted the wrong URL form, ask them to grab it from the Pages-result page.
- **"No ads found (or Meta blocked the page)"** — either the brand has no active ads, or Meta served a stripped page. Suggest they retry; if it persists, the brand may genuinely have no active ads.

### 3. Analyze each UNIQUE creative and write its generation prompt

**Dedup first.** Group the manifest entries by `creative_hash`. The scraper has already merged duplicate file writes on disk, but the manifest still has one entry per ad ID — and the same creative often appears under multiple IDs (audience-split testing). Don't waste tokens analyzing the same image twice.

Build a list of canonical entries: keep the first (lowest-index) entry per unique non-empty `creative_hash`. Skip later entries with the same hash entirely. Entries with empty `creative_hash` (rare — fallback rasterization failed) get analyzed individually.

For each canonical entry, in manifest order:

1. Use the `Read` tool on `<RUN_DIR>/screenshots/<card_png>` — that's the full Meta Ad Library card. You need it to extract the body copy / link headline / CTA / Library ID **verbatim** (those live in the Meta UI chrome around the creative). Also use it to confirm whether the ad is a video — the manifest's `is_video` flag is the source of truth, but visual confirmation helps.
2. Also `Read` `<RUN_DIR>/screenshots/<creative_png>` for a clean look at the creative itself. That's what the report displays and what the generation prompt will reference.
3. Build the visual-analysis fields — see [§ Visual-analysis schema](#visual-analysis-schema) below.
4. **If a customer profile is loaded**, also write the prompt-generation fields — `concept_breakdown`, `adaptation_notes`, `recreate_prompts` (array), `reimagine_prompt` — see [§ Generation-prompt schema](#generation-prompt-schema) below.
5. Append ONE merged object to your analyses list — keyed by the canonical entry's `index`. Do not add separate entries for duplicate ad IDs that share this hash.

`build_report.py` will automatically collapse duplicate ads into a single card with a small "× N variants" badge — you don't need to do anything else for that. Your analyses array should have exactly as many entries as there are unique creatives.

After processing every ad, write the array to `<RUN_DIR>/analyses.json` and **also copy the customer profile to `<RUN_DIR>/customer.json`** so the report build is self-contained:

```bash
cp ~/meta-scraper/brands/<slug>/brand.json <RUN_DIR>/customer.json
```

Be concrete. "Sans-serif headline" is not enough — say "geometric sans similar to Inter, medium weight, all-caps headline". For colors, sample the actual dominant hues and write hex codes (your eye is good enough for this — exact values aren't critical, but they should reflect the ad). All visible text goes in `headline` / `primary_text` / `cta_text` **verbatim**, including any "Sponsored" label, disclaimers, or small text.

Extract `library_id` from the ad itself — Meta prints "Library ID: 1234567890" near the top of each card. Extract `brand_name` from the advertiser name shown on each ad (it'll be the same across the run). If different ads show different advertiser names (rare — sometimes a parent brand runs ads through sub-brands), use the one shown on the first ad.

### 4. Build the report

Run (with the customer slug if you have one):

```bash
~/.meta-scraper-venv/bin/python ~/.claude/skills/scrape-meta-ads/scripts/build_report.py <RUN_DIR> --customer <customer-slug>
```

If the user gave you a competitor brand name that differs from what shows on the ads (e.g. they want the parent-brand label), pass `--brand "Parent Brand"`.

If you copied `customer.json` into the run dir during step 3, the `--customer` flag is optional — `build_report.py` will pick it up automatically.

The script's last line is `REPORT=/absolute/path/to/<slug>-<timestamp>.html`. That's the deliverable.

### 5. Tell the user

Report:
- The absolute path to the HTML.
- Competitor brand and ad count. If a customer profile was loaded, mention that too: "with generation prompts for *<Customer>*".
- That it's a self-contained file — they can `open` it locally, or drop it on Netlify / S3 / GitHub Pages with no build step.
- Offer `open <path>` to preview it immediately.

## Visual-analysis schema

Each ad's analysis must be a JSON object with these keys. Optional keys can be empty strings or empty arrays — never null, never missing.

```json
{
  "index": 0,
  "library_id": "1234567890",
  "brand_name": "Patagonia",
  "format": "single_image",
  "headline": "Built to last. Built to be repaired.",
  "primary_text": "Our Worn Wear program keeps gear in play and out of landfill...",
  "cta_text": "Shop Now",
  "visual_summary": "Wide editorial photo of a weathered jacket on a mountain hut chair, late-afternoon sun, single line of headline overlaid bottom-left in white, brand wordmark top-right corner.",
  "color_palette": [
    {"hex": "#1a2e4f", "role": "deep navy sky background"},
    {"hex": "#c8a778", "role": "warm jacket tan"},
    {"hex": "#ffffff", "role": "headline & wordmark"},
    {"hex": "#0b1220", "role": "deep shadow"}
  ],
  "typography": "Geometric sans-serif headline, medium weight, generous tracking. Inter / Söhne family. Body copy is the same family at lighter weight. CTA button uses a slightly bolder cut.",
  "style_tags": ["editorial photography", "outdoor lifestyle", "minimal overlay", "natural light", "warm tones"],
  "composition": "Full-bleed photograph, single line of overlay text bottom-left, brand wordmark anchored top-right. Rule-of-thirds: subject in lower-left third.",
  "focal_point": "The worn jacket on the chair — sunlight catches the patched elbow, drawing the eye there first.",
  "mood": "rugged, lived-in, quietly premium",
  "notes": ""
}
```

### Field-by-field guidance

- **`format`** — one of: `single_image`, `video`, `carousel`, `stories`, `text_only`, `reel`. If unsure, pick the closest; if it's clearly something else, write your own short label.
- **`headline`, `primary_text`, `cta_text`** — copy what's actually visible, exactly. Preserve line breaks (use `\n` in JSON). If a field is genuinely absent (e.g. video frame with no overlay text), use `""`.
- **`color_palette`** — 3 to 6 swatches. Order by visual prominence. `role` is short — "background", "headline", "CTA fill", "skin tone", "logo". Hex must be 6-digit `#RRGGBB`.
- **`typography`** — describe the *style* — weight, family suggestion, geometric vs humanist, all-caps vs sentence case. Don't claim to identify exact fonts you can't be sure of; say "Inter / Söhne family" rather than asserting one.
- **`style_tags`** — 3 to 6 short, lowercase tags. Used for cross-ad pattern detection. Examples: `lifestyle photography`, `flat illustration`, `ugc`, `bold sans-serif`, `pastel`, `minimalist`, `meme aesthetic`, `before / after`, `product shot`, `testimonial card`.
- **`composition`** — describe layout structure (where text sits, where logo sits, framing).
- **`focal_point`** — 1 sentence on what catches the eye first.
- **`mood`** — 2–4 comma-separated words.
- **`notes`** — only if there's something specific worth flagging (e.g. "frame from a video — the still doesn't capture the motion", "two ads in this run are near-duplicates with different copy"). Otherwise leave empty.

### Why this schema

The downstream `build_report.py` renders these fields into a clean card layout. If a field is missing or null, rendering falls back gracefully but the card looks thinner. Hitting all the fields makes the report genuinely useful for someone briefing a creative team.

## Generation-prompt schema

When a customer profile is loaded, **add these fields to each static ad's analysis object** (skip videos — generation prompts only make sense for static creatives the user can recreate as a single image).

```json
{
  "concept_breakdown": "1–2 sentences on what the competitor ad does conceptually — the format archetype, what creative pattern it taps into.",
  "adaptation_notes": "1–2 sentences on how you're translating that concept into something for the customer brand — what changes, what stays, what claims/audience anchors you're pulling from the foundational docs.",
  "recreate_prompts": [
    {"angle": "Anti-sucralose wedge", "prompt": "..."},
    {"angle": "Real cocoa / real flavor", "prompt": "..."},
    {"angle": "32g complete protein math", "prompt": "..."}
  ],
  "reimagine_prompt": "A full text-to-image prompt that reworks the concept through the customer's foundational documents."
}
```

You produce **multiple recreate prompts** (each leaning on a different brand angle pulled from `brand.json`'s `proof_points`) plus **one reimagine prompt** per static ad. Skim the customer's proof points and avatar sheets to pick the angles most likely to land for THAT ad's concept and audience, rotating across the run so different ads emphasize different angles.

If the customer profile is set up for single-angle ads (or you genuinely cannot find more than one defensible angle for a given competitor concept), it's fine to emit just one recreate prompt. The schema also accepts a legacy single-string `recreate_prompt` for backward compatibility, but new analyses should always use the array form.

- **`recreate_prompts`** are for speed-to-shipped: faithful adaptations of an ad the user already knows is working. Each prompt is **3–6 sentences, plain prose** — short and surgical. The image model will see both the competitor ad and the customer's product photo as attachments, so the prompt's only job is to (1) name what we're doing, (2) provide the NEW overlay text in the customer's voice, (3) include any state-file directives (e.g. current promo), (4) name the brand identity to switch to. Do NOT re-describe the competitor's visual, layout, typography, or copy — the model is looking at it. Do NOT describe the product packaging — the product image carries it.
- **`reimagine_prompt`** is for when the user wants the *strongest version* of the same idea: same concept, but redesigned through the customer's avatars, beliefs, proof points, and unique mechanism. 1–2 paragraphs of plain prose describing the NEW scene from scratch, anchored in the foundational documents.

Both prompts will be pasted into an image-generation model **with two attachments**: the competitor ad and the customer's product photo. Both prompts must assume both attachments will be present.

### Per-ad check: does the competitor carry a product-specific disclaimer?

Supplement, OTC, beauty, and health brands almost always run an FDA-style or product-specific disclaimer on the ad creative itself, either as a footer line ("These statements have not been evaluated by the FDA…") or as a small asterisk-tagged claim in the corner. Image models tend to reproduce that fine print in the recreate unless told not to.

While analyzing each ad, decide whether the competitor's creative visibly carries a disclaimer. The signals:

- An asterisk (`*`) in the headline or any claim
- A small line of fine-print text at the bottom edge of the creative
- Regulatory boilerplate like "These statements have not been evaluated by the FDA. This product is not intended to diagnose, treat, cure, or prevent any disease."
- A "Clinical" or similar trust badge that's typically paired with a regulatory footnote
- Any supplement/health-claim ad — disclaimers are usually present even when not obvious

If the ad has one, append the directive **`No disclaimer needed.`** to every recreate and reimagine prompt for that ad, placed right before the logo/reference-image directive at the end of the prompt. Skip the directive entirely on ads with no visible disclaimer (pure brand/collab editorial, meme cartoons, clean comparison UI) — adding it there would confuse the model.

This is a per-ad analysis decision, not a brand-level always-include, so it does NOT belong in `current_state.md`.

### Shared principles for both prompts — describe the NEW, not the OLD

The model can see both attachments and has context about the customer brand. Detailed descriptions are redundant and actively *worse* than short directives — they introduce contradictions and confuse the model. Specifically:

- **Don't describe the product.** No "30ml glass dropper bottle", no "shape, label, colors, packaging". Just *"show the {product_name} from the attached product image"*. The image carries every detail you'd otherwise list.
- **Don't describe the reference ad's visual elements.** No "the dark hero background with two converging luminous tubes…". Just *"recreate the attached ad"* / *"use the attached ad as a direct layout reference"*. The model is looking at it.
- **Don't quote or re-narrate the competitor's overlay text.** Don't write "replace the headline `<their headline>` with…" — just write "set the headline to <your new headline>". The model will see what's currently in the ad. Your job is to give it the NEW text in the customer's voice.
- **Don't over-specify brand identity.** *"Match {brand_name}'s brand identity (colors and typography)"* is enough. The product photo and the customer's brand context carry the specifics — only hand-spec hex codes or type families if the foundational docs name them and they meaningfully sharpen the directive.
- **No em dashes — but never say so in the prompt itself.** Em dashes confuse image models when they show up in instruction text (they parse as caesuras). So: don't *use* em dashes anywhere in your prompt or in the overlay copy you propose, AND don't *write* "no em dashes" as a directive in the prompt either. Just write the prompt cleanly with commas, periods, parentheses, "and", or semicolons. The rule lives in the skill, not in the prompt text.
- Spend the prompt on what's *new*, *different*, or *changing* — not on re-narrating what the model is already seeing or can infer.

### How to write a `recreate_prompts` entry

Each entry leans on **one** specific brand angle from `proof_points` and produces an Aonic-Fuel-style recreate using that angle as the wedge. Two core principles:

- **Visual: defer, don't describe.** "Recreate the attached competitor ad for {brand_name}." That's the whole visual brief. The model can see the layout, lighting, composition, typography, and model casting in the attached image. Don't list any of it.
- **Copy: provide the NEW text, don't reference the OLD.** Tell the model what overlay text the new ad should carry, in the customer's own voice (pulled from `brand.json`, `current_state.md`, and the foundational docs). Don't quote, paraphrase, or instruct the model to preserve the competitor's existing copy. The image model can see what's currently in the ad; your job is to give it the new headline, body, and CTA the customer wants to ship.

A typical recreate prompt is **3–6 sentences**, structured as:

1. **Name the goal + the angle.** *"Recreate the attached competitor ad for {brand_name}'s {product_name}, leaning on the [angle, e.g. anti-sucralose] wedge."*
2. **Use the product image.** *"Show the {product_name} from the attached product image."*
3. **Set the brand identity.** *"Replace the wordmark with {brand_name}'s. Match {brand_name}'s brand identity (colors and typography)."*
4. **Provide the new overlay text in the customer's voice.** *"Headline: 'F\*ck You, Sucralose.' Body: '32g complete protein. Real cocoa. Zero artificial sweeteners.' CTA: 'Shop Now.'"* Pull all text from `brand.json` / foundational docs. Translate to `{language}` if the original is in a different language.
5. **Weave in any `current_state.md` directives** (e.g. current promo or scarcity note).
6. **Close.** *"All overlay text in English."* (Never write "no em dashes" as a directive in the prompt; just don't use any em dashes in the prompt or in the overlay copy you propose. See § *Describe the NEW, not the OLD* for why.)

Total length: 3–6 sentences. If it's longer than that, you're describing the scene or paraphrasing competitor copy — cut.

### How to write `reimagine_prompt`

The reimagine prompt's job is to produce an ad that's *stronger than the competitor's*, not just rebranded. It describes the NEW scene from scratch, with active reference to the foundational docs.

Four beats, in order:

1. **Open by naming what we're generating.** *"Generate a social media ad for {brand_name}'s {product_name}."* No product-type description, the product image is attached.
2. **Defer to the example ad for layout/style only.** *"Use the attached example ad as a layout and composition reference, but build the scene fully for {brand_name}."* Don't re-describe what's in the example ad, the model can see it.
3. **Defer to the product photo for product accuracy.** *"Show the {product_name} from the attached product image."* No description of shape, label, colors, or packaging.
4. **Describe the NEW brand-adapted scene** — only the parts you're changing or specifying. Draw actively from the customer's foundational docs:
   - Scene elements that should differ from the competitor (different casting, different setting, different mood, different proof-point placement)
   - Brand visual identity. *"Match {brand_name}'s brand identity (colors and typography)."* Brief directive is enough; the model infers specifics from the attached product photo and the customer's brand context. Only hand-spec hex codes or type families if the foundational docs name them.
   - **Exact NEW text overlays in `{language}`**, claims defensibly grounded in `proof_points` from `brand.json` or specific facts in the foundational documents
   - Logo placement and any small print / credibility text
   - Any `current_state.md` directives (current promo, scarcity note, limited drop)
   - **Strengthen the argument the competitor was making.** Pull in a sharper proof point from the foundational docs, lean on the customer's UMP/UMS, or push the awareness / sophistication level up (if the competitor is making a Level 3 claim, write a Level 4).

The model has both attachments in view. Describe what's *new*, don't re-narrate the reference ad. Never use em dashes anywhere in the prompt or in the overlay copy you propose, and never write "no em dashes" as a directive inside the prompt either; just keep the punctuation clean throughout.

### Things to avoid in BOTH prompts

- No aspect ratio. Always 1:1 — the user's image gen handles this.
- Don't describe the product packaging from scratch — defer to the attached product image.
- Don't pad with generic stock-photo language ("stunning", "beautiful"). Be specific.
- No markdown headings or formatting inside the prompt. Plain prose only — the user pastes it directly.

### Tone & audience

Match the emotional register to the customer's foundational documents. Study the target audience deeply from those documents and ensure each headline, scene choice, and credibility cue speaks directly to their desires, fears, and level of awareness. If the docs name specific proof points (clinical results, ingredient credentials, founder credibility, partnership credentials), pull them in where relevant.

### Example shapes (illustrative, not literal templates)

**A single `recreate_prompts` entry** (3–6 sentences, surgical, NEW text only):

```
Recreate the attached competitor ad for Acme's Renewal Serum, leaning on the "clinical proof" angle. Show the Renewal Serum from the attached product image. Replace the wordmark with Acme's and match Acme's brand identity (colors and typography). Set the headline to "Skin like the day you stopped trying" and the proof line under the product to "clinically tested, NSF-cleaned ingredients." Keep the CTA as "Shop Now." Add a small "30% off your first order" tag in the lower-right corner per current_state.md. All overlay text in English.
```

**`reimagine_prompt`** — 1–2 paragraphs, full scene anchored in the foundational docs (describes the *new* scene, not the reference):

```
Generate a social media ad for Acme's Renewal Serum. Use the attached example ad as a layout and composition reference, but build the scene fully for Acme Skincare. Show the Renewal Serum from the attached product image.

Compose a clean editorial still on a soft cream surface lit with warm late-afternoon side-light. Place the product slightly left of center with a single sprig of dried rosemary trailing past it for tactile warmth. Top-right, a small black classical-serif headline reading "Skin like the day you stopped trying" (anchored in the "I'm done forcing it" insight from the avatar sheets). Below the product, a thin horizontal divider and a one-line proof point in the same typeface ("clinically tested, NSF-cleaned ingredients"). Lower-right corner, a small "30% off your first order" tag per current_state.md. Logo lockup in the opposite corner, no larger than 7% of the canvas. Color palette dominated by cream (#f3e9da), warm tan (#c8a778), and deep charcoal text (#1a1a1a). Match Acme's brand identity (colors and typography). All overlay text in English. Mood: rugged, lived-in, quietly premium.
```

These are illustrative. Your real prompts should reflect what the *specific* customer brand needs.

### Backward compatibility

The report builder accepts three legacy shapes:
- single string `brand_prompt` (very old): treated as the `reimagine_prompt`, recreate block skipped.
- single string `recreate_prompt` (older): rendered as a single Recreate block.
- new array `recreate_prompts` (current): one Recreate block per entry, with the entry's `angle` shown as a chip.

New analyses should always use the array form, even when it contains just one entry.

## Performance & cost notes

- Analyzing 30–40 ads in one pass uses meaningful tokens since each PNG goes into context. That's expected. The scraper caps at `MAX_ADS = 200` by default, but Meta's Ad Library only auto-loads the first ~30 ads on entry and gates the rest behind a "See more" button. The scraper handles both: it scrolls AND clicks "See more" repeatedly until the ad count plateaus or the cap is reached. To raise the cap for a single run, set the env var: `META_SCRAPER_MAX_ADS=500 ~/.meta-scraper-venv/bin/python ~/.claude/skills/scrape-meta-ads/scripts/run_scrape.py "<URL>"`. To raise it permanently, edit the `MAX_ADS` line in `~/meta-scraper/scrape.py`.
- Per-ad analyses should be 2–4 paragraphs of structured content — don't pad. Don't editorialize between ads in the conversation; do all the looking, then dump the analyses array at once.
- Don't re-read PNGs you've already analyzed.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Wrapper says "URL is missing view_all_page_id" | User pasted wrong URL | Ask for the URL from the Ad Library *Pages-result* page |
| Wrapper says "No ads found" | Brand has 0 active ads, or Meta blocked the page | Retry once; if persistent, tell user the brand likely has no active ads |
| Some screenshots are clipped or blank | Card rendered after the screenshot timeout | Note this in the affected ad's `notes` field; don't fail the run |
| `build_report.py` says "missing input file" | Skipped step 3 (didn't write `analyses.json`) | Go back and finish the analyses |
| Brand name in report is wrong | First ad showed sub-brand name | Re-run `build_report.py` with `--brand "Right Name"` |
| No prompt sections in the report | Customer profile wasn't loaded — `--customer` not passed and no `customer.json` in run dir | Re-run with `--customer <slug>`. If the slug doesn't exist yet, scaffold via `init_brand.py` |
| Generation prompts feel generic or off-brand | Foundational docs weren't read deeply enough | Re-do step 3 — `Read` every file in `~/meta-scraper/brands/<slug>/documents/` (with page ranges for long PDFs) before writing prompts |
| Recreate prompt re-describes the competitor's visual or quotes its copy | Treated the prompt as a "transform the old" instead of "specify the new" | Re-read § *How to write a recreate_prompts entry* — the model is looking at the competitor ad as an attachment; your only job is to specify the NEW overlay text in the customer's voice and the brand identity to switch to. Don't quote, paraphrase, or instruct preservation of competitor copy. |
| Prompt contains em dashes | Old habit | Strip them from the prompt and from any proposed overlay copy. Use comma, period, parentheses, "and", or semicolon. |
| Prompt contains the literal directive "no em dashes" | Treated the rule as a model instruction instead of an author rule | Image models parse em dashes as caesuras and get confused when "em dash" appears inside instruction text. The rule lives in the skill, not in the prompt. Remove the directive and just keep the punctuation clean. |
| Prompt over-describes the product, reference ad, or brand identity | Ignored § *Describe the NEW, not the OLD* | Tighten to *"show the {product_name} from the attached product image"*, *"recreate the attached ad"*, and *"match {brand_name}'s brand identity (colors and typography)"*. Let the attachments and brand context carry the specifics. |
| Current promo / pricing isn't reflected in the prompts | Skipped `current_state.md` | Re-read it. Any "Always include in every prompt" directive in that file must show up in every recreate and reimagine prompt for the run. |
| Every recreate leans on the same angle (all "anti-sucralose", all "real cocoa", etc.) | Didn't rotate angles across the run | Each ad gets multiple recreate entries; each entry uses a different angle from `proof_points`. Across the run, the mix of angles should reflect the customer's broader positioning, not a single wedge. |
| Customer name shows wrong in subtitle | Wrong slug, or `brand.json` has placeholder `brand_name` | Edit `~/meta-scraper/brands/<slug>/brand.json` and re-run `build_report.py` |

## Bundled resources

- `assets/report_template.html` — Uplane-branded, Wagetab design-language template with `{{...}}` placeholders. Includes prompt-section CSS + a click-to-copy button.
- `assets/uplane-logo.svg` — Official Uplane logo, inlined into every report so the file stays self-contained.
- `assets/brand_template.json` — Template used by `init_brand.py` when scaffolding a new customer brand profile.
- `scripts/run_scrape.py` — Wrapper that runs the underlying scraper and writes the structured manifest.
- `scripts/build_report.py` — Renders the final HTML report. Loads the customer profile (via `--customer <slug>` or auto from `customer.json` in the run dir) when present.
- `scripts/init_brand.py` — Scaffolds a new customer brand folder under `~/meta-scraper/brands/<slug>/`.

## On-disk layout

```
~/meta-scraper/
├── brands/                                   one folder per customer
│   └── <customer-slug>/
│       ├── brand.json                        metadata Claude reads each run
│       ├── documents/                        4 foundational docs (PDF/md/txt)
│       └── <product_image_filename>          high-quality product photo
├── runs/                                     one folder per scrape
│   └── <competitor-page-id>-<timestamp>/
│       ├── screenshots/                      ad-NN.png (cards) + creative-NN.jpg (creatives)
│       ├── manifest.json                     {index, card_png, creative_png, is_video, dest_url}
│       ├── analyses.json                     visual analyses + generation prompts
│       ├── customer.json                     copy of the customer brand profile (for self-contained re-builds)
│       ├── run.json                          {page_id, source_url, scraped_at, ad_count}
│       └── scraper.log
└── reports/                                  one HTML per scrape, hostable as-is
    └── <competitor-slug>-<timestamp>.html
```

If a user wants design tweaks (different brand color, hide the summary band, etc.), edit `assets/report_template.html` directly — the template uses CSS custom properties so the primary color is one line.

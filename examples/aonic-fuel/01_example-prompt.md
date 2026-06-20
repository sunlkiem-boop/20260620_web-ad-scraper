# What Claude received as input

For the Aonic Fuel sprint, the initial prompt looked roughly like this:

---

> **User:** Run a brand research sprint for **Aonic Fuel**.
>
> Save the four deliverables (VOC Dossier + Avatar Sheets + Offer Brief + Beliefs Doc, each as `.md` + `.pdf`) into `/Users/danie/meta-scraper/brands/aonic-fuel/documents/`. Use `/Users/danie/meta-scraper/brands/aonic-complete/documents/` as the quality-bar reference for format and depth.
>
> Brand context: Aonic Fuel is the new 11 fl oz aluminum-canned protein shake from the Aonic line, co-founded by Senada Greca (MBA, Kim Kardashian's trainer, 7M+ IG followers). Launched April 30, 2026. 32g protein, 5g fiber, 160 calories per can. Lactose-free milk protein isolate. **Zero artificial sweeteners.** Stevia Reb A/D/M + monk fruit. Real cocoa. Chief Medical Advisor: Dr. Jason Mitchell, N.D.

---

## What Claude asked back in Phase 0

> **Claude:** *Before I start — are there non-negotiables that must thread through every deliverable?*

The user answered with the brand-voice list:

- *"Scientifically studied dosages"* (NEVER *"clinically effective"*)
- *"No pixie-dusting"*
- *"We-Use-It-Ourselves Guarantee"* (brand offers no refunds)
- *"Zero artificial sweeteners"* / *"Zero grams added sugar"*
- *"Real cocoa"* / *"Real vanilla"* (NEVER *"natural flavor"*)
- *"Complete protein"* / *"Complete amino acid profile"*
- *"Made in USA with globally sourced ingredients"*
- *"End Fake Health"* (Senada Greca's mission)
- *"From our small space in San Francisco, we're redefining the health and wellness space..."* (origin-story frame)
- FDA Structure-Function Disclaimer on every structural claim

## What Claude did next

1. **VOC research** — 40+ targeted web searches, 200+ quotes collected with source URLs
2. **Product reality check** — verified via aoniclife.com + OpenFoodFacts (found: Aonic Fuel contains carrageenan in the stabilizer blend, so "no carrageenan" is NOT usable as a wedge — explicitly documented in §0.5)
3. **VOC Dossier** written — 141 KB, ~60k words, 9 sections
4. **Avatar Sheets** — 3 avatars based on VOC data
5. **Offer Brief** — every template field, 12 headlines, 13 objections, 10-step belief chain
6. **Beliefs Doc** — 6 meta-beliefs in logical-dependency order, per-avatar copy flows
7. **PDFs** generated for each of the 4 documents

Total elapsed: **~2 hours**, broken down as ~30 min research waves, ~30 min writing the VOC, ~30 min Avatars + Offer, ~30 min Beliefs + PDFs.

## What's in `00_brand-info.json`

The `brand.json` is the minimal structural input the skill consumes:

```json
{
  "brand_name": "Aonic Fuel",
  "niche": "premium clean-fuel canned RTD protein shake",
  "what_you_sell_and_to_whom": "...",
  "product_name": "Aonic Fuel",
  "language": "English",
  "tone": "scientific authority + lifestyle aspiration...",
  "proof_points": ["32g complete protein", "160 calories", ...],
  "product_line": ["Rich Chocolate", "Smooth Vanilla"]
}
```

→ See `00_brand-info.json` for the full file.

---

**Note:** The skill also works without a pre-prepared `brand.json` — Claude will scrape the product page itself and assemble the base structure in Phase 0, then ask you about the gaps. The `brand.json` is just a shortcut that saves the first ~5 minutes.

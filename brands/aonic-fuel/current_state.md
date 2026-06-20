# Aonic Fuel — current state

Lightweight, fast-changing facts that should be woven into every generation prompt for the next few weeks. The foundational documents (avatar sheets, beliefs, offer brief, VOC dossier) stay untouched; this file is the live layer on top.

**Last updated:** 2026-06-19

---

## Current promo

There is **no flat "30% off your first order"** anymore (the old version of this file was wrong). The live offers on aoniclife.com as of 2026-06-19 are:

- **Subscribe & Save, up to 30% off your first month:** the **24-pack** gets **30% off the first month**, the **12-pack** gets **25% off the first month**, then **15% off every order after** on both. (The 30% is 24-pack-specific, not a general deal. See the flag note below.)
- **WELCOME10:** **10% off your first order** (code, any one-time order).
- **Free shipping on all orders.**
- No struck-through / flat sale pricing (all variants' compare-at prices are empty).

## Pricing reference

**12-Pack** (Rich Chocolate / Smooth Vanilla):
- One-time: **$53.99** ($4.50/can) — with WELCOME10: $48.59 ($4.05/can)
- Subscribe & Save: **$40.49 first month** (25% off, $3.37/can), then **$45.89** recurring (15% off, $3.82/can)

**24-Pack** ("Best Value"; Rich Chocolate / Smooth Vanilla / Chocolate & Vanilla):
- One-time: **$107.98** ($4.50/can) — with WELCOME10: $97.18 ($4.05/can)
- Subscribe & Save: **$75.59 first month** (30% off, $3.15/can), then **$91.78** recurring (15% off, $3.82/can)

Best per-can value is the 24-pack subscription first month at $3.15/can. The brand's price-justification framing is net-of-bloat / net-of-aftertaste vs. Premier ($2.30/can), not a price-to-undercut.

## Always include in every prompt

### 1. The promo

> DEFAULT pending your call: I have set the hero promo to **"Subscribe & Save, up to 30% off your first month."** Tell me to switch it to the flat **WELCOME10 (10% off your first order)** or to feature both, and I will swap the chip.

Weave it somewhere visible in every recreate and reimagine prompt. Keep it short and unobtrusive so it reads at thumbnail scale without crowding the product, the headline, or the brand mark. Phrasing options (pick whichever fits the ad's mood):

- "Subscribe & Save, up to 30% off your first month"
- "Up to 30% off your first month with Subscribe & Save"
- "Subscribe & Save and lock in 15% off every order"
- One-time alternative: "10% off your first order with code WELCOME10"

Place it as a small chip, badge, sticker, footer band, or a single discreet line near the CTA. Match the visual weight to the rest of the on-image text. Never make it the dominant element.

### 2. The Aonic logo reference

The user always attaches the **Aonic** logo (the parent brand mark, not the "Aonic FUEL" SKU-specific lockup) as a reference image. Every recreate and reimagine prompt must include a directive instructing the model to use that logo:

> Add the Aonic logo (just Aonic, not Aonic FUEL) from the reference image somewhere suitable.

Place it near the end of the prompt, right before the "All overlay text in English." line. Do not write "Aonic Fuel wordmark" anywhere in a prompt; refer to the brand mark as the "Aonic logo" exclusively.

## Compliance reminders

These already live in the foundational docs; flagged here as a fast-reference:

- Never name a GLP-1 medication by brand (Wegovy, Ozempic, Mounjaro, Zepbound). Use "for people changing how they eat" or equivalent.
- Never use "money-back guarantee." Use "We-Use-It-Ourselves Guarantee."
- Never claim "no carrageenan" (Aonic Fuel contains food-grade carrageenan in its stabilizer blend at scientifically studied dosages).
- Never use "clinically effective." Use "scientifically studied dosages."
- Never use em dashes anywhere.

## Available product image

`product_image_filename` in `brand.json` points to `aonic-fuel-rich-chocolate.png`, the canonical Aonic Fuel Rich Chocolate can.

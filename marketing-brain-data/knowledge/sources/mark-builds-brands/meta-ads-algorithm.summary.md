---
video_id: meta-ads-algorithm
title: "the entire meta ads algorithm explained in 21 mins"
creator: mark-builds-brands
channel: Mark Builds Brands
url: https://www.youtube.com/@markbuildsbrands
upload_date: unknown
duration_seconds: unknown
topics: [Meta ads algorithm, retrieval, light ranking, heavy ranking, auction, total value formula, CTR, conversion rate, Andromeda retrieval phase, learning phase, EMQ, conversions API, creative is targeting, attribution, broad targeting]
---

# the entire meta ads algorithm explained in 21 mins

## TL;DR
Facebook decides which ad to show each user in ~200 ms via a 4-step pipeline (retrieval → light ranking → heavy ranking → auction). Each ad is scored by a formula that compounds bid × estimated action rate (CTR × conversion rate) + user-experience score. Three real takeaways: creative IS targeting, optimize soft metrics + conversion rate together, and Facebook is a for-profit public company that doesn't play by the rules — question everything in their UI.

## Frameworks & models

- **4-step delivery pipeline.** Retrieval (tens of millions → thousands) → Light ranking (thousands → hundreds) → Heavy ranking (hundreds → few competitors, where the value formula is applied) → Auction (highest score wins). All happens in ~200 ms.
- **Total value formula** (Meta, since-removed from their site): `Total Value = (Advertiser Bid × Estimated Action Rate) + User Experience Score`, where Estimated Action Rate = CTR × click-to-conversion-rate for purchase-optimized campaigns.
- **Estimated action rate ≈ all soft metrics rolled up.** Not just CTR — also CPC, CPM, hook rate, hold rate, cost per 3-sec view. All your engagement signals compound here.
- **The user-experience term exists to prevent platform destruction.** Without it, "black-hat savages" would flood Facebook and tank the stock. Poor page/ad reviews → penalized CPMs.
- **Andromeda focuses on retrieval.** It's the AI brain that handles the most data-intensive step. It's grouping similar creatives together (so variations of one concept compete with themselves).
- **Learning phase is theater.** Ads never stop learning; "exiting the learning phase" isn't a real stable state. The fix to volatility is usually just better creatives, not waiting it out.
- **Facebook doesn't play by the rules.** Ban waves, ad rejections, and inconsistent enforcement correlate with Meta's quarterly earnings reports — when revenue tightens, restrictions tighten.

## Key principles

- **Creative is the targeting.** Hook, copy, thumbnail, on-screen demographic, even your landing page all feed Meta's targeting decision in the retrieval step.
- The two halves of the formula: (1) high soft metrics → cheap qualified traffic, (2) high conversion rate → monetize that traffic.
- **Run broad.** Interest audiences and lookalikes barely scale post-Andromeda. Mark uses no custom audiences in retargeting either — just broad with maybe a purchaser exclusion.
- Auto-bid (lowest cost) runs profitable 5-figure and 6-figure day accounts. Don't obsess over bid caps unless they solve a specific constraint.
- Inconsistencies in daily ROAS are normal — especially under ~$1K/day spend. Zoom out to 7-day windows.
- **Send Facebook good data, but don't trust its reports.** Conversions API improves EMQ; third-party attribution (Triple Whale, Hyros, We Track, custom builds) is the source of truth for CPA.
- Mark personally has profitable accounts running at 0 opportunity score and 9.8+ EMQ — both extremes — so don't optimize life around those numbers.
- **Don't listen to Meta's in-account suggestions.** Their job is to extract spend, not maximize your ROAS. Every "lower your CPA by 11%" prompt ruins ads.

## Tactics & playbook steps

1. Optimize for **purchase** events on **sales** campaigns. Other objectives are a waste for ecom 99% of the time.
2. Push CTR by improving the hook — that's the single biggest lever on the formula's first half.
3. Push conversion rate via funnel/page quality — that's the second half. Doing both compounds.
4. Stay **broad**: Advantage+ placements, age 18-65+, both genders unless single-demo product.
5. Don't pause based on one day of bad results — look at 7-day rolling minimum.
6. Implement **Conversions API** for server-side tracking → better EMQ → better long-term optimization.
7. Use third-party attribution as the source of truth for ROAS / CPA, not Meta's reported numbers.
8. Mix variations + new concepts in your testing — variations still get more at-bats per concept, even though Andromeda penalizes near-identical clones.
9. Treat ban waves as a calendar event, not a personal failure — they line up with earnings cycles.

## Signature quotes (verbatim)

- "The creative is the targeting."
- "Facebook is an emotional ass platform, man."
- "Facebook doesn't play by the rules."
- "Question everything."
- "Don't listen to Facebook."

## Tools / resources mentioned

- **Conversions API** (Meta) — server-side event tracking; lives in Events Manager.
- **EMQ (Event Match Quality)** — 1-10 score in Events Manager on the Purchase event.
- **Triple Whale** — third-party ecom attribution.
- **Hyros** — third-party attribution (frequently used for info products too).
- **Wicked Reports**, **We Track** — alternatives.
- **Custom-built attribution** — Mark notes you can "vibe code" your own in a few hours.

## Counterpoints / caveats

- The EMQ-correlates-with-performance claim is *not* something Mark sees in his data. He has profitable accounts at low EMQ and unprofitable ones at high EMQ. Treat EMQ as hygiene, not a lever.
- Cost caps and bid caps work great for some advertisers — Mark isn't anti-manual-bidding, just anti-obsession.
- The 4-step pipeline is from Meta's (now-removed) documentation — directional, not a guarantee.
- Inconsistencies under $1K/day spend are normal. Don't react to them.

## Citations

- [the entire meta ads algorithm explained in 21 mins](https://www.youtube.com/@markbuildsbrands) — Mark Builds Brands

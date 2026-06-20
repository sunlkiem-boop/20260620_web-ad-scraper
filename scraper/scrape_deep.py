#!/usr/bin/env python3
"""Deep capture for the Meta Ad Library — beats DOM virtualization.

The bundled scrape.py paginates ALL cards first, THEN screenshots them by index.
On large advertisers Meta unloads off-screen cards, so the later screenshots
time out (scroll_into_view 4s) and most of the tail is lost.

This script instead scrolls the page in small steps and captures each card
*while it is still rendered*, deduplicating by the creative image URL so the
many audience-split copies of one creative are skipped instantly (no per-card
timeouts). Result: one card+creative per UNIQUE creative, across the whole list.

Reuses scrape.py's helpers so the installed engine is untouched.

Usage:
  META_SCRAPER_MAX_ADS=500 python scrape_deep.py "<url>" <run_dir>
"""
import os, sys, re, json, time, datetime
sys.path.insert(0, os.path.expanduser("~/meta-scraper"))
import scrape  # noqa: E402  reuse helpers/constants
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError  # noqa: E402
from playwright_stealth import Stealth  # noqa: E402
from urllib.parse import urlparse, parse_qs, unquote  # noqa: E402

MAX_ADS = int(os.environ.get("META_SCRAPER_MAX_ADS", "500"))
MAX_SECONDS = int(os.environ.get("META_SCRAPER_MAX_SECONDS", "480"))  # hard wall-clock cap
STAGNANT_STOP = 12          # stop after this many AT-BOTTOM steps with no new creative
STEP_FRAC = 0.55            # scroll this fraction of the viewport per step (overlap so nothing is skipped)

CARD_XPATH = (
    'xpath=//div[.//*[contains(text(),"Library ID")] and .//img]'
    '[not(.//div[.//*[contains(text(),"Library ID")] and .//img])]'
)


def largest_img(card):
    best, best_area = None, 0.0
    try:
        imgs = card.locator("img").all()
    except Exception:
        return None
    for img in imgs:
        try:
            box = img.bounding_box()
        except Exception:
            continue
        if not box or box["width"] < 120 or box["height"] < 120:
            continue
        area = box["width"] * box["height"]
        if area > best_area:
            best_area, best = area, img
    return best


def best_img_url(best):
    url = ""
    try:
        srcset = best.get_attribute("srcset", timeout=1200) or ""
        if srcset:
            cands = []
            for chunk in srcset.split(","):
                parts = chunk.strip().split(None, 1)
                if not parts:
                    continue
                u, w = parts[0], 1.0
                if len(parts) > 1:
                    d = parts[1].strip()
                    if d.endswith("w"):
                        try: w = float(d[:-1])
                        except ValueError: pass
                    elif d.endswith("x"):
                        try: w = float(d[:-1]) * 1000
                        except ValueError: pass
                cands.append((w, u))
            if cands:
                cands.sort(reverse=True)
                url = cands[0][1]
    except Exception:
        pass
    if not url:
        try:
            url = best.get_attribute("src", timeout=1200) or ""
        except Exception:
            url = ""
    return url


def creative_key(url):
    try:
        return urlparse(url).path  # CDN path is stable; query carries size/signature
    except Exception:
        return url


def grab_dest(card):
    dest = ""
    try:
        href = card.locator('a[href*="l.facebook.com"]').first.get_attribute("href", timeout=1200)
        if href:
            real = parse_qs(urlparse(href).query).get("u", [None])[0]
            dest = unquote(real) if real else href
    except Exception:
        pass
    if not dest:
        try:
            for link in card.locator('a[href^="https://"]').all():
                href = link.get_attribute("href")
                if href and "facebook.com" not in href and "fb.me" not in href:
                    dest = href
                    break
        except Exception:
            pass
    return dest


def download_creative(url, ctx, shots, stamp, idx, seen_hashes):
    if not url:
        return "", ""
    try:
        resp = ctx.request.get(url, timeout=20000)
        if not resp.ok:
            return "", ""
        body = resp.body()
        h = scrape.creative_dedup_hash(body)
        if h in seen_hashes:
            return seen_hashes[h], h
        if body[:3] == b"\xff\xd8\xff": ext = "jpg"
        elif body[:8] == b"\x89PNG\r\n\x1a\n": ext = "png"
        elif body[:4] == b"RIFF" and body[8:12] == b"WEBP": ext = "webp"
        elif body[:6] in (b"GIF87a", b"GIF89a"): ext = "gif"
        else: ext = "bin"
        path = os.path.join(shots, f"creative-{stamp}-{idx:03d}.{ext}")
        with open(path, "wb") as f:
            f.write(body)
        seen_hashes[h] = path
        return path, h
    except Exception:
        return "", ""


def main():
    if len(sys.argv) < 3:
        print('usage: scrape_deep.py "<url>" <run_dir>', file=sys.stderr)
        sys.exit(2)
    url = scrape.normalize_url(sys.argv[1])
    run_dir = sys.argv[2]
    shots = os.path.join(run_dir, "screenshots")
    os.makedirs(shots, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    pid = parse_qs(urlparse(url).query).get("view_all_page_id", ["?"])[0]
    print(f"Deep-scraping (cap {MAX_ADS}): {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900}, locale="en-US",
            user_agent=scrape.USER_AGENT,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        page = ctx.new_page()
        Stealth().apply_stealth_sync(page)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        scrape.dismiss_cookies(page)
        try:
            page.wait_for_selector('text=/Library ID/i', timeout=30000)
        except PWTimeoutError:
            print("No ads found (or Meta blocked the page).", file=sys.stderr)
            browser.close(); sys.exit(1)

        manifest, seen, seen_hashes = [], set(), {}
        idx, stagnant, last = 0, 0, 0
        vh = (page.viewport_size or {}).get("height", 900)
        t0 = time.time()
        for step in range(5000):
            if time.time() - t0 > MAX_SECONDS:
                print(f"time cap ({MAX_SECONDS}s) reached at {len(seen)} creatives.")
                break
            cards = page.locator(CARD_XPATH)
            try:
                n = cards.count()
            except Exception:
                n = 0
            for j in range(n):
                if idx >= MAX_ADS:
                    break
                card = cards.nth(j)
                # Capture ONLY cards already in the viewport, so element.screenshot
                # does not auto-scroll the page back up. That back-yank fought the
                # forward scroll and was why the first run hung after one screen.
                try:
                    box = card.bounding_box()
                except Exception:
                    continue
                if not box or box["y"] < -60 or box["y"] > vh - 140:
                    continue
                best = largest_img(card)
                if best is None:
                    continue
                url_i = best_img_url(best)
                if not url_i:
                    continue
                key = creative_key(url_i)
                if key in seen:
                    continue
                cardpath = os.path.join(shots, f"ad-{stamp}-{idx:03d}.png")
                try:
                    card.screenshot(path=cardpath, timeout=5000)
                except Exception:
                    continue  # not stable right now; a later step may catch it
                seen.add(key)
                libid, vc = "", 1
                try:
                    t = card.inner_text(timeout=1000)
                    m = re.search(r"([0-9]+)\s+ads use this creative", t)
                    if m: vc = int(m.group(1))
                    lm = re.search(r"Library ID[:\s]*([0-9]{6,})", t)
                    if lm: libid = lm.group(1)
                except Exception:
                    pass
                is_video = False
                try:
                    is_video = card.locator("video").count() > 0
                except Exception:
                    pass
                dest = grab_dest(card)
                cpath, chash = download_creative(url_i, ctx, shots, stamp, idx, seen_hashes)
                manifest.append({
                    "index": idx, "library_id": libid,
                    "card_png": os.path.basename(cardpath),
                    "creative_png": os.path.basename(cpath) if cpath else "",
                    "creative_hash": chash, "is_video": is_video,
                    "dest_url": dest, "variants_reported": vc,
                })
                idx += 1
                if idx % 15 == 0:
                    print(f"  {idx} unique creatives captured... ({int(time.time()-t0)}s)")
            if idx >= MAX_ADS:
                print(f"reached cap ({MAX_ADS}); stopping.")
                break
            # Guaranteed forward progress; never scroll_into_view (that yanks back up).
            page.evaluate(f"window.scrollBy(0, Math.floor({vh} * {STEP_FRAC}))")
            page.wait_for_timeout(scrape.SCROLL_PAUSE_MS)
            scrape.try_click_see_more(page)
            try:
                at_bottom = page.evaluate(
                    "(window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 350)"
                )
            except Exception:
                at_bottom = False
            if len(seen) == last:
                stagnant += 1
                # Only a real plateau if we are also at the bottom (nothing left to lazy-load).
                if at_bottom and stagnant >= STAGNANT_STOP:
                    print(f"plateau at bottom: no new creative for {stagnant} steps (total {len(seen)}).")
                    break
            else:
                stagnant = 0
            last = len(seen)
        browser.close()

    json.dump(manifest, open(os.path.join(run_dir, "manifest.json"), "w"), indent=2)
    json.dump({"page_id": pid, "source_url": url,
               "scraped_at": stamp, "ad_count": len(manifest), "mode": "deep"},
              open(os.path.join(run_dir, "run.json"), "w"), indent=2)
    vids = sum(1 for e in manifest if e["is_video"])
    print(f"Done. {len(manifest)} unique creatives ({vids} video) -> {run_dir}")
    print(f"RUN_DIR={run_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Assemble the final Uplane-branded HTML report from a run directory.

Inputs (all live inside <RUN_DIR>):
  - run.json        : { page_id, source_url, scraped_at, ad_count }
  - manifest.json   : [ { index, png, dest_url } ... ]                (built by run_scrape.py)
  - analyses.json   : [ { index, library_id, brand_name, ... } ... ]  (written by Claude in the skill)
  - screenshots/*.png

Output:
  ~/meta-scraper/reports/<brand_slug>-<YYYYMMDD-HHMMSS>.html

The output is a single self-contained file:
  - Uplane logo inlined as SVG
  - Per-ad screenshots embedded as base64
  - All CSS + JS inlined
Drop it on Netlify, S3, GitHub Pages, or just open() it locally.

Usage:
  python build_report.py <RUN_DIR>
  python build_report.py <RUN_DIR> --brand "Patagonia"
  python build_report.py <RUN_DIR> --out /custom/path/report.html
"""
from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import os
import re
import sys
from collections import Counter
from typing import Any

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(SKILL_ROOT, "assets", "report_template.html")
LOGO_PATH = os.path.join(SKILL_ROOT, "assets", "uplane-logo.svg")
REPORTS_DIR = os.path.expanduser("~/meta-scraper/reports")


# ---------- helpers ----------------------------------------------------------

def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "brand"


def esc(s: Any) -> str:
    """HTML-escape a value, treating None/empty as ''."""
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def img_data_url(path: str) -> str:
    """Return a data: URL with the right mime type for any common image
    format. Sniffs magic bytes so the same code works for JPEG (Meta's CDN
    default), PNG (element screenshots), WebP, and GIF."""
    with open(path, "rb") as f:
        body = f.read()
    if body[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif body[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        mime = "image/webp"
    elif body[:6] in (b"GIF87a", b"GIF89a"):
        mime = "image/gif"
    else:
        # Fall back to PNG mime type — browsers are lenient about this for
        # known formats but we shouldn't reach this branch in practice.
        mime = "image/png"
    b64 = base64.b64encode(body).decode("ascii")
    return f"data:{mime};base64,{b64}"


def fmt_date_long(iso: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso)
    except Exception:
        dt = datetime.datetime.now()
    # e.g. "May 4, 2026 · 14:30"
    return dt.strftime("%B %-d, %Y · %H:%M")


def fmt_date_short(iso: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso)
    except Exception:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d")


# ---------- per-ad rendering -------------------------------------------------

def render_palette(palette: list[dict]) -> str:
    if not palette:
        return '<span class="ad-section-body dim">Not extracted.</span>'
    chunks = []
    for sw in palette:
        hex_v = (sw.get("hex") or "").strip()
        role = sw.get("role") or ""
        if not hex_v:
            continue
        # Normalize: ensure leading #
        if not hex_v.startswith("#"):
            hex_v = "#" + hex_v
        chunks.append(
            f'<button class="swatch" data-hex="{esc(hex_v)}" type="button" '
            f'title="Click to copy {esc(hex_v)}">'
            f'<span class="swatch-chip" style="background:{esc(hex_v)}"></span>'
            f'<span class="swatch-hex">{esc(hex_v.upper())}</span>'
            f'<span class="swatch-role">{esc(role)}</span>'
            f"</button>"
        )
    return "".join(chunks) or '<span class="ad-section-body dim">Not extracted.</span>'


def render_style_tags(tags: list[str]) -> str:
    out = []
    for t in tags or []:
        t = (t or "").strip()
        if t:
            out.append(f'<span class="tag tag-style">{esc(t)}</span>')
    return "".join(out)


def render_copy_block(headline: str, body: str, cta: str) -> str:
    rows = []
    if headline:
        rows.append(
            '<div class="copy-row">'
            '<span class="copy-label">Headline</span>'
            f'<span class="copy-text">{esc(headline)}</span>'
            "</div>"
        )
    if body:
        rows.append(
            '<div class="copy-row">'
            '<span class="copy-label">Primary text</span>'
            f'<span class="copy-text">{esc(body)}</span>'
            "</div>"
        )
    if cta:
        rows.append(
            '<div class="copy-row">'
            '<span class="copy-label">CTA</span>'
            f'<span class="copy-text cta">{esc(cta)}</span>'
            "</div>"
        )
    if not rows:
        return (
            '<div class="copy-row">'
            '<span class="copy-text muted">No on-image text detected.</span>'
            "</div>"
        )
    return "".join(rows)


def render_dest_link(dest: str) -> str:
    if not dest:
        return ""
    # Truncate display text if very long
    display = dest if len(dest) <= 70 else dest[:67] + "…"
    return (
        f'<a class="ad-dest" href="{esc(dest)}" target="_blank" rel="noopener" '
        f'title="{esc(dest)}">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>'
        '<polyline points="15 3 21 3 21 9"></polyline>'
        '<line x1="10" y1="14" x2="21" y2="3"></line>'
        "</svg>"
        f"<span>{esc(display)}</span>"
        "</a>"
    )


def _normalize_recreate_prompts(a: dict) -> list[dict]:
    """Collect recreate prompts into a normalized list of {angle, prompt} dicts.

    Supports three input shapes for backward compatibility:
      1. recreate_prompts: [ {angle, prompt}, ... ]   (current schema)
      2. recreate_prompts: [ "text", ... ]            (lightweight array)
      3. recreate_prompt: "text"                       (legacy single-string)

    Returns [] if no recreate prompt is set.
    """
    out: list[dict] = []
    arr = a.get("recreate_prompts")
    if isinstance(arr, list):
        for item in arr:
            if isinstance(item, dict):
                p = (item.get("prompt") or "").strip()
                ang = (item.get("angle") or "").strip()
                if p:
                    out.append({"angle": ang, "prompt": p})
            elif isinstance(item, str):
                if item.strip():
                    out.append({"angle": "", "prompt": item.strip()})
    elif isinstance(arr, str) and arr.strip():
        out.append({"angle": "", "prompt": arr.strip()})
    if not out:
        single = (a.get("recreate_prompt") or "").strip()
        if single:
            out.append({"angle": "", "prompt": single})
    return out


def render_ad_prompt(a: dict, customer: dict | None) -> str:
    """Render the per-ad brand-adapted generation prompt block(s).

    Each static ad can carry:
      - one or more ``recreate_prompts`` (each tagged with a brand "angle" the
        prompt leans on, e.g. "anti-sucralose", "real cocoa", "32g protein")
      - one ``reimagine_prompt`` that reworks the concept through the
        customer's foundational docs

    Backward compatibility: legacy ``recreate_prompt`` (single string) and
    ``brand_prompt`` (single string treated as reimagine) still render.
    Returns "" if no prompts are present, signaling the report should skip
    the prompt section entirely.
    """
    recreate_list = _normalize_recreate_prompts(a)
    reimagine = (
        (a.get("reimagine_prompt") or "").strip()
        or (a.get("brand_prompt") or "").strip()  # legacy fallback
    )
    if not recreate_list and not reimagine:
        return ""

    concept = (a.get("concept_breakdown") or "").strip()
    adapt = (a.get("adaptation_notes") or "").strip()
    customer_name = (customer.get("brand_name") if customer else "") or "your brand"

    head_sections = []
    if concept:
        head_sections.append(
            '<div class="ad-prompt-section">'
            '<span class="ad-prompt-section-label">Concept breakdown</span>'
            f'<p class="ad-prompt-section-body">{esc(concept)}</p>'
            "</div>"
        )
    if adapt:
        head_sections.append(
            '<div class="ad-prompt-section">'
            '<span class="ad-prompt-section-label">Adaptation notes</span>'
            f'<p class="ad-prompt-section-body">{esc(adapt)}</p>'
            "</div>"
        )

    def variant_block(key: str, label: str, tagline: str, body: str, angle: str = "") -> str:
        # Display label may include a per-variant angle suffix when set
        full_label = label if not angle else f"{label} · {angle}"
        copy_text = f"Copy {full_label.lower()}"
        angle_html = ""
        if angle:
            angle_html = f'<span class="ad-prompt-variant-angle">{esc(angle)}</span>'
        return (
            f'<div class="ad-prompt-variant ad-prompt-variant-{esc(key)}">'
            '<div class="ad-prompt-variant-head">'
            f'<span class="ad-prompt-variant-label">{esc(label)}</span>'
            f"{angle_html}"
            f'<span class="ad-prompt-variant-tag">{esc(tagline)}</span>'
            "</div>"
            '<div class="ad-prompt-block">'
            f'<button class="copy-prompt-btn" type="button" aria-label="{esc(copy_text)}">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>'
            '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>'
            f"</svg> Copy</button>"
            f'<pre class="ad-prompt-block-text">{esc(body)}</pre>'
            "</div>"
            "</div>"
        )

    variants_html = []
    if recreate_list:
        if len(recreate_list) == 1:
            variants_html.append(variant_block(
                "recreate", "Recreate",
                "minimum change, keep visual & copy where possible",
                recreate_list[0]["prompt"],
                recreate_list[0]["angle"],
            ))
        else:
            for i, r in enumerate(recreate_list, start=1):
                variants_html.append(variant_block(
                    "recreate", f"Recreate {i}",
                    "minimum change, keep visual & copy where possible",
                    r["prompt"],
                    r["angle"],
                ))
    if reimagine:
        variants_html.append(variant_block(
            "reimagine", "Reimagine",
            "concept reworked through customer's foundational docs",
            reimagine,
        ))

    return (
        '<div class="ad-prompt">'
        '<div class="ad-prompt-head">'
        '<span class="ad-prompt-label">Generation prompts</span>'
        f'<span class="ad-prompt-customer">for {esc(customer_name)}</span>'
        "</div>"
        + "".join(head_sections)
        + "".join(variants_html)
        + "</div>"
    )


def render_ad_card(idx: int, png_data_url: str, dest_url: str, a: dict, customer: dict | None = None,
                   variant_count: int = 1, variant_indexes: list[int] | None = None) -> str:
    headline = a.get("headline") or ""
    body = a.get("primary_text") or ""
    cta = a.get("cta_text") or ""
    library_id = a.get("library_id") or ""
    fmt = a.get("format") or "ad"
    visual = a.get("visual_summary") or ""
    typo = a.get("typography") or ""
    comp = a.get("composition") or ""
    focal = a.get("focal_point") or ""
    mood = a.get("mood") or ""
    notes = a.get("notes") or ""
    style_tags = a.get("style_tags") or []
    palette = a.get("color_palette") or []

    notes_html = ""
    if notes:
        notes_html = (
            '<div class="ad-notes">'
            '<span class="ad-notes-label">Notes</span>'
            f"{esc(notes)}"
            "</div>"
        )

    libid_html = (
        f'<span class="ad-libid">Library ID {esc(library_id)}</span>' if library_id else "<span></span>"
    )
    dest_html = render_dest_link(dest_url)
    prompt_html = render_ad_prompt(a, customer)

    variants_html = ""
    if variant_count > 1:
        # Tooltip lists the original ad-library indexes the user can cross-ref
        ix = ", ".join(f"#{n + 1:02d}" for n in (variant_indexes or []))
        variants_html = (
            f'<span class="ad-variants" title="This creative runs as {variant_count} ads in the library: {ix}">'
            f'× {variant_count} variants</span>'
        )

    return f"""
<article class="ad-card">
  <div class="ad-img-col">
    <a class="ad-img-wrap" href="#" onclick="return false;">
      <img src="{png_data_url}" alt="Ad {idx + 1}" loading="lazy" />
    </a>
    <button class="copy-image-btn" type="button" aria-label="Copy ad image">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <polyline points="21 15 16 10 5 21"></polyline>
      </svg>
      Copy image
    </button>
  </div>
  <div class="ad-body">
    <div class="ad-head">
      <span class="ad-num">#{idx + 1:02d}</span>
      {variants_html}
      <div class="ad-tags">
        <span class="tag tag-format">{esc(fmt)}</span>
        {render_style_tags(style_tags)}
      </div>
    </div>

    <div class="ad-section">
      <h3 class="ad-section-title">Visual summary</h3>
      <p class="ad-section-body">{esc(visual) or '<span class="ad-section-body dim">—</span>'}</p>
    </div>

    <div class="ad-section">
      <h3 class="ad-section-title">Copy <span class="ad-section-meta">verbatim</span></h3>
      <div class="copy-block">{render_copy_block(headline, body, cta)}</div>
    </div>

    <div class="ad-section">
      <h3 class="ad-section-title">Color palette</h3>
      <div class="palette">{render_palette(palette)}</div>
    </div>

    <div class="ad-section ad-section-grid">
      <div>
        <h4 class="ad-section-title">Typography</h4>
        <p class="ad-section-body">{esc(typo) or '—'}</p>
      </div>
      <div>
        <h4 class="ad-section-title">Composition</h4>
        <p class="ad-section-body">{esc(comp) or '—'}</p>
      </div>
      <div>
        <h4 class="ad-section-title">Focal point</h4>
        <p class="ad-section-body">{esc(focal) or '—'}</p>
      </div>
      <div>
        <h4 class="ad-section-title">Mood</h4>
        <p class="ad-section-body">{esc(mood) or '—'}</p>
      </div>
    </div>

    {notes_html}

    {prompt_html}

    <div class="ad-foot">
      {libid_html}
      {dest_html}
    </div>
  </div>
</article>
"""


# ---------- summary band -----------------------------------------------------

def render_summary_band(analyses: list[dict]) -> str:
    if not analyses:
        return ""
    n = len(analyses)
    fmts = Counter((a.get("format") or "").strip().lower() for a in analyses if a.get("format"))
    style_counter = Counter()
    for a in analyses:
        for t in a.get("style_tags") or []:
            t = (t or "").strip().lower()
            if t:
                style_counter[t] += 1
    top_styles = [t for t, _ in style_counter.most_common(8)]

    fmts_html = "".join(
        f'<span class="summary-tag">{esc(k)} <strong>· {v}</strong></span>'
        for k, v in fmts.most_common()
    ) or '<span class="summary-tag">—</span>'

    styles_html = "".join(
        f'<span class="summary-tag">{esc(t)}</span>' for t in top_styles
    ) or '<span class="summary-tag">—</span>'

    # Palette: gather most-used hex codes across ads
    hex_counter = Counter()
    for a in analyses:
        for sw in a.get("color_palette") or []:
            h = (sw.get("hex") or "").strip().lower()
            if h:
                if not h.startswith("#"):
                    h = "#" + h
                hex_counter[h] += 1
    top_hex = [h for h, _ in hex_counter.most_common(8)]
    palette_html = "".join(
        f'<button class="swatch" data-hex="{esc(h)}" type="button" title="Copy {esc(h)}">'
        f'<span class="swatch-chip" style="background:{esc(h)}"></span>'
        f'<span class="swatch-hex">{esc(h.upper())}</span>'
        "</button>"
        for h in top_hex
    ) or '<span class="summary-tag">—</span>'

    return f"""
<section class="summary-band">
  <div class="summary-stat">
    <div class="summary-stat-label">Active creatives</div>
    <div class="summary-stat-value numeric">{n}</div>
  </div>
  <div class="summary-stat">
    <div class="summary-stat-label">Formats in rotation</div>
    <div class="summary-stat-value">
      <div class="summary-tags">{fmts_html}</div>
    </div>
  </div>
  <div class="summary-stat">
    <div class="summary-stat-label">Recurring styles</div>
    <div class="summary-stat-value">
      <div class="summary-tags">{styles_html}</div>
    </div>
  </div>
  <div class="summary-stat">
    <div class="summary-stat-label">Most-used colors</div>
    <div class="summary-stat-value">
      <div class="palette" style="margin-top:2px">{palette_html}</div>
    </div>
  </div>
</section>
"""


# ---------- main -------------------------------------------------------------

def load_customer_profile(run_dir: str, customer_arg: str | None) -> dict | None:
    """Resolve the customer profile in this priority order:
       1. --customer <slug-or-path>  → load from ~/meta-scraper/brands/<slug>/brand.json
                                       or directly from a brand.json path
       2. <run_dir>/customer.json    → embedded copy made at scrape time
       3. None                        → no customer; report renders without prompt sections
    """
    brands_root = os.path.expanduser("~/meta-scraper/brands")
    if customer_arg:
        # Treat as direct path if it looks like one
        if os.path.isfile(customer_arg):
            with open(customer_arg) as f:
                return json.load(f)
        # Otherwise treat as a slug under ~/meta-scraper/brands/
        candidate = os.path.join(brands_root, customer_arg, "brand.json")
        if os.path.isfile(candidate):
            with open(candidate) as f:
                return json.load(f)
        print(f"WARNING: --customer '{customer_arg}' did not resolve to a brand profile; ignoring.", file=sys.stderr)
    embedded = os.path.join(run_dir, "customer.json")
    if os.path.isfile(embedded):
        with open(embedded) as f:
            return json.load(f)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", help="Path to the run directory created by run_scrape.py")
    ap.add_argument("--brand", help="Override competitor brand name (otherwise inferred from analyses[0].brand_name)")
    ap.add_argument("--customer", help="Customer brand slug (under ~/meta-scraper/brands/) or path to a brand.json. Used to render the per-ad generation prompt section.")
    ap.add_argument("--out", help="Override output path (otherwise ~/meta-scraper/reports/<slug>-<stamp>.html)")
    args = ap.parse_args()

    run_dir = os.path.abspath(os.path.expanduser(args.run_dir))
    if not os.path.isdir(run_dir):
        print(f"ERROR: not a directory: {run_dir}", file=sys.stderr)
        return 2

    # Load inputs
    try:
        with open(os.path.join(run_dir, "run.json")) as f:
            run = json.load(f)
        with open(os.path.join(run_dir, "manifest.json")) as f:
            manifest = json.load(f)
        with open(os.path.join(run_dir, "analyses.json")) as f:
            analyses = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: missing input file in {run_dir}: {e.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"ERROR: malformed JSON in {run_dir}: {e}", file=sys.stderr)
        return 2

    if len(analyses) != len(manifest):
        print(
            f"WARNING: analyses ({len(analyses)}) and manifest ({len(manifest)}) length mismatch. "
            "Pairing by index where possible.",
            file=sys.stderr,
        )

    # Index analyses by 'index' field for safe pairing
    analyses_by_idx = {a.get("index", i): a for i, a in enumerate(analyses)}

    # Brand name resolution: --brand wins, else first analysis with non-empty brand_name, else page_id
    brand_name = (args.brand or "").strip()
    if not brand_name:
        for a in analyses:
            bn = (a.get("brand_name") or "").strip()
            if bn:
                brand_name = bn
                break
    if not brand_name:
        brand_name = f"Page {run.get('page_id', '?')}"

    # Customer profile (the brand the prompts will be generated FOR).
    # Optional — if absent, prompt sections are skipped and the report is
    # purely a competitor analysis with no per-ad generation prompts.
    customer = load_customer_profile(run_dir, args.customer)

    # Resolve the customer's reference images (product photo + optional
    # logo variants), if any. We search in priority order:
    # (1) the brand-folder copy next to brand.json (the canonical location),
    # (2) the file as named directly inside the run dir (legacy).
    # When found, each image is embedded as a data URL so the report
    # stays fully self-contained.
    def _resolve_customer_image(filename_field: str) -> str:
        if not customer:
            return ""
        name = (customer.get(filename_field) or "").strip()
        if not name:
            return ""
        brand_slug = (customer.get("brand_slug") or "").strip()
        candidates: list[str] = []
        if brand_slug:
            candidates.append(
                os.path.expanduser(f"~/meta-scraper/brands/{brand_slug}/{name}")
            )
        candidates.append(os.path.join(run_dir, name))  # legacy fallback
        for path in candidates:
            if os.path.isfile(path):
                try:
                    return img_data_url(path)
                except Exception as e:
                    print(f"WARNING: could not embed {filename_field}={path}: {e}", file=sys.stderr)
                    return ""
        return ""

    customer_image_data_url = _resolve_customer_image("product_image_filename")
    customer_logo_light_url = _resolve_customer_image("logo_light_bg_filename")
    customer_logo_dark_url = _resolve_customer_image("logo_dark_bg_filename")

    # Load template + logo
    with open(TEMPLATE_PATH, "r") as f:
        tpl = f.read()
    with open(LOGO_PATH, "r") as f:
        logo_svg = f.read().strip()

    # Dedup by creative_hash. Meta serves identical bytes for the same creative
    # across multiple ad IDs (audience-split testing). We collapse those into a
    # single card per unique hash, with a "× N variants" badge listing the
    # other indexes the user can cross-reference. Entries without a hash
    # (legacy runs) fall back to per-index rendering — old reports still build.
    by_hash: dict[str, list[dict]] = {}
    no_hash: list[dict] = []
    for entry in manifest:
        h = (entry.get("creative_hash") or "").strip()
        if h:
            by_hash.setdefault(h, []).append(entry)
        else:
            no_hash.append(entry)

    # Render order: keep the first index of each group (lowest index = most
    # impressions / earliest-loaded), then any unhashed entries. Cards in the
    # original manifest order so the report matches what Meta showed first.
    canonical_entries: list[tuple[dict, int, list[int]]] = []
    seen_hashes: set[str] = set()
    for entry in manifest:
        h = (entry.get("creative_hash") or "").strip()
        if h:
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            group = by_hash[h]
            indexes = [g["index"] for g in group]
            canonical_entries.append((entry, len(group), indexes))
        else:
            canonical_entries.append((entry, 1, [entry["index"]]))

    # Render per-ad cards in manifest order. Prefer the clean creative image
    # (just the ad visual, no Meta UI chrome) when the scraper extracted one.
    # Fall back to the full card screenshot only if the creative is missing —
    # that way old run dirs (manifests without creative_png) still render.
    cards_html_parts = []
    shots_dir = os.path.join(run_dir, "screenshots")
    n_total_ads = len(manifest)
    for entry, variant_count, variant_indexes in canonical_entries:
        idx = entry["index"]
        # Choose image: creative > card. `png` is the legacy field name.
        chosen = ""
        for key in ("creative_png", "card_png", "png"):
            name = entry.get(key) or ""
            if name and os.path.isfile(os.path.join(shots_dir, name)):
                chosen = name
                break
        if not chosen:
            print(f"WARNING: no usable image for ad {idx}", file=sys.stderr)
            continue
        png = os.path.join(shots_dir, chosen)
        a = analyses_by_idx.get(idx, {})
        try:
            data_url = img_data_url(png)
        except Exception as e:
            print(f"WARNING: could not embed {png}: {e}", file=sys.stderr)
            continue
        cards_html_parts.append(
            render_ad_card(idx, data_url, entry.get("dest_url", ""), a, customer,
                           variant_count=variant_count, variant_indexes=variant_indexes)
        )

    cards_html = "\n".join(cards_html_parts)

    # Substitute placeholders
    scraped_at = run.get("scraped_at", datetime.datetime.now().isoformat(timespec="seconds"))

    # Customer-aware subtitle suffix. If a customer profile is loaded, the
    # subtitle gains "...adapted as a generation prompt for <Customer>"
    # framing. Otherwise it stays neutral.
    customer_name = (customer.get("brand_name") if customer else "") or ""
    if customer_name:
        subtitle_suffix = f", and adapted as a ready-to-paste image-generation prompt for <strong>{esc(customer_name)}</strong>"
    else:
        subtitle_suffix = " — built to surface the creative patterns this brand is leaning on right now"

    # Customer-context card. Only renders when both a customer profile and
    # at least one usable reference image (product or logo) are present.
    # Otherwise the placeholder collapses to empty and the layout flows
    # past it.
    customer_card_html = ""
    has_any_ref_image = bool(
        customer_image_data_url or customer_logo_light_url or customer_logo_dark_url
    )
    if customer and has_any_ref_image:
        c_product = (customer.get("product_name") or "").strip()
        c_type = (customer.get("product_type") or "").strip()
        c_niche = (customer.get("niche") or "").strip()
        # Build a short meta line under the brand name. We don't render the
        # raw what_you_sell_and_to_whom string because it tends to be long.
        meta_bits = [b for b in (c_product, c_type or c_niche) if b]
        meta_line = " · ".join(meta_bits)

        def _img_tile(data_url: str, label: str, alt: str, tile_class: str = "") -> str:
            """Render one image tile + its copy button. Empty when no image."""
            if not data_url:
                return ""
            return f"""
    <div class="customer-card-img-tile {tile_class}">
      <span class="customer-card-img-tile-label">{esc(label)}</span>
      <div class="customer-card-img-wrap">
        <img src="{data_url}" alt="{esc(alt)}" loading="lazy" />
      </div>
      <button class="copy-image-btn" type="button" aria-label="Copy {esc(label).lower()}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        Copy
      </button>
    </div>"""

        # Available references list, for the help line.
        ref_bits = []
        if customer_image_data_url:
            ref_bits.append("the product photo")
        if customer_logo_light_url or customer_logo_dark_url:
            ref_bits.append("the brand logo")
        ref_phrase = " and ".join(ref_bits) if ref_bits else "the reference image"

        tiles_html = "".join([
            _img_tile(customer_image_data_url, "Product photo", f"{customer_name} product photo"),
            _img_tile(customer_logo_light_url, "Logo for light backgrounds", f"{customer_name} logo (light bg)"),
            _img_tile(customer_logo_dark_url, "Logo for dark backgrounds", f"{customer_name} logo (dark bg)", "customer-card-img-tile-dark"),
        ])

        # Uplane pre-flight settings. These are tool-specific defaults the
        # user wants to confirm before pasting any prompt. Rendered inside
        # the customer-context card so it lives in the report's
        # "beginning instructions" area.
        uplane_setup_html = """
    <div class="uplane-setup">
      <span class="uplane-setup-label">Uplane setup, before pasting any prompt</span>
      <div class="uplane-setup-toggles">
        <span class="uplane-toggle uplane-toggle-off" title="Set this toggle to OFF in Uplane">
          <span class="uplane-toggle-track"><span class="uplane-toggle-dot"></span></span>
          <span class="uplane-toggle-name">Layer Based</span>
          <span class="uplane-toggle-state">OFF</span>
        </span>
        <span class="uplane-toggle uplane-toggle-on" title="Set this toggle to ON in Uplane">
          <span class="uplane-toggle-track"><span class="uplane-toggle-dot"></span></span>
          <span class="uplane-toggle-name">Skip Thinking</span>
          <span class="uplane-toggle-state">ON</span>
        </span>
      </div>
    </div>"""

        customer_card_html = f"""
<section class="customer-card">
  <div class="customer-card-imgrow">
    {tiles_html}
  </div>
  <div class="customer-card-body">
    <span class="customer-card-eyebrow">Prompts are written for</span>
    <h2 class="customer-card-title">{esc(customer_name)}</h2>
    <p class="customer-card-meta">{esc(meta_line)}</p>
    <p class="customer-card-help">Attach {ref_phrase} alongside the competitor ad when you paste any of the prompts below into your image-generation model. Click <em>Copy</em> on any tile to grab a PNG straight to your clipboard.</p>
    {uplane_setup_html}
  </div>
</section>
"""

    replacements = {
        "{{UPLANE_LOGO_SVG}}": logo_svg,
        "{{BRAND_NAME}}": esc(brand_name),
        "{{BRAND_SLUG}}": esc(slugify(brand_name)),
        "{{GENERATED_DATE}}": esc(fmt_date_short(scraped_at)),
        "{{GENERATED_DATE_LONG}}": esc(fmt_date_long(scraped_at)),
        "{{PAGE_ID}}": esc(run.get("page_id", "")),
        "{{AD_COUNT}}": esc(str(len(cards_html_parts))),
        "{{SOURCE_URL}}": esc(run.get("source_url", "")),
        "{{SUMMARY_BAND_HTML}}": render_summary_band(analyses),
        "{{AD_CARDS_HTML}}": cards_html,
        "{{CUSTOMER_BRAND}}": esc(customer_name),
        "{{SUBTITLE_CUSTOMER_SUFFIX}}": subtitle_suffix,
        "{{CUSTOMER_CARD_HTML}}": customer_card_html,
    }
    out_html = tpl
    for k, v in replacements.items():
        out_html = out_html.replace(k, v)

    # Decide output path
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(brand_name)
    if args.out:
        out_path = os.path.abspath(os.path.expanduser(args.out))
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    else:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        out_path = os.path.join(REPORTS_DIR, f"{slug}-{stamp}.html")

    with open(out_path, "w") as f:
        f.write(out_html)

    print(f"REPORT={out_path}")
    customer_line = f" · Customer: {customer_name}" if customer_name else ""
    n_unique = len(cards_html_parts)
    n_total = len(manifest)
    if n_unique < n_total:
        dedup_note = f" · {n_total} ad IDs collapsed to {n_unique} unique creatives"
    else:
        dedup_note = ""
    print(f"Competitor: {brand_name} · Cards: {n_unique}{dedup_note}{customer_line} · Size: {os.path.getsize(out_path) / 1024:.1f} KB")
    if customer:
        n_recreate_ads = 0
        n_recreate_total = 0
        for a in analyses:
            lst = _normalize_recreate_prompts(a)
            if lst:
                n_recreate_ads += 1
                n_recreate_total += len(lst)
        n_reimagine = sum(
            1 for a in analyses
            if (a.get("reimagine_prompt") or "").strip()
            or (a.get("brand_prompt") or "").strip()  # legacy fallback
        )
        total = len(analyses)
        print(f"Generation prompts: {n_recreate_total} recreate ({n_recreate_ads}/{total} ads) · {n_reimagine}/{total} reimagine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

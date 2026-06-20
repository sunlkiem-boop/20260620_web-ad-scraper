#!/usr/bin/env python3
"""
Scaffold a customer brand folder under ~/meta-scraper/brands/<slug>/.

Each customer needs ONE brand profile. The skill loads it whenever you
analyze a competitor's Meta ads "for" that customer, so it can:
  - substitute the customer's brand/product/language into generated prompts
  - read the 4 foundational documents to inform tone, claims, audience, etc.
  - reference the customer's product image when generating image-gen prompts

Usage:
  python init_brand.py acme-skincare
  python init_brand.py acme-skincare --name "Acme Skincare"

After running, edit ~/meta-scraper/brands/acme-skincare/brand.json with
the customer's details and drop the foundational docs into documents/.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_ROOT, "assets", "brand_template.json")
BRANDS_ROOT = os.path.expanduser("~/meta-scraper/brands")


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "brand"


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a customer brand folder.")
    ap.add_argument("slug", help="Brand slug, e.g. 'acme-skincare'.")
    ap.add_argument("--name", help="Brand display name (defaults to titleized slug).")
    args = ap.parse_args()

    slug = slugify(args.slug)
    folder = os.path.join(BRANDS_ROOT, slug)

    if os.path.exists(folder):
        print(f"Brand folder already exists: {folder}", file=sys.stderr)
        print("Edit it directly or pick a new slug.", file=sys.stderr)
        return 1

    os.makedirs(os.path.join(folder, "documents"), exist_ok=True)

    if not os.path.isfile(TEMPLATE):
        print(f"ERROR: missing template at {TEMPLATE}", file=sys.stderr)
        return 2
    with open(TEMPLATE) as f:
        tpl = json.load(f)

    tpl["brand_slug"] = slug
    tpl["brand_name"] = args.name or slug.replace("-", " ").title()

    with open(os.path.join(folder, "brand.json"), "w") as f:
        json.dump(tpl, f, indent=2)

    print(
        f"""
Brand scaffolded: {folder}

Next steps:

1. Edit {folder}/brand.json — fill in:
     - niche                       e.g. "natural skincare"
     - what_you_sell_and_to_whom   e.g. "anti-aging serums to women aged 35-55"
     - product_name                e.g. "Acme Renewal Serum"
     - product_type                e.g. "30ml glass dropper bottle"
     - language                    default: "English"
     - product_image_filename      e.g. "product.jpg" (drop the file in this folder)

2. Drop your 4 foundational documents into:
     {folder}/documents/

   Supported formats:
     - .pdf (preferred for long docs)
     - .md / .txt (for shorter notes)
     - .docx (basic support)

3. Drop a high-quality product image into the brand folder:
     {folder}/<product_image_filename>

4. Now run the skill — when you paste a Meta Ad Library URL, mention this
   customer (or they'll be auto-detected if it's the only profile).
   The skill will use this brand profile to generate per-ad prompts.
"""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Bundle the scrape-meta-ads skill + the underlying scraper + selected
customer brand folders into a single .zip that another Mac can install
with `bash install.sh`.

Usage:
  # Bundle everything (all brand folders, with their documents)
  python package_handoff.py

  # Bundle only specific brands
  python package_handoff.py --brands brand-slug-1 brand-slug-2

  # Bundle the skill+scraper only, no brands at all (e.g. you want the
  # recipient to set up their own customers from scratch)
  python package_handoff.py --no-brands

  # Bundle brands but exclude the foundational documents (keeps brand.json
  # and product images, drops anything in documents/). Useful if the docs
  # are confidential.
  python package_handoff.py --no-docs

Output: ~/meta-scraper/handoffs/scrape-meta-ads-<timestamp>.zip
"""
from __future__ import annotations

import argparse
import datetime
import os
import stat
import sys
import zipfile

HOME = os.path.expanduser("~")
SKILL_DIR = os.path.join(HOME, ".claude", "skills", "scrape-meta-ads")
SCRAPER = os.path.join(HOME, "meta-scraper", "scrape.py")
BRANDS_ROOT = os.path.join(HOME, "meta-scraper", "brands")
HANDOFFS_ROOT = os.path.join(HOME, "meta-scraper", "handoffs")
INSTALL_SH_SRC = os.path.join(SKILL_DIR, "assets", "install.sh.template")
README_SRC = os.path.join(SKILL_DIR, "assets", "handoff_README.md")
BUNDLE_ROOT = "scrape-meta-ads-handoff"

# Filenames / dirs we never want in a handoff
EXCLUDE_NAMES = {"__pycache__", ".DS_Store", ".pytest_cache"}
EXCLUDE_SUFFIXES = (".pyc",)


def keep(name: str) -> bool:
    if name in EXCLUDE_NAMES:
        return False
    if name.endswith(EXCLUDE_SUFFIXES):
        return False
    return True


def add_path(zf: zipfile.ZipFile, src_path: str, arc_name: str, executable: bool = False) -> None:
    """Write a single file with optional +x permission preserved in the zip."""
    zi = zipfile.ZipInfo.from_file(src_path, arcname=arc_name)
    if executable:
        # Preserve Unix mode 0755 in the zip (macOS unzip respects this)
        zi.external_attr = (stat.S_IFREG | 0o755) << 16
    zi.compress_type = zipfile.ZIP_DEFLATED
    with open(src_path, "rb") as f:
        zf.writestr(zi, f.read())


def add_tree(zf: zipfile.ZipFile, src_dir: str, arc_prefix: str, skip_dirs: set[str] | None = None) -> int:
    """Recursively add a directory tree, returning file count."""
    skip_dirs = skip_dirs or set()
    count = 0
    for root, dirs, files in os.walk(src_dir):
        # Filter dirs in-place so os.walk doesn't descend into excluded ones
        dirs[:] = [d for d in dirs if keep(d) and d not in skip_dirs]
        for f in files:
            if not keep(f):
                continue
            src = os.path.join(root, f)
            rel = os.path.relpath(src, src_dir)
            arc = f"{arc_prefix}/{rel}" if arc_prefix else rel
            add_path(zf, src, arc)
            count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="Package the skill for handoff to another Mac.")
    ap.add_argument("--brands", nargs="*", help="Brand slugs to include. Default: all under ~/meta-scraper/brands/")
    ap.add_argument("--no-brands", action="store_true", help="Don't include any brand folders.")
    ap.add_argument("--no-docs", action="store_true", help="Include brand folders but drop documents/ subfolders (keeps brand.json + product images).")
    ap.add_argument("--name", default="scrape-meta-ads", help="Output filename prefix.")
    ap.add_argument("--out", help="Override output path.")
    args = ap.parse_args()

    if args.brands and args.no_brands:
        print("ERROR: --brands and --no-brands are mutually exclusive.", file=sys.stderr)
        return 2

    # Sanity: required source files
    if not os.path.isdir(SKILL_DIR):
        print(f"ERROR: skill dir not found at {SKILL_DIR}", file=sys.stderr)
        return 2
    if not os.path.isfile(SCRAPER):
        print(f"ERROR: scraper not found at {SCRAPER}", file=sys.stderr)
        return 2
    if not os.path.isfile(INSTALL_SH_SRC):
        print(f"ERROR: install.sh template missing at {INSTALL_SH_SRC}", file=sys.stderr)
        return 2
    if not os.path.isfile(README_SRC):
        print(f"ERROR: handoff README missing at {README_SRC}", file=sys.stderr)
        return 2

    # Resolve brand selection
    available = (
        sorted(d for d in os.listdir(BRANDS_ROOT) if os.path.isdir(os.path.join(BRANDS_ROOT, d)))
        if os.path.isdir(BRANDS_ROOT)
        else []
    )
    if args.no_brands:
        chosen: list[str] = []
    elif args.brands:
        bad = [b for b in args.brands if b not in available]
        if bad:
            print(f"ERROR: unknown brand slug(s): {', '.join(bad)}", file=sys.stderr)
            print(f"Available: {', '.join(available) or '(none)'}", file=sys.stderr)
            return 2
        chosen = list(args.brands)
    else:
        chosen = available

    # Output path
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = args.out or os.path.join(HANDOFFS_ROOT, f"{args.name}-{stamp}.zip")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print(f"Packaging handoff bundle:")
    print(f"  Output:   {out_path}")
    print(f"  Skill:    {SKILL_DIR}")
    print(f"  Scraper:  {SCRAPER}")
    print(f"  Brands:   {', '.join(chosen) if chosen else '(none)'}")
    print(f"  Docs:     {'excluded' if args.no_docs else 'included'}")
    print()

    skill_files = scraper_files = brand_files = 0

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Skill (under skill/ inside the bundle)
        skill_files = add_tree(zf, SKILL_DIR, f"{BUNDLE_ROOT}/skill")

        # Scraper
        add_path(zf, SCRAPER, f"{BUNDLE_ROOT}/scraper/scrape.py", executable=True)
        scraper_files = 1

        # Brands
        for slug in chosen:
            src = os.path.join(BRANDS_ROOT, slug)
            skip = {"documents"} if args.no_docs else set()
            n = add_tree(zf, src, f"{BUNDLE_ROOT}/brands/{slug}", skip_dirs=skip)
            print(f"  + brand: {slug} ({n} file{'s' if n != 1 else ''})")
            brand_files += n

        # Installer + README at bundle root
        add_path(zf, INSTALL_SH_SRC, f"{BUNDLE_ROOT}/install.sh", executable=True)
        add_path(zf, README_SRC, f"{BUNDLE_ROOT}/README.md")

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nDone.")
    print(f"  Skill files:    {skill_files}")
    print(f"  Scraper files:  {scraper_files}")
    print(f"  Brand files:    {brand_files}")
    print(f"  Bundle size:    {size_mb:.2f} MB")
    print(f"\nSend the zip to whoever needs it. They run:")
    print(f"  unzip {os.path.basename(out_path)}")
    print(f"  cd {BUNDLE_ROOT}")
    print(f"  bash install.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

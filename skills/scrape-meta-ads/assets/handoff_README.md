# scrape-meta-ads · handoff package

You've been given a setup bundle for a tool that scrapes Meta Ad Library pages, analyzes each ad visually, and (when a customer brand profile is set up) produces a ready-to-paste image-generation prompt for each one.

## Requirements

- macOS (the scraper is tested on Mac)
- Python 3.11 or newer (`python3 --version` to check; `brew install python@3.12` if missing)
- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and signed in

## Install (one-time, ~3 minutes)

1. Unzip this bundle wherever you like.
2. Open Terminal in the unzipped folder (right-click → Services → New Terminal at Folder, or `cd path/to/scrape-meta-ads-handoff`).
3. Run:

   ```bash
   bash install.sh
   ```

That's it. The installer:

- Verifies your Python version
- Creates a Python virtual environment at `~/.meta-scraper-venv`
- Installs Playwright + `playwright-stealth==2.0.3` (pinned)
- Downloads Chromium for Playwright (~150 MB)
- Copies the skill to `~/.claude/skills/scrape-meta-ads/`
- Copies the underlying scraper to `~/meta-scraper/scrape.py`
- Copies any included customer brand folders to `~/meta-scraper/brands/`
- Sanity-checks that imports work

If you already have a `~/.claude/skills/scrape-meta-ads/` folder, the installer backs it up to `…bak` first — your existing setup isn't lost.

## Use it

Open Claude Code in any directory. Paste a Meta Ad Library URL, mention the customer:

> Scrape these ads for aonic: `https://www.facebook.com/ads/library/?...&view_all_page_id=...`

Claude auto-loads the `scrape-meta-ads` skill, scrapes the competitor's active ads, analyzes each statically (skipping videos by default unless you ask otherwise), and — because the customer brand profile is already set up — generates a per-ad image-generation prompt tailored to that customer.

You get a self-contained HTML report at `~/meta-scraper/reports/<competitor>-<timestamp>.html`. Open it locally or upload it anywhere static (Netlify, S3, GitHub Pages).

## Adding more customers later

Two ways:

**A. Let Claude do it.** Paste:

> Set up a new customer: `<brand name>` — their site is `<url>`

The skill will fetch the site, populate the brand profile, and tell you where to drop their foundational documents and product image.

**B. Run the scaffolder yourself:**

```bash
~/.meta-scraper-venv/bin/python ~/.claude/skills/scrape-meta-ads/scripts/init_brand.py <slug> --name "<Brand Name>"
```

Then edit `~/meta-scraper/brands/<slug>/brand.json`, drop the 4 foundational docs into `documents/`, and put a product image in the brand folder root.

## What's bundled

```
scrape-meta-ads-handoff/
├── README.md              this file
├── install.sh             the installer (run once)
├── skill/                 → installs to ~/.claude/skills/scrape-meta-ads/
├── scraper/
│   └── scrape.py          → installs to ~/meta-scraper/scrape.py
└── brands/                → installs to ~/meta-scraper/brands/
    └── <slug>/            customer brand profile(s) included by the sender
        ├── brand.json
        ├── documents/     foundational docs (PDF / md / txt)
        └── <product>.png  product image (if shared)
```

## Troubleshooting

- **"python3 not found"** → install Python 3.11+: `brew install python@3.12`
- **"Chromium install hung"** → re-run `~/.meta-scraper-venv/bin/playwright install chromium`
- **Skill doesn't trigger in Claude Code** → restart the Claude Code session; type `what skills do you have?` to confirm `scrape-meta-ads` is listed
- **Reports show no generation prompt section** → either no customer brand was named, or the customer's `brand.json` is missing — check `~/meta-scraper/brands/<slug>/brand.json` exists

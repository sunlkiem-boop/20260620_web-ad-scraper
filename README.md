# Marketing skills — setup bundle

Everything needed to run three Claude Code marketing skills on a Mac:

- **scrape-meta-ads** — scrape a brand's currently-active Meta/Facebook/Instagram ads, analyze each one (palette + hex, typography, layout, copy verbatim, CTA, mood), and produce a self-contained, branded HTML report. When a customer brand profile is loaded, it also writes a ready-to-paste image-generation prompt for every static ad.
- **brand-research-sprint** — produce a full foundational research package for a product: VOC Dossier + Avatar Sheets + Offer Brief + Beliefs doc (4 markdown files + 4 matching PDFs), with 200+ attributed customer quotes.
- **marketing-brain** — a personal, file-based knowledge base built from marketing creators' YouTube transcripts. Ask it questions and it answers in the creator's framing with citations.

## Easiest setup: let Claude do it

1. Make sure [Claude Code](https://docs.claude.com/en/docs/claude-code) is installed and you're signed in.
2. Open Claude Code **in this folder**.
3. Say:

   > Read SETUP_FOR_CLAUDE.md and set everything up.

Claude reads [SETUP_FOR_CLAUDE.md](SETUP_FOR_CLAUDE.md), runs the installer, handles any hiccups, and verifies the result. Then **restart Claude Code** so the skills load.

## Manual setup (if you'd rather)

Open Terminal in this folder and run:

```bash
bash install.sh
```

Takes ~2–4 minutes (mostly the Chromium download). It's idempotent and non-destructive — existing skills are backed up to `*.bak`, and existing brand/brain data is left untouched.

## Requirements

- macOS
- Python 3.11+ (`python3 --version`; if missing, `brew install python@3.12`)
- Claude Code, installed and signed in

## What the installer puts where

| From this bundle | Installs to |
|---|---|
| `skills/scrape-meta-ads/` | `~/.claude/skills/scrape-meta-ads/` |
| `skills/brand-research-sprint/` | `~/.claude/skills/brand-research-sprint/` |
| `skills/marketing-brain/` | `~/.claude/skills/marketing-brain/` |
| `scraper/scrape.py` | `~/meta-scraper/scrape.py` (the scraper engine) |
| `scraper/scrape_deep.py` | `~/meta-scraper/scrape_deep.py` (deep-scroll variant for large advertisers) |
| `brands/aonic-fuel/` | `~/meta-scraper/brands/aonic-fuel/` (example customer) |
| `brands/aonic-complete/` | `~/meta-scraper/brands/aonic-complete/` (example customer) |
| `marketing-brain-data/knowledge/` | `~/Second Marketing Brain/knowledge/` (seed brain) |
| (created) | `~/.meta-scraper-venv/` — Python env + Chromium, shared by all three skills |

## Using the skills (after restarting Claude Code)

| Skill | Say something like |
|---|---|
| scrape-meta-ads | "Scrape these ads for [BRAND]: `<Meta Ad Library URL with view_all_page_id>`" |
| brand-research-sprint | "Create the foundational docs for `<product URL>`" |
| marketing-brain | "Ask the marketing brain: how does Mark structure a VSL?" |

For the ad scraper, grab the URL from the brand's **Pages** result in the [Meta Ad Library](https://www.facebook.com/ads/library/) — the one containing `view_all_page_id=...`.

## What's bundled

```
marketing-skills-handoff/
├── README.md                  this file
├── SETUP_FOR_CLAUDE.md        instructions Claude follows to install
├── install.sh                 the installer
├── skills/                    the three skills
│   ├── scrape-meta-ads/
│   ├── brand-research-sprint/
│   └── marketing-brain/
├── scraper/
│   ├── scrape.py              the Meta Ad Library scraper engine
│   └── scrape_deep.py         deep-scroll variant for large advertisers
├── brands/
│   ├── aonic-fuel/            example customer brand profile
│   └── aonic-complete/        example customer brand profile
├── marketing-brain-data/      seed knowledge base
└── examples/                  finished Aonic Fuel deliverables + walkthrough
```

## Troubleshooting

- **Skill doesn't show in `/skills`** — restart Claude Code; confirm `~/.claude/skills/<skill>/SKILL.md` exists.
- **Ad scrape times out** — re-run `~/.meta-scraper-venv/bin/playwright install chromium`.
- **PDF rendering fails in brand-research-sprint** — `~/.meta-scraper-venv/bin/python -m pip install markdown_pdf`.
- **Report shows no generation-prompt section** — name a customer brand when you ask (e.g. "for aonic"), or check `~/meta-scraper/brands/<slug>/brand.json` exists.

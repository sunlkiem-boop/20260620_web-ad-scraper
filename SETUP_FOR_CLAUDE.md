# Setup instructions for Claude

You are helping the person who just opened this folder install three marketing skills on their Mac. Everything you need is in this folder. Follow these steps in order. Stream progress to the user as you go.

## Step 1 — Run the installer

From this folder, run:

```bash
bash install.sh
```

Stream its output to the user. It takes ~2–4 minutes (most of that is downloading Chromium). The installer is idempotent and non-destructive — existing skills are backed up to `*.bak`, and existing brand/brain data is never overwritten.

It will:
- Verify Python 3.11+ is present
- Create a virtual environment at `~/.meta-scraper-venv`
- Install all Python dependencies into that venv (playwright, playwright-stealth==2.0.3, Pillow, markdown_pdf, yt-dlp, requests)
- Download Chromium for Playwright
- Copy the three skills to `~/.claude/skills/`
- Copy the scraper engine to `~/meta-scraper/scrape.py`
- Copy the Aonic Fuel example brand to `~/meta-scraper/brands/aonic-fuel/`
- Seed the marketing brain at `~/Second Marketing Brain/knowledge/`
- Sanity-check that every dependency imports

## Step 2 — If something fails

| Symptom | Fix |
|---|---|
| `python3 not found` or `Python 3.11+ required` | Tell the user to install Python: `brew install python@3.12` (install Homebrew first if needed from brew.sh), then re-run `bash install.sh`. |
| Chromium download hung or failed | Re-run just that step: `~/.meta-scraper-venv/bin/playwright install chromium` |
| A pip dependency failed to build | Make sure Xcode command line tools are present: `xcode-select --install`, then re-run `bash install.sh`. |
| Import sanity check failed | Re-run `bash install.sh`. If it still fails, run the imports manually to see which one breaks: `~/.meta-scraper-venv/bin/python -c "import markdown_pdf, yt_dlp, requests; from PIL import Image; from playwright_stealth import Stealth"` |

Do not skip the installer and try to hand-install — the skills are hard-wired to use `~/.meta-scraper-venv` and the `~/meta-scraper/` and `~/.claude/skills/` locations.

## Step 3 — Verify the install

Run these checks and confirm each:

```bash
ls ~/.claude/skills/                       # expect: scrape-meta-ads  brand-research-sprint  marketing-brain
ls ~/meta-scraper/scrape.py                # the scraper engine
ls ~/meta-scraper/brands/aonic-fuel/       # the example brand profile
~/.meta-scraper-venv/bin/python -c "from playwright_stealth import Stealth; import markdown_pdf; print('deps ok')"
```

## Step 4 — Tell the user they're done

Report success and tell them:

1. **Restart Claude Code** (open a new session) so the three skills load. They can confirm with `/skills`.
2. How to use each skill:
   - **scrape-meta-ads** — paste a Meta Ad Library URL and name the customer: *"Scrape these ads for aonic: `<facebook.com/ads/library URL with view_all_page_id>`"*. Produces a self-contained HTML report with a generation prompt per ad.
   - **brand-research-sprint** — *"Create the foundational docs for `<product URL>`"*. Produces VOC Dossier + Avatar Sheets + Offer Brief + Beliefs (markdown + PDF).
   - **marketing-brain** — *"Ask the marketing brain: how does Mark structure a VSL?"* or *"Add this video to my marketing brain: `<transcript>`"*.
3. Point them at the `examples/` folder for context on what the output looks like — especially `examples/WALKTHROUGH_AONIC_FUEL.html` and the finished deliverables in `examples/aonic-fuel/`. The `aonic-fuel` brand is already installed as a working customer profile they can scrape against immediately.

That's the whole job. Keep it friendly and concise.

#!/usr/bin/env bash
# ============================================================================
# Marketing skills — handoff installer
# ----------------------------------------------------------------------------
# Run ONCE on a fresh Mac to install everything the three skills need:
#   - a Python virtual environment with all dependencies
#   - Chromium (for the Meta Ad Library scraper)
#   - the three skills, into ~/.claude/skills/
#   - the underlying scraper engine, into ~/meta-scraper/scrape.py
#   - bundled example brands (if present in brands/)
#   - the seed "marketing brain" knowledge base
#
#   bash install.sh
#
# Idempotent and non-destructive: existing skills are backed up to *.bak,
# and existing brand / brain data is preserved (never overwritten).
# ============================================================================
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"
VENV="$HOME_DIR/.meta-scraper-venv"

c_blue=$'\033[1;34m'; c_green=$'\033[1;32m'; c_yellow=$'\033[1;33m'; c_red=$'\033[1;31m'; c_reset=$'\033[0m'
step() { echo "${c_blue}→${c_reset} $*"; }
ok()   { echo "${c_green}✓${c_reset} $*"; }
warn() { echo "${c_yellow}!${c_reset} $*"; }
die()  { echo "${c_red}✗${c_reset} $*" >&2; exit 1; }

echo ""
echo "Marketing skills — handoff installer"
echo "===================================="
echo ""

# ---- 1. Python 3.11+ --------------------------------------------------------
step "Checking Python..."
command -v python3 >/dev/null 2>&1 || die "python3 not found. Install Python 3.11+ first (e.g. brew install python@3.12)."
PYV=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYV_MAJOR=$(printf '%s' "$PYV" | cut -d. -f1)
PYV_MINOR=$(printf '%s' "$PYV" | cut -d. -f2)
if [ "$PYV_MAJOR" -lt 3 ] || { [ "$PYV_MAJOR" -eq 3 ] && [ "$PYV_MINOR" -lt 11 ]; }; then
  die "Python 3.11+ required (found $PYV). Install a newer Python, e.g. brew install python@3.12."
fi
ok "Python $PYV"

# ---- 2. Virtual environment -------------------------------------------------
if [ -d "$VENV" ]; then
  ok "venv exists at $VENV"
else
  step "Creating venv at $VENV"
  python3 -m venv "$VENV"
  ok "venv created"
fi

# ---- 3. Python dependencies (all three skills share this one venv) ----------
step "Installing Python dependencies (playwright, playwright-stealth, Pillow, markdown_pdf, yt-dlp, requests)"
"$VENV/bin/python" -m pip install --upgrade pip --quiet
"$VENV/bin/python" -m pip install \
  "playwright" \
  "playwright-stealth==2.0.3" \
  "Pillow" \
  "markdown_pdf" \
  "yt-dlp" \
  "requests" \
  --quiet
ok "Python dependencies installed"

# ---- 4. Chromium (for the Meta Ad Library scraper) --------------------------
step "Installing Chromium for Playwright (~150 MB; can take a minute)"
"$VENV/bin/playwright" install chromium >/dev/null 2>&1
ok "Chromium installed"

# ---- 5. Scraper engine ------------------------------------------------------
mkdir -p "$HOME_DIR/meta-scraper/screenshots" "$HOME_DIR/meta-scraper/runs" "$HOME_DIR/meta-scraper/reports" "$HOME_DIR/meta-scraper/brands"
SCRAPER_DEST="$HOME_DIR/meta-scraper/scrape.py"
if [ -f "$SCRAPER_DEST" ]; then
  step "Backing up existing scraper to scrape.py.bak"
  cp "$SCRAPER_DEST" "$SCRAPER_DEST.bak"
fi
cp "$BUNDLE_DIR/scraper/scrape.py" "$SCRAPER_DEST"
chmod +x "$SCRAPER_DEST"
ok "Scraper engine at $SCRAPER_DEST"

SCRAPER_DEEP_DEST="$HOME_DIR/meta-scraper/scrape_deep.py"
if [ -f "$SCRAPER_DEEP_DEST" ]; then
  step "Backing up existing deep scraper to scrape_deep.py.bak"
  cp "$SCRAPER_DEEP_DEST" "$SCRAPER_DEEP_DEST.bak"
fi
cp "$BUNDLE_DIR/scraper/scrape_deep.py" "$SCRAPER_DEEP_DEST"
chmod +x "$SCRAPER_DEEP_DEST"
ok "Deep scraper engine at $SCRAPER_DEEP_DEST"

# ---- 6. Skills --------------------------------------------------------------
SKILLS_DIR="$HOME_DIR/.claude/skills"
mkdir -p "$SKILLS_DIR"
for skill_dir in "$BUNDLE_DIR/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  dest="$SKILLS_DIR/$name"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    warn "Existing skill '$name' — backing up to ${name}.bak"
    rm -rf "${dest}.bak"
    mv "$dest" "${dest}.bak"
  fi
  cp -R "$skill_dir" "$dest"
  find "$dest/scripts" -type f \( -name '*.py' -o -name '*.sh' \) -exec chmod +x {} \; 2>/dev/null || true
  ok "Skill: $name"
done

# ---- 7. Example brands -------------------------------------------------------
if [ -d "$BUNDLE_DIR/brands" ]; then
  for brand_dir in "$BUNDLE_DIR/brands"/*/; do
    [ -d "$brand_dir" ] || continue
    name=$(basename "$brand_dir")
    dest="$HOME_DIR/meta-scraper/brands/$name"
    if [ -d "$dest" ]; then
      warn "Brand '$name' already exists at $dest — leaving your copy untouched"
    else
      cp -R "$brand_dir" "$dest"
      ok "Brand: $name"
    fi
  done
fi

# ---- 8. Marketing-brain seed knowledge --------------------------------------
BRAIN_SRC="$BUNDLE_DIR/marketing-brain-data/knowledge"
BRAIN_DEST="$HOME_DIR/Second Marketing Brain/knowledge"
if [ -d "$BRAIN_SRC" ]; then
  if [ -d "$BRAIN_DEST" ]; then
    warn "Marketing brain already exists at $BRAIN_DEST — leaving your copy untouched"
  else
    mkdir -p "$(dirname "$BRAIN_DEST")"
    cp -R "$BRAIN_SRC" "$BRAIN_DEST"
    ok "Marketing brain seeded at $BRAIN_DEST"
  fi
fi

# ---- 9. Sanity check --------------------------------------------------------
step "Sanity-checking that all dependencies import"
"$VENV/bin/python" - <<'PY' >/dev/null || die "Import sanity check failed. Re-run this script; if it persists, see README.md troubleshooting."
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from PIL import Image
import markdown_pdf
import yt_dlp
import requests
print("ok")
PY
ok "All imports work"

# ---- Done -------------------------------------------------------------------
echo ""
echo "${c_green}ALL DONE.${c_reset}"
echo ""
echo "Installed skills:"
for f in "$SKILLS_DIR"/*/SKILL.md; do
  [ -f "$f" ] || continue
  echo "  - $(basename "$(dirname "$f")")"
done
echo ""
echo "Open Claude Code in any directory and try:"
echo "  • \"Scrape these ads for <your-brand>: <Meta Ad Library URL>\""
echo "  • \"Create the foundational docs for <product URL>\""
echo "  • \"Ask the marketing brain: how does Mark structure a VSL?\""
echo ""
echo "Skills auto-load from ~/.claude/skills/ in your next Claude Code session."
echo ""

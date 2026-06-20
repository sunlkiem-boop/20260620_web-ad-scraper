"""Creator slug resolution and metadata bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

from .paths import DEFAULT_CREATOR_SLUG, SOURCES_DIR, creator_dir, creator_index, creator_meta

# channel → slug. Extend as new creators are added.
CHANNEL_TO_SLUG = {
    "Mark Builds Brands": "mark-builds-brands",
    "@markbuildsbrands": "mark-builds-brands",
}

DEFAULT_META = {
    "mark-builds-brands": {
        "name": "Mark Builds Brands",
        "channel": "@markbuildsbrands",
        "channel_url": "https://www.youtube.com/@markbuildsbrands",
        "focus": [
            "direct-response copywriting",
            "Meta / Facebook ad scaling",
            "Andromeda algorithm strategy",
            "VSLs, advertorials, quiz funnels",
            "AI-powered creative production",
            "AI agentic workflows for marketing",
            "branded dropshipping / ecommerce scaling",
            "funnel economics (CAC / LTV / AOV)",
        ],
        "signature_phrases": [
            "run more ads",
            "the creative is the targeting",
            "copy is the foundation of everything",
            "AI is a vehicle, not a strategy",
            "Facebook doesn't play by the rules",
            "the winning message, not the winning ad",
            "think like a mad scientist, not like a marketer",
            "ugly ads = pretty profits",
            "clarity over cleverness",
            "swipe the philosophy, not the copy",
            "purple ocean theory",
            "success is a game of subtraction, not addition",
            "disguise your marketing",
            "data is data",
            "quiz funnels are the foreplay of funnels",
            "marketing is a game of belief change",
        ],
        "answer_style_override": "hybrid",
    }
}


def resolve_slug(channel_name: str | None, override: str | None) -> str:
    if override:
        return override
    if channel_name and channel_name in CHANNEL_TO_SLUG:
        return CHANNEL_TO_SLUG[channel_name]
    return DEFAULT_CREATOR_SLUG


def ensure_creator(slug: str) -> Path:
    d = creator_dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    meta_path = creator_meta(slug)
    if not meta_path.exists():
        meta = DEFAULT_META.get(slug, {"name": slug, "channel": "", "channel_url": "", "focus": [], "signature_phrases": []})
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    index_path = creator_index(slug)
    if not index_path.exists():
        index_path.write_text(f"# {slug} — videos\n\n_Auto-generated. Run reindex.py to refresh._\n", encoding="utf-8")
    return d

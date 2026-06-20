"""Centralized paths for the marketing-brain skill.

Edit KNOWLEDGE_DIR if you move the data folder.
"""
from pathlib import Path

KNOWLEDGE_DIR = Path.home() / "Second Marketing Brain" / "knowledge"
SOURCES_DIR = KNOWLEDGE_DIR / "sources"
GLOBAL_INDEX = KNOWLEDGE_DIR / "_global_index.md"

DEFAULT_CREATOR_SLUG = "mark-builds-brands"


def creator_dir(slug: str) -> Path:
    return SOURCES_DIR / slug


def transcript_path(slug: str, video_id: str) -> Path:
    return creator_dir(slug) / f"{video_id}.transcript.md"


def summary_path(slug: str, video_id: str) -> Path:
    return creator_dir(slug) / f"{video_id}.summary.md"


def creator_meta(slug: str) -> Path:
    return creator_dir(slug) / "_meta.json"


def creator_index(slug: str) -> Path:
    return creator_dir(slug) / "_index.md"

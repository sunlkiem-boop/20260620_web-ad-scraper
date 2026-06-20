#!/usr/bin/env python3
"""List videos in the marketing brain.

Usage:
    python3 list_videos.py [--creator <slug>] [--topic <topic>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reindex import collect


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--creator", help="Filter by creator slug")
    p.add_argument("--topic", help="Filter by topic")
    args = p.parse_args()

    rows = collect()
    if args.creator:
        rows = [r for r in rows if r["_creator_slug"] == args.creator]
    if args.topic:
        rows = [r for r in rows if args.topic in (r.get("topics") or [])]

    if not rows:
        print("(no videos)")
        return 0

    rows.sort(key=lambda r: r.get("upload_date", ""), reverse=True)
    for r in rows:
        topics = ", ".join(r.get("topics") or [])
        print(
            f"{r.get('upload_date', '?'):10}  "
            f"[{r['_creator_slug']:<20}]  "
            f"{r.get('title', '(no title)')[:80]:<80}  "
            f"topics: {topics}"
        )
    print(f"\n{len(rows)} videos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

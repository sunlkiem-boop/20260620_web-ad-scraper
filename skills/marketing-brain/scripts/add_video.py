#!/usr/bin/env python3
"""Fetch a YouTube video's transcript + metadata and save it to the marketing brain.

Usage:
    python3 add_video.py <youtube_url> [--creator <slug>] [--force]

The script ONLY fetches and stores the raw transcript. Summarization is done by
Claude after reading the transcript file. After all videos are added, run
reindex.py to rebuild the indexes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python3 scripts/add_video.py ...` from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.creators import ensure_creator, resolve_slug
from lib.paths import transcript_path
from lib.transcript import TranscriptUnavailable, YtDlpMissing, fetch


def write_transcript_file(path: Path, data) -> None:
    fm = [
        "---",
        f"video_id: {data.video_id}",
        f"title: {_yaml_escape(data.title)}",
        f"channel: {_yaml_escape(data.channel)}",
        f"channel_url: {data.channel_url}",
        f"url: https://www.youtube.com/watch?v={data.video_id}",
        f"upload_date: {data.upload_date}",
        f"duration_seconds: {data.duration_seconds}",
    ]
    if data.view_count is not None:
        fm.append(f"view_count: {data.view_count}")
    fm.append(f"transcript_source: {data.source}")
    fm.append("---")

    body = [
        f"\n# {data.title}\n",
        "## Description\n",
        data.description.strip() or "_(no description)_",
        "\n## Transcript (plain)\n",
        data.transcript_text.strip(),
        "\n\n## Transcript (with timestamps)\n",
        "```",
        data.transcript_with_timestamps.strip(),
        "```",
        "",
    ]
    path.write_text("\n".join(fm) + "\n".join(body), encoding="utf-8")


def _yaml_escape(s: str) -> str:
    s = (s or "").replace("\n", " ").strip()
    if any(c in s for c in [":", "#", "'", '"', "[", "]", "{", "}", "|", ">", "&", "*", "!", "%", "@", "`"]):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url", help="YouTube video URL")
    p.add_argument("--creator", help="Creator slug override (default: auto-detect, fallback mark-builds-brands)")
    p.add_argument("--force", action="store_true", help="Overwrite existing transcript file")
    args = p.parse_args()

    try:
        data = fetch(args.url)
    except YtDlpMissing as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except TranscriptUnavailable as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"ERROR fetching {args.url}: {e}", file=sys.stderr)
        return 1

    slug = resolve_slug(data.channel, args.creator)
    ensure_creator(slug)
    out = transcript_path(slug, data.video_id)

    if out.exists() and not args.force:
        print(f"ALREADY EXISTS: {out} (pass --force to overwrite)")
        # Still print metadata so Claude can decide to skip
        print(f"video_id={data.video_id}")
        print(f"title={data.title}")
        print(f"channel={data.channel}")
        print(f"creator_slug={slug}")
        return 0

    write_transcript_file(out, data)
    print(f"WROTE: {out}")
    print(f"video_id={data.video_id}")
    print(f"title={data.title}")
    print(f"channel={data.channel}")
    print(f"creator_slug={slug}")
    print(f"upload_date={data.upload_date}")
    print(f"transcript_source={data.source}")
    print(f"NEXT: read this file, write {out.with_suffix('').with_suffix('.summary.md').name}, then run reindex.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

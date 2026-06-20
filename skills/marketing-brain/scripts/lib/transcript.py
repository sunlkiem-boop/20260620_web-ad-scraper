"""yt-dlp wrapper: fetch transcript + metadata for a YouTube URL.

Uses the yt-dlp CLI (not the Python module) so the user only needs
`pip3 install -U yt-dlp` once. Returns plain text plus structured metadata.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class YtDlpMissing(RuntimeError):
    pass


class TranscriptUnavailable(RuntimeError):
    pass


@dataclass
class VideoData:
    video_id: str
    title: str
    channel: str
    channel_url: str
    upload_date: str  # YYYY-MM-DD
    duration_seconds: int
    view_count: int | None
    description: str
    transcript_text: str  # plain text, no timing
    transcript_with_timestamps: str  # [mm:ss] line per cue, useful for citations
    source: str  # "manual" or "auto"


def _ensure_yt_dlp() -> str:
    path = shutil.which("yt-dlp")
    if not path:
        raise YtDlpMissing(
            "yt-dlp is not installed. Run: pip3 install -U yt-dlp"
        )
    return path


def _format_upload_date(yt_dlp_date: str) -> str:
    # yt-dlp gives "20260119" — convert to "2026-01-19"
    if not yt_dlp_date or len(yt_dlp_date) != 8:
        return yt_dlp_date or ""
    return f"{yt_dlp_date[:4]}-{yt_dlp_date[4:6]}-{yt_dlp_date[6:8]}"


_VTT_TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.\d{3} --> ")
_VTT_TAG = re.compile(r"<[^>]+>")


def _parse_vtt(vtt: str) -> tuple[str, str]:
    """Return (plain_text, timestamped_text).

    Strips WebVTT header, timing lines, inline tags, and dedupes consecutive
    identical lines (yt auto-captions overlap a lot).
    """
    plain_lines: list[str] = []
    stamped_lines: list[str] = []
    current_time: str | None = None
    last_text: str | None = None

    for raw in vtt.splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("NOTE", "Kind:", "Language:")):
            continue
        m = _VTT_TIME.match(line)
        if m:
            hh, mm, ss = m.group(1), m.group(2), m.group(3)
            # If hours are 00, use mm:ss; else hh:mm:ss
            current_time = f"{mm}:{ss}" if hh == "00" else f"{hh}:{mm}:{ss}"
            continue
        # Cue text — strip inline tags
        text = _VTT_TAG.sub("", line).strip()
        if not text or text == last_text:
            continue
        plain_lines.append(text)
        stamped_lines.append(f"[{current_time or '00:00'}] {text}")
        last_text = text

    return "\n".join(plain_lines), "\n".join(stamped_lines)


def fetch(url: str) -> VideoData:
    yt_dlp = _ensure_yt_dlp()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # First: grab metadata + try manual EN subs, then auto-EN as fallback
        cmd = [
            yt_dlp,
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "en.*,en",
            "--sub-format",
            "vtt",
            "--write-info-json",
            "-o",
            str(tmp_path / "%(id)s.%(ext)s"),
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"yt-dlp failed (exit {result.returncode}):\n{result.stderr.strip()}"
            )

        info_files = list(tmp_path.glob("*.info.json"))
        if not info_files:
            raise RuntimeError("yt-dlp did not produce an info.json")
        info = json.loads(info_files[0].read_text(encoding="utf-8"))

        # Find best VTT — prefer manual (no .auto in name), then auto.
        all_vtts = sorted(tmp_path.glob("*.vtt"))
        manual_vtts = [p for p in all_vtts if "auto" not in p.suffixes[-2:]
                       and not p.name.endswith(".en.auto.vtt")]
        # yt-dlp names auto subs like "<id>.en.vtt" too (auto-generated CC), but
        # there's no clean flag. Heuristic: if subtitles in info json, manual exists.
        sub_source = "manual" if info.get("subtitles", {}).get("en") else "auto"
        if not all_vtts:
            raise TranscriptUnavailable(
                "No English subtitles (manual or auto) available for this video."
            )
        vtt_text = all_vtts[0].read_text(encoding="utf-8", errors="ignore")
        plain, stamped = _parse_vtt(vtt_text)
        if not plain.strip():
            raise TranscriptUnavailable("Subtitle file was empty after parsing.")

        return VideoData(
            video_id=info["id"],
            title=info.get("title", ""),
            channel=info.get("channel", info.get("uploader", "")),
            channel_url=info.get("channel_url", info.get("uploader_url", "")),
            upload_date=_format_upload_date(info.get("upload_date", "")),
            duration_seconds=int(info.get("duration", 0) or 0),
            view_count=info.get("view_count"),
            description=info.get("description", "") or "",
            transcript_text=plain,
            transcript_with_timestamps=stamped,
            source=sub_source,
        )

# marketing-brain skill

A persistent, file-based knowledge base built from marketing creators' YouTube videos. Claude reads the indexes and summaries to answer marketing questions in a hybrid voice: neutral expert + the creator's signature phrases verbatim, with citations on every claim.

## One-time setup

```bash
~/.meta-scraper-venv/bin/python -m pip install -U yt-dlp
```

That's it (and the handoff installer already did this) — the skill is registered automatically because it lives under `~/.claude/skills/`.

## Where the data lives

`~/Second Marketing Brain/knowledge/` — edit `scripts/lib/paths.py` to change.

## How to use it (talking to Claude)

- **Add a video:** "Add this video to my marketing brain: `<youtube_url>`"
- **Bulk seed:** Paste a list of YouTube URLs and say "seed the brain with these"
- **Ask:** "Ask the marketing brain: how does Mark structure a VSL?"
- **List:** "What's in my marketing brain about copy?"

## How it works under the hood

Claude does the smart parts (deciding when to add, what to extract, how to answer). The Python scripts handle the deterministic parts:

| Script | Job |
|---|---|
| `add_video.py URL` | yt-dlp fetch → write `<id>.transcript.md` with metadata frontmatter |
| `reindex.py` | Rebuild `_global_index.md` + each creator's `_index.md` from summary frontmatter |
| `list_videos.py` | Print stored videos (filterable by creator/topic) |

After `add_video.py` runs, Claude reads the transcript and writes a structured `<id>.summary.md` next to it. Then `reindex.py` aggregates everything.

## Adding a new creator

The skill auto-creates a creator folder when `add_video.py` sees a new channel — but to get nice defaults (display name, signature phrases for verbatim citations) add an entry to `CHANNEL_TO_SLUG` and `DEFAULT_META` in `scripts/lib/creators.py`.

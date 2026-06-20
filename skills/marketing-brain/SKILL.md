---
name: marketing-brain
description: Use this skill whenever the user wants to query, build, or update their personal knowledge base of marketing-creator YouTube videos (their "second marketing brain"). The brain stores transcripts + structured summaries on disk and answers questions in a hybrid voice that paraphrases the creator neutrally while quoting their signature phrases verbatim and citing every claim. Triggers on phrases like "ask the marketing brain", "ask my second brain", "what does Mark say about X", "what would Mark Builds Brands say about X", "according to MBB", "according to [creator]", "add this video to my marketing brain", "save this transcript to the brain", "seed the brain with this", "list videos in my marketing brain", "what's in my brain about [topic]", or the user pastes a video transcript and asks to add/summarize it. The primary seeded creator is Mark Builds Brands (channel @markbuildsbrands) — focus areas: direct-response copy, Meta/Facebook ad scaling, Andromeda algorithm strategy, VSLs/advertorials/quiz funnels, AI-powered creative production, branded dropshipping, funnel economics (CAC/LTV/AOV). Do NOT trigger for: general marketing questions not directed at the brain, YouTube videos unrelated to marketing, requests to download/watch videos for other purposes.
---

# Marketing Brain — YouTube Knowledge Base for Marketing Creators

A persistent, file-based knowledge base built from marketing creators' YouTube transcripts. The user adds videos one at a time (or in batches). You write the transcript file, distill a structured summary, index it, and later answer questions by reading the index + relevant summaries + (when needed) transcript chunks.

## Where everything lives

**Skill code** (this directory): `~/.claude/skills/marketing-brain/`

**Knowledge data** (the actual brain): `~/Second Marketing Brain/knowledge/`

```
knowledge/
├── _global_index.md                          # master topic → video map (read FIRST for any query)
└── sources/
    └── <creator-slug>/                       # e.g. mark-builds-brands
        ├── _meta.json                        # creator name, signature phrases, frameworks, tools, missing videos
        ├── _index.md                         # this creator's video list with topics (auto-generated)
        ├── <video_id>.transcript.md          # raw transcript + metadata frontmatter
        └── <video_id>.summary.md             # distilled: TL;DR / frameworks / principles / tactics / quotes / tools / caveats
```

Data path is set in `scripts/lib/paths.py` — edit `KNOWLEDGE_DIR` if the user moves the folder.

## Primary workflow: manual transcript paste (preferred)

The user has indicated this is faster and more reliable than scraping. Use this path by default.

Triggers: user pastes one or more YouTube video titles + transcripts and says "add to brain", "save to brain", "seed the brain", "add this video", or implies it ("here's the transcript for…").

Steps for each pasted video:

1. **Choose a slug-style `video_id`** from the title — short, kebab-case, descriptive (e.g. `quiz-funnels-playbook`, `ai-ads-30-days`, `meta-ads-algorithm`). Keep IDs stable; never rename later.
2. **Write the transcript file** at `sources/mark-builds-brands/<id>.transcript.md` (or the appropriate creator) using this frontmatter:

   ```yaml
   ---
   video_id: <slug>
   title: "<full title>"
   channel: Mark Builds Brands
   channel_url: https://www.youtube.com/@markbuildsbrands
   url: <actual YouTube URL if known, else the channel URL>
   upload_date: <YYYY-MM-DD if known, else "unknown">
   duration_seconds: <if known, else "unknown">
   transcript_source: manual
   ---
   ```

   Then a body with `# <title>`, a `## Description` section (or `_(manually pasted by user — original video URL not captured)_`), and `## Transcript (plain)` containing the user's pasted text verbatim. Preserve their formatting — including the `[ __ ]` censoring, line breaks, and any timestamps if present.

3. **Write the summary file** at `<id>.summary.md` using the exact section structure below. This is the unit of recall — keep dense, structured, and consistent across videos:

   ```markdown
   ---
   video_id: <slug>
   title: "<title>"
   creator: mark-builds-brands
   channel: Mark Builds Brands
   url: <url>
   upload_date: <date or unknown>
   duration_seconds: <int or unknown>
   topics: [comma, separated, primary, topics — be specific, 8-15 tags is normal]
   ---

   # <title>

   ## TL;DR
   2-4 sentences. What's the video about and what's the main argument. Lead with results/numbers if mentioned.

   ## Frameworks & models
   Named or implied frameworks the creator uses. For each: 1-2 sentence definition + when it applies. Use bold for framework names.

   ## Key principles
   Bullet list of opinions/heuristics stated as if the creator were saying them. Keep them sharp and quote-worthy.

   ## Tactics & playbook steps
   Concrete how-to — numbered, actionable. Include exact numbers, ratios, tools, specific recommended phrases. If the video has a step-by-step setup (like an ad-account walkthrough), capture it in full.

   ## Signature quotes (verbatim)
   Up to 5 short verbatim quotes that capture the creator's voice. Each <30 words. Include `[mm:ss]` timestamp if findable in the transcript.

   ## Tools / resources mentioned
   Software, books, people, URLs, DM keywords.

   ## Counterpoints / caveats
   Anything flagged as risky, exceptions, contrarian opinions, "most people get this wrong" admissions.

   ## Citations
   - [<title>](<url>) — Mark Builds Brands
   ```

4. **Run reindex** once you've finished adding videos in a batch:
   ```bash
   ~/.meta-scraper-venv/bin/python ~/.claude/skills/marketing-brain/scripts/reindex.py
   ```
   This rebuilds `_global_index.md` and the per-creator `_index.md` from summary frontmatter. Don't hand-edit indexes.

## Alternative workflow: yt-dlp fetch (when user gives a bare URL)

Triggers: user pastes a YouTube URL and says "add to brain" / "save" — without a transcript.

1. Run `~/.meta-scraper-venv/bin/python ~/.claude/skills/marketing-brain/scripts/add_video.py <URL>`. This uses `yt-dlp` to fetch the transcript via official captions and writes `<youtube_video_id>.transcript.md` with full metadata (upload date, duration, view count, etc.).
2. If `yt-dlp` isn't installed, run `~/.meta-scraper-venv/bin/python -m pip install -U yt-dlp` (the installer preinstalls it, so this is rarely needed).
3. Then proceed to summary + reindex as in the manual workflow (steps 3-4 above).

## Answering a question (the main use case)

Triggers: "ask the brain ...", "what does Mark say about ...", "according to MBB ...", or any marketing question while the user explicitly references the brain.

Steps:

1. **Read `_global_index.md` first.** Topic → video map. Use it to decide which summaries to load. Do NOT skip this step.
2. Read 1-4 relevant `*.summary.md` files. Pick by topic match. Prefer fewer high-relevance summaries over many tangential ones.
3. If you need to verify a quote or pull more detail than the summary has, open the corresponding `*.transcript.md` and grep for the relevant section. Don't load full transcripts pre-emptively — the 8-years transcript alone is ~30K tokens.
4. **Answer in hybrid style:**
   - Default voice: neutral expert, paraphrasing the creator's framing using their structures (e.g. organizing answers around "ad economics / funnel economics / backend economics" or "stage of awareness × level of consciousness").
   - Quote signature phrases **verbatim in quotation marks** when they fit naturally — pull from the creator's `_meta.json` `signature_phrases` list (or the summary's `Signature quotes` section). Examples for Mark: *"the creative is the targeting"*, *"copy is the foundation of everything"*, *"think like a mad scientist, not like a marketer"*, *"ugly ads = pretty profits"*, *"Facebook doesn't play by the rules"*.
   - **Every substantive claim has an inline citation** in the form `([video title](url))` at sentence end. No footer blocks.
   - If the brain has no relevant content, say so plainly — don't invent the creator's opinions. Suggest which video the user might want to add next.
5. End with a short "Sources used" list pointing to the summary files you read.

## Listing / browsing the brain

Triggers: "what's in my marketing brain", "list videos", "what do I have on `<topic>`".

```bash
~/.meta-scraper-venv/bin/python ~/.claude/skills/marketing-brain/scripts/list_videos.py
# optional filters:
~/.meta-scraper-venv/bin/python ~/.claude/skills/marketing-brain/scripts/list_videos.py --topic "Andromeda"
~/.meta-scraper-venv/bin/python ~/.claude/skills/marketing-brain/scripts/list_videos.py --creator mark-builds-brands
```

## Answer style — hybrid (locked-in)

The user picked this style. Don't change it without being asked.

- Tone: neutral, direct. Tight answers — no fluff.
- Mark's voice surfaces through **verbatim quoted signature phrases** and **his framings** (organize around his structures: contrast, purple ocean, stages of awareness × consciousness, 4-step Meta pipeline, LTV:CAC ratios, AI non-negotiables, quiz funnel 3 pillars, etc.)
- Citations on every paragraph minimum. Never claim Mark said something without pointing at the video.
- If two videos contradict each other (e.g. variations vs new concepts before/after Andromeda), surface that explicitly — don't paper over.
- When a question crosses multiple videos, organize the answer by his framework rather than by video.

## Operational rules

- **Never invent transcripts or quotes.** If a transcript doesn't have what you need, say so. Don't hallucinate Mark's opinions.
- **Never hand-edit `_global_index.md` or `_index.md`.** `reindex.py` owns them — your edits will be overwritten.
- **Summary files are the primary unit of recall.** Keep them dense, structured, and consistent across videos. That's what makes the brain useful months from now.
- When unsure which creator a video belongs to, ask the user once rather than guessing.
- Default creator slug for Mark Builds Brands: `mark-builds-brands` (channel `@markbuildsbrands`, IG `@markbuildsbrand`).
- The `_meta.json` for each creator holds their signature phrases, frameworks, tools, and known-missing videos. Read it when answering to source the right verbatim quotes.

## Currently seeded videos (as of 2026-05-16)

Six Mark Builds Brands videos:
1. `8-years-marketing-advice` — flagship long-form (think/create/math/multiply)
2. `meta-ads-algorithm` — 4-step pipeline + value formula
3. `andromeda-update-explained` — retrieval algorithm change + new concepts vs variations
4. `testing-ads-post-andromeda` — exact CBO playbook
5. `quiz-funnels-playbook` — 3 pillars: micro-commit / seed / pre-handle
6. `ai-ads-30-days` — AI creative production stack

**Missing / pending re-paste:** `vsl-ads-playbook` ($1,525,513 with VSLs — user's first paste was a duplicate of the quiz-funnels content; awaiting re-paste of the actual VSL transcript).

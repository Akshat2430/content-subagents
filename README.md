# content-subagents

Point Claude Code at a long-form transcript. Get back a thread, a blog post, and a newsletter section. Each written by a specialist subagent, reviewed by a QA pass, dropped into a timestamped folder.

## Why this exists

You make long-form content (a video, a podcast, a talk). It should be repurposed into shorter formats. In practice it doesn't get repurposed, because doing it by hand is more work than making the original. And dumping the transcript into a single Claude session and asking for "all of it" produces three pieces that all sound the same.

This is the same idea as hiring a team instead of one person doing five jobs: specialization, separation of context, a review step at the end.

## How to use it

From inside this folder in Claude Code, you have two ways in:

**You already have a transcript file:**
```
/repurpose samples/example-transcript.md
```

**You have a YouTube link:**
```
/yt https://www.youtube.com/watch?v=XXXXXXXXXXX
```
This pulls the transcript via `scripts/fetch_yt.py`, drops it into the run folder as `_source.md`, and then runs the same pipeline. Works on `youtube.com/watch`, `youtu.be/`, and `youtube.com/shorts/` URLs. Requires `pip install -r scripts/requirements.txt` once.

In either case, the orchestrator will:

1. Create a timestamped folder under `content-drops/`
2. Run three writer subagents in parallel, each with its own context and personality
3. Run a QA subagent over the outputs against the original transcript
4. Report one line to the main session — your context barely moves

Open the folder. The pieces are ready to copy-paste.

## Repo layout

```
.claude/
  agents/                   # subagent definitions (Claude Code convention)
    thread-writer.md
    blog-writer.md
    newsletter-writer.md
    qa-reviewer.md
  commands/
    repurpose.md            # the /repurpose slash command
personalities/              # voice/style rules — main tuning surface
  thread.md
  blog.md
  newsletter.md
content-drops/              # gitignored; run outputs land here
samples/
  example-transcript.md
  example-output/             # a real run, committed verbatim
README.md
```

## Tuning it

Edit the files in `personalities/`. That's where voice, structural rules, and anti-patterns live. Adding an anti-pattern ("stop writing `leverage`") is a one-line change and takes effect on the next run.

The subagent files under `.claude/agents/` define *what each agent does* — you shouldn't need to edit those often. The personality files define *how it sounds*.

### Make it sound like you, not me

Each file in `personalities/` ends with a `## Personal quirks` section — those are *my* quirks (how I open posts, what asides I'm okay with, the hook templates I refuse to use). They're in there as a working example, not a prescription.

**Before your first real run, replace that section.** A few prompts that surface useful quirks:
- What's a phrase you cringe at when AI writes it for you?
- What's an opener you'd never use? What's one you actually use a lot?
- Which formats are you in the story (first-person scenes) vs. observing it from outside?
- Where are you comfortable admitting "I don't know"?
- Any words on a permanent ban list? (Mine: `leverage`, `unlock`, `cutting-edge`.)

Three or four lines per file is plenty. The `## Voice`, `## Structure`, and `## Anti-patterns` sections above the quirks are general enough to leave alone.

## Example output folder

```
content-drops/2026-04-22-1430-ai-adoption-fails/
  _source.md          # copy of the input transcript
  thread.md
  blog.md
  newsletter.md
  qa-brief.md         # QA findings across all three pieces
```

A real run from this repo is checked in at [`samples/example-output/`](samples/example-output/) — open it to see what the three pieces and the QA brief actually look like before you run the tool yourself.

## Adding a new format

1. Add a new subagent file at `.claude/agents/<name>-writer.md` following the pattern of the existing ones.
2. Add a matching personality file at `personalities/<name>.md`.
3. Add the new subagent name to the parallel dispatch list in `.claude/commands/repurpose.md`.
4. Teach the QA reviewer about the new file in `.claude/agents/qa-reviewer.md`.

## What's intentionally not here

- **Posting to any platform.** This produces drafts, not posts. Copy-paste is the handoff.
- **Spotify / arbitrary podcast URL ingestion.** YouTube is supported via `/yt`; for other sources, bring the transcript file and use `/repurpose`.
- **Unbounded revision loops.** QA runs once, the orchestrator dispatches a single auto-revision round for any writer it flagged, then stops. If issues remain after that, run `/redo <writer> <folder>` yourself.

## What it does remember across runs

`memory/used-hooks.md` accumulates the opening lines from every run. Writers read it before drafting and avoid recycling earlier openers, so post 30 doesn't sound like post 3. The file is local-only (gitignored) and capped at 20 entries.

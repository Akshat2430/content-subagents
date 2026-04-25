---
description: Fetch a YouTube transcript from a link and run the full repurpose pipeline on it. INVOKE PROACTIVELY whenever the user pastes a YouTube URL (youtube.com/watch, youtu.be/, youtube.com/shorts/) and is asking to repurpose, turn into posts, make content from, or distribute it — even if they don't type the slash command. Pass the URL as the argument.
argument-hint: <youtube-url>
---

Paste-a-link version of `/repurpose`. You are the orchestrator. You are NOT writing any of the content yourself.

## Step 1 — Validate input

- If `$1` is empty, tell the user the command needs a YouTube URL and stop.
- If `$1` doesn't look like a YouTube URL (no `youtube.com` or `youtu.be`), tell the user and stop. Do not guess.

## Step 2 — Set up the output folder

1. Get the current date/time in `YYYY-MM-DD-HHMM` format.
2. Create the folder: `content-drops/<YYYY-MM-DD-HHMM>-yt/` using `mkdir -p`. (Slug will be refined after fetch.)
3. Resolve it to an absolute path.

## Step 3 — Fetch the transcript

Run:

```
python3 scripts/fetch_yt.py "$1" "<absolute-folder>/_source.md"
```

- If the script exits non-zero, print the stderr message to the user and stop. Do not continue to writers.
- On success, read the first line of `_source.md` (the `# Title` heading) and derive a slug: lowercase, replace spaces with hyphens, strip punctuation, cap at 40 chars.
- Rename the folder from `<timestamp>-yt` to `<timestamp>-<slug>` using `mv`. Update your absolute path.

## Step 3b — Summarize first, but only for long transcripts

Run `wc -w "<absolute-path-to-_source.md>"` to get the word count.

- If word count is **under 4000**, skip this step.
- If **4000 or more**, invoke the `transcript-summarizer` subagent (sequentially, before writers):

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
>
> Produce a structured brief at `<output-folder>/_brief.md`. Report back with the path.

The brief becomes the writers' compact source of truth. The full transcript stays at `_source.md` for verbatim quote lookup.

## Step 4 — Dispatch the four writers in parallel

Invoke these four subagents in a SINGLE message with four parallel Task tool calls (not sequential):

- `thread-writer`
- `blog-writer`
- `newsletter-writer`
- `clips-writer`

Each call's prompt should be exactly this template (with the absolute paths filled in):

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
>
> Read your personality file, read the transcript, write your output file into the output folder per your spec. Report back with the path to the file you wrote.

Running them in parallel is non-negotiable.

## Step 5 — Run QA

Once all four writers have returned, invoke the `qa-reviewer` subagent with this prompt:

> Output folder: `<absolute-path-to-run-folder>`
>
> Read _source.md, thread.md, blog.md, newsletter.md, clips.md. Read the four personality files under personalities/. Write qa-brief.md with your findings. Report back with the path and total issue count.

## Step 6 — Revision loop (one round, automatic)

After QA returns, read `<folder>/qa-findings.json`.

For each writer key (`thread`, `blog`, `newsletter`, `clips`) whose `issues` array is non-empty, invoke its writer subagent in revision mode. Dispatch all needed revisions in a SINGLE message with parallel Task tool calls.

Each revision call's prompt:

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
> Previous draft path: `<absolute-path-to-<writer>.md>`
> Revision notes:
> - <issue 1>
> - <issue 2>
>
> You are in revision mode. Read your personality file, your previous draft, and address each note. Overwrite the same output file. Report back with the path.

After all revisions return, invoke `qa-reviewer` once more on the same folder.

**Hard cap: one revision round.** If post-revision QA still flags issues, do not loop again. The user can run `/redo <writer> <folder>` manually.

Skip this step if the first QA's findings JSON has zero issues across all four files.

## Step 6b — Update used-hooks memory

After the final QA pass, append to `memory/used-hooks.md` at the project root. Create if missing.

Format:

```
## <YYYY-MM-DD> — <slug>

- thread opener: <first non-blank line of thread.md>
- blog opener: <first sentence of opening paragraph of blog.md, after the H1>
- newsletter opener: <first sentence of newsletter.md>
- clip 1 hook: <text after "## Clip 1 — ">
- clip 2 hook: <text after "## Clip 2 — ">
- clip 3 hook: <text after "## Clip 3 — ">
```

Skip lines for any file that's a `# Failed` stub. Do not crash the run for memory-write issues — mention "memory not updated" in the final report if the write fails.

## Step 7 — Report back to the user

Print exactly one line. Format:

- No revisions needed: `Done. <folder>/ — clean on first pass.`
- Revisions ran: `Done. <folder>/ — revised <N> pieces; <M> issues remain.`

Do not dump the drafts into the main session.

## If a writer subagent fails

Write a stub file at the expected path containing a single line: `# Failed — <short reason>` and continue to QA. Mention the failure in the final report line.

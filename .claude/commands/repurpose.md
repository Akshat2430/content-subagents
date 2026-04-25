---
description: Turn a long-form transcript into a full distribution pack (thread, blog, newsletter) with QA
argument-hint: <path-to-transcript>
---

Repurpose the transcript at: $1

You are the orchestrator for a content distribution run. Your job is to coordinate specialist subagents and produce a clean output folder. You are NOT writing any of the content yourself.

## Step 1 — Validate input

- If `$1` is empty, tell the user the command needs a transcript path and stop.
- If the file at `$1` doesn't exist, tell the user and stop. Do not guess or substitute.
- Resolve `$1` to an absolute path for the rest of the run.

## Step 2 — Set up the output folder

1. Read the transcript file.
2. Derive a slug: take the first H1 heading if present, otherwise the filename without extension. Lowercase, replace spaces with hyphens, strip punctuation, cap at 40 characters.
3. Get the current date/time in `YYYY-MM-DD-HHMM` format.
4. Create the folder: `content-drops/<YYYY-MM-DD-HHMM>-<slug>/` using `mkdir -p`.
5. Copy the original transcript to `<folder>/_source.md`.

All subsequent paths you pass to subagents must be absolute.

## Step 2b — Summarize first, but only for long transcripts

Run `wc -w "<absolute-path-to-_source.md>"` to get the word count.

- If word count is **under 4000**, skip this step entirely. The writers can read the transcript directly.
- If word count is **4000 or more**, invoke the `transcript-summarizer` subagent (sequentially, before dispatching writers) with this prompt:

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
>
> Produce a structured brief at `<output-folder>/_brief.md`. Report back with the path.

The brief gives all four writers a compact source of truth, so each one doesn't re-read 25k+ tokens. The full transcript stays at `_source.md` for verbatim quote lookup.

## Step 3 — Dispatch the three writers in parallel

Invoke these three subagents in a SINGLE message with three parallel Task tool calls (not sequential):

- `thread-writer`
- `blog-writer`
- `newsletter-writer`

Each call's prompt should be exactly this template (with the absolute paths filled in):

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
>
> Read your personality file, read the transcript, write your output file into the output folder per your spec. Report back with the path to the file you wrote.

Running them in parallel is non-negotiable — it's half the point of the system.

## Step 4 — Run QA

Once all three writers have returned, invoke the `qa-reviewer` subagent with this prompt:

> Output folder: `<absolute-path-to-run-folder>`
>
> Read _source.md, thread.md, blog.md, newsletter.md. Read the three personality files under personalities/. Write qa-brief.md with your findings. Report back with the path and total issue count.

## Step 5 — Revision loop (one round, automatic)

After QA returns, read `<folder>/qa-findings.json`.

For each writer key (`thread`, `blog`, `newsletter`) whose `issues` array is non-empty, invoke its writer subagent in revision mode. Dispatch all needed revisions in a SINGLE message with parallel Task tool calls.

Each revision call's prompt:

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-run-folder>`
> Previous draft path: `<absolute-path-to-<writer>.md>`
> Revision notes:
> - <issue 1>
> - <issue 2>
>
> You are in revision mode. Read your personality file, your previous draft, and address each note. Overwrite the same output file. Report back with the path.

After all revisions return, invoke `qa-reviewer` once more on the same folder (it will overwrite `qa-brief.md` and `qa-findings.json`).

**Hard cap: one revision round.** If post-revision QA still flags issues, do not loop again. The user can run `/redo <writer> <folder>` manually for further iteration.

Skip this step entirely if the first QA's findings JSON has zero issues across all three files.

## Step 5b — Update used-hooks memory

After the final QA pass (post-revision if revisions ran), append to `memory/used-hooks.md` at the project root. Create the file if it doesn't exist.

Append a section with this exact format:

```
## <YYYY-MM-DD> — <slug>

- thread opener: <first non-blank line of thread.md>
- blog opener: <first sentence of the opening paragraph of blog.md, after the H1>
- newsletter opener: <first sentence of newsletter.md>
```

Use the same date and slug that named the run folder. Future writer runs will read this file as anti-patterns to keep openers and hooks varied across the catalog.

If any of the four files was a `# Failed` stub, skip its line. Do not crash the run for memory-write issues — if it fails, continue to the report and mention "memory not updated" in the final line.

After appending, trim `memory/used-hooks.md` to the last 20 entries. Count entries by `## ` section headers — if there are more than 20, delete the oldest ones from the top, keeping only the 20 most recent sections. Rewrite the file in place.

## Step 6 — Report back to the user

Print exactly one line. Format:

- Zero issues from first QA: `Done. <folder>/ — clean on first pass.`
- Revisions ran: `Done. <folder>/ — revised <N> pieces; <M> issues remain.`
- No revisions needed: `Done. <folder>/ — clean on first pass.`

Example:

```
Done. content-drops/2026-04-22-1430-ai-adoption-fails/ — revised 2 pieces; 0 issues remain.
```

Do not dump any draft contents into the main session. The user will open the folder.

## If a writer subagent fails

If one of the four writers returns an error or fails to write its file, do NOT halt the whole run. Write a stub file at the expected path containing a single line: `# Failed — <short reason>` and continue to QA. Mention the failure in the final report line.

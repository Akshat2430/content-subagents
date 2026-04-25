---
description: Re-run a single writer subagent against an existing repurpose drop. Useful when one piece came out flat but the rest are fine.
argument-hint: <thread|blog|newsletter|clips> <folder> [optional notes in quotes]
---

You are coordinating a single-piece regeneration. You are NOT writing content yourself.

## Step 1 — Parse arguments

`$ARGUMENTS` will look like one of:
- `thread content-drops/2026-04-24-2233-foo`
- `thread content-drops/2026-04-24-2233-foo "make the hook more specific, drop the stat"`

Extract:
- **writer** — must be one of: `thread`, `blog`, `newsletter`, `clips`. If not, tell the user the valid options and stop.
- **folder** — path to an existing run folder. If it doesn't exist or doesn't contain `_source.md`, tell the user and stop.
- **notes** — optional free-text. If absent, the writer regenerates without specific guidance (essentially a re-roll).

Resolve the folder to an absolute path.

## Step 2 — Verify the previous draft exists

The expected file is `<folder>/<writer>.md`. If it doesn't exist, tell the user and stop — `/redo` revises an existing draft, it doesn't create one from scratch.

## Step 3 — Invoke the writer in revision mode

Map `writer` → subagent name: `thread` → `thread-writer`, `blog` → `blog-writer`, `newsletter` → `newsletter-writer`, `clips` → `clips-writer`.

Invoke that subagent with this prompt template:

> Transcript path: `<absolute-path-to-_source.md>`
> Output folder: `<absolute-path-to-folder>`
> Previous draft path: `<absolute-path-to-<writer>.md>`
> Revision notes:
> <notes from the user, or "Re-roll: produce a different take on the same source. Keep voice and structure rules; vary the angle, hook, and examples." if no notes were given>
>
> You are in revision mode. Read your personality file, read the transcript, read your previous draft, and address the revision notes. Overwrite the same output file. Report back with the path.

## Step 4 — Report back

Print exactly one line:

```
Redone. <folder>/<writer>.md updated.
```

Do not dump the file contents. Do not re-run QA automatically — `/redo` is a manual escape hatch. If the user wants QA, they can run it themselves.

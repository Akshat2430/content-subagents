# Example output

This folder is what a single `/repurpose` run actually produces. It was generated from `samples/example-transcript.md` (a talk on *ship the ugly version first*) and committed verbatim — no cleanup, no cherry-picking. The `qa-brief.md` flags real issues with the drafts, including a fabricated anecdote in the newsletter that the auto-revision round didn't fully resolve. That's the point: the QA pass is the safety net, and you can see it doing its job.

Files:
- `_source.md` — the input transcript the orchestrator copies in
- `thread.md` — X/Twitter thread (6–10 posts)
- `blog.md` — 600–1000 word blog post
- `newsletter.md` — 150–250 word newsletter section
- `clips.md` — three 45–60 second short-form scripts
- `qa-brief.md` — the QA reviewer's pass over all four pieces against the source
- `used-hooks.md` — what the orchestrator appends to `memory/used-hooks.md` after the run, so future runs know which openers and clip hooks have already been used and avoid repeating them

A fresh run lands in `content-drops/<timestamp-slug>/` with the same shape (the memory entry lands in `memory/used-hooks.md` at repo root, not inside the run folder — it's reproduced here for the sample only). Your output will read differently once you replace the `## Personal quirks` section in each `personalities/*.md` file with your own — see the main README for the prompts.

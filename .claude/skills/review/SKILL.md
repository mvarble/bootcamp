---
name: review
description: "Review a solved exercise: tricks, related problems with verified URLs, notes, and pattern pages."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *)
---

## Gate

```!
uv run scripts/meta.py gate review
```

## Task

For the exercise on the `exercise:` line in the gate output above, read my README.md (especially Takeaways), `analysis/hints.md`, and any other `analysis/*.md`. Also read `.meta/prompts.jsonl` (what I asked while solving), mine, my tests, `notes/tricks.md`, and `notes/patterns/README.md`.

1. **`analysis/review.md`** with these sections:
   - **Tricks to remember**: 1-3 transferable insights, phrased so they would trigger recognition on a new problem.
   - **Where I got stuck**: from the hints and prompts, briefly.
   - **Related problems**: 3-5. Each needs a URL you actually retrieved in this session with WebSearch/WebFetch. Anything you did not retrieve gets `[unverified]` (AGENTS.md §4).
2. **`notes/tricks.md`**: append one short entry: `- YYYY-MM-DD: <trick> ([<slug>](../<path>)) · [<pattern>](patterns/<pattern>.md)`.
3. **Pattern page** (`<pattern>` is kebab-case, e.g. `prefix-sums`). If `notes/patterns/<pattern>.md` exists, add this exercise to its list. Otherwise create it with a one-paragraph description, when it applies, and an exercises list, and add a line for it between the markers in `notes/patterns/README.md`.
4. Run `uv run scripts/meta.py tags <pattern> <existing tags…>`, keeping the existing tags and putting the pattern first. Then run `uv run scripts/meta.py set-status reviewed`.

Report the tricks in two lines and suggest `just index`.

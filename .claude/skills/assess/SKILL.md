---
name: assess
description: "For a solved exercise, say whether an asymptotic or constant-factor improvement likely exists. No code."
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(uv run scripts/scaling.py *)
---

## Gate

```!
uv run scripts/meta.py gate assess
```

## Task

For the exercise above, read `README.md`, `provided/`, mine, brute, generate, my tests, and `analysis/hints.md` if present. Then run `uv run scripts/scaling.py <path>/.meta/bench/scaling.jsonl --no-plot`.

Answer two questions: is a better complexity class likely achievable, and is a meaningful constant-factor gain likely? Write `analysis/assessment.md` so it stands alone: a reader who has not seen the problem, the exercise, or this conversation must be able to follow it. Use full paragraphs, not bullet dumps, and describe what the solution does before judging it.

Use exactly these sections, in this order:

1. **Summary.** Open with a sentence of the form "This is an assessment of whether an asymptotic improvement can be made on the solution." Name the exercise and state both verdicts (`likely` / `unlikely` / `unsure`) in a short paragraph, each with its confidence.
2. **My solution.** A paragraph or two describing what the current implementation does, in plain language, and its claimed complexity. Include the per-element work, since the verdicts turn on it. Assume the reader has not read the code.
3. **A better approach.** Include this section **only** when the asymptotic verdict is `likely` and the alternative is faster or uses less memory. Teach the family of technique at a high level: why it works on this problem, what it exploits that the current solution does not, and when it would and would not help. No code, no pseudocode, no step lists, and no identifiers from the code.
4. **Evidence.** How the verdicts were reached: the fitted slope and R² for each implementation, the problem's input bounds, what the solution does per element, and any structural reasoning. Every number you cite must come from the scaling output. Say so when the sweep cannot resolve the effect you are reasoning about.
5. **Questions to think about.** Questions only, no answers.

For the asymptotic question, state the before and after complexity classes and name the family of technique (e.g. "a linear scan with a running state", "sorting plus two pointers"). For the constant-factor question, name the kind of gain (allocation or copying, interpreter overhead, recursion, cache behaviour, I/O, an unnecessary `log n` factor). Give each a verdict and a confidence. No code, no pseudocode, no step lists. Follow the citation rule in AGENTS.md §4. Do not touch `exercise.toml`.

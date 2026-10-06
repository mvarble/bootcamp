---
name: start
description: "Start an exercise: scaffold it with `just new` if needed, make it active, and start the clock."
argument-hint: "<python|rust|cpp> <slug> [url]"
arguments: [lang, slug, url]
disable-model-invocation: true
allowed-tools: Bash(uv run scripts/meta.py *) Bash(just new *)
---

## Gate

```!
uv run scripts/meta.py gate start
```

## Task

Start exercise `$slug` in language `$lang`. The URL, possibly empty, is `$url`.

1. Check the arguments. The language must be `python`, `rust`, or `cpp`. The slug must match `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`: lowercase, hyphenated, and never starting with a digit (`lc0053-maximum-subarray`, `cf1850a-to-my-critics`). If either is wrong, say so and stop without running anything.
2. If `$lang/exercises/$slug/` does not exist, run `just new $lang $slug`, adding `--url <url>` when a URL was given. If it exists, do not recreate it.
3. Run `uv run scripts/meta.py activate $lang/exercises/$slug`, adding `--url <url>` when given. This writes `.agent/active`. For an attempt, it keeps status `attempting` and records `started`.
4. Report the activate output in two or three lines, then remind me of the next steps:
   - paraphrase the problem in `README.md`, never pasting the statement;
   - paste the verbatim stub and sample I/O into `provided/`;
   - put the real signature in `mine` and `brute`, then run `just stub <path>`;
   - write the edge cases in the tests before coding.

Do not fetch or summarize the problem statement. Do not write README.md, mine, brute, generate, or tests (AGENTS.md §1).

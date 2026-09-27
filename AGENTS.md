# Rules for agents working in this repo

This is a practice repo. **I** solve the problems. Agents support the process with hints, assessments, reference solutions, reviews, and bookkeeping, and must never quietly do the solving. Every rule below states the reason it exists.

## 1. Ownership: never write my files

In any exercise directory (`python/exercises/<slug>/`, `rust/exercises/<slug>/`, `cpp/exercises/<slug>/`), agents never create, edit, or overwrite these files:

- `README.md` at the exercise root
- `mine.*`, `brute.*`, `generate.*`, wherever they live in the exercise
- my tests: files under `tests/` whose name contains `cases`, namely `tests/test_cases.py`, `tests/cases/mod.rs`, and `tests/cases.cpp`
- `shim.*`, the Codeforces parse/format shim

The only exception is when I explicitly ask for that specific edit **in the same prompt**.

**Why:** these files *are* the exercise. An agent that "helpfully" fixes `mine`, tightens `generate`, or adds a test case turns a solve into a read. That silently invalidates `minutes`, `solved_cold`, and the revisit schedule.

**Enforcement:** `.pi/extensions/bootcamp/guard.ts` (loaded as a pi project extension) blocks the `write` and `edit` tools on these paths unless `.agent/allow-owned-edits` exists, and blocks bash commands that would create the bypass file. The extension cannot see shell writes (`sed -i`, `>`, `cp`, `git checkout`), so this rule binds regardless of what it catches. Never create `.agent/allow-owned-edits` yourself; only I do that.

**Not owned (wiring):** `tests/conftest.py`, `tests/test_samples.py`, `tests/suite.rs`, `tests/samples.rs`, `tests/samples.cpp`, `impls.hpp`, `src/lib.rs`, `src/__init__.py`, `__main__.py`, `main.*`, `scale.*`, `bench*`, build files, and everything under `templates/`.

## 2. Where agents write

| What | Where |
|---|---|
| Prose (hints, assessments, comparisons, reviews, proposed tests) | `<exercise>/analysis/` |
| Exercise state | `<exercise>/.meta/exercise.toml`, **only** via `uv run scripts/meta.py …` |
| Bench data, attempt archives, prompt logs | `<exercise>/.meta/` |
| Session state and logs outside an exercise | `.agent/` (`active` and `prompts.jsonl` are gitignored) |
| Reference implementation (deep tier, `/reference` only) | `reference.*` |
| Cross-exercise notes (`/review` only) | `notes/tricks.md`, `notes/patterns/*.md` |

**Why:** with a predictable split, I can tell my work from agent work at a glance, and agent text never leaks into files I re-solve from. Routing state through `meta.py` keeps `exercise.toml` valid and the status machine consistent.

## 3. Status gates

`uv run scripts/meta.py gate <skill>` checks the gate for the active exercise (`.agent/active`). If it fails, **stop and change nothing**. Each `/name` below is a pi extension command (`.pi/extensions/bootcamp/`) that runs the gate first; a failed gate stops the command before any task text is injected.

| Skill | Requires | Effect |
|---|---|---|
| `/start` | valid slug | `just new` if missing; writes `.agent/active`; `status = attempting`; `started` |
| `/hint` | `attempting` | next graduated hint appended to `analysis/hints.md`; `hints_used += 1` |
| `/done` | `attempting`, and tests + stress pass | runs scale; records `minutes`, `solved_cold`, revisit schedule; `status = solved` |
| `/assess` | `solved` | `analysis/assessment.md` (no code) |
| `/reference` | `tier = deep`, `solved`, and my tests pass | `reference.*`, `analysis/proposed-tests.md`; `status = referenced` |
| `/compare` | `referenced` | `analysis/figures/`, `analysis/comparison.md` |
| `/review` | `solved` or `referenced` | `analysis/review.md`, `notes/`; `status = reviewed` |
| `/due` | none | read-only summary |

Status machine: `attempting → solved → reviewed`. The deep tier inserts `referenced` after `solved`. `just revisit` sends any status back to `attempting`.

**Why:** each step only makes sense after the previous one. An assessment or reference before I've solved the problem is a spoiler, and a review before a solve has nothing to review.

## 4. Citations and related problems

Any citation, editorial, or "related problem" must include a URL that was actually retrieved in this session (with the web search/fetch tools). Anything else is marked `[unverified]`.

**Why:** problem numbers, titles, and editorial claims are easy to hallucinate. A wrong link is worse than none, because I'd trust it.

## 5. Other conventions

- **Never paste problem statements verbatim.** READMEs paraphrase. `provided/` holds only the verbatim function stub and sample I/O.
  - **Why:** copyright, and paraphrasing is itself a comprehension check.
- **Numbers in analysis prose must come from `.meta/bench/` data** or tables generated from it, never from estimates.
  - **Why:** the benchmarking practice is worthless if the write-up invents numbers.
- **A claimed speedup must exceed run-to-run variance**, measured as criterion CIs, pytest-benchmark stddev, or Google Benchmark `_stddev`/`_cv` aggregates.

## Repo map

- `python/`: a uv workspace (`algolib`, `harness`, `exercises/*`).
- `rust/`: a cargo workspace, edition 2024 (`algolib`, `harness`, `exercises/*`).
- `cpp/`: CMake + CTest + presets `debug|asan|release` (`algolib`, `harness`, `exercises/*`).
- `templates/<lang>/{quick,deep}/`: exercise templates. See `templates/README.md`.
- `.pi/extensions/bootcamp/`: the pi project extension. `guard.ts` protects my files,
  `prompts.ts` logs prompts, `instructions.ts` holds the command task text, and `index.ts`
  wires the `tool_call`/`input` handlers and the `/start` … `/due` commands. Tests under
  `tests/` run with `node --test`.
- `scripts/`: `uv run` scripts:
  - `meta.py`: state and gates;
  - `exercise.py`: new, deepen, revisit, stub;
  - `scaling.py`, `bench_report.py`, `index.py`, `due.py`.
- `just --list` shows every recipe.

/**
 * Task instructions for the workflow commands, adapted from the original
 * Claude-Code skills. The gate output is injected by the command handler, so
 * these texts cover only the work after a passing gate.
 */

function lines(...rows: string[]): string {
  return rows.join("\n");
}

function startTask(args: string): string {
  const [lang = "", slug = "", url = ""] = args.trim().split(/\s+/);
  return lines(
    `Start exercise \`${slug}\` in language \`${lang}\`. The URL, possibly empty, is \`${url}\`.`,
    "",
    "1. Check the arguments. The language must be `python`, `rust`, or `cpp`. The slug must match "
      + "`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`: lowercase, hyphenated, and never starting with a digit "
      + "(`lc0053-maximum-subarray`, `cf1850a-to-my-critics`). If either is wrong, say so and stop "
      + "without running anything.",
    `2. If \`${lang}/exercises/${slug}/\` does not exist, run \`just new ${lang} ${slug}\`, adding `
      + "`--url <url>` when a URL was given. If it exists, do not recreate it.",
    `3. Run \`uv run scripts/meta.py activate ${lang}/exercises/${slug}\`, adding \`--url <url>\` `
      + "when given. This writes `.agent/active`. For an attempt, it keeps status `attempting` and "
      + "records `started`.",
    "4. Report the activate output in two or three lines, then remind me of the next steps:",
    "   - paraphrase the problem in `README.md`, never pasting the statement;",
    "   - paste the verbatim stub and sample I/O into `provided/`;",
    "   - put the real signature in `mine` and `brute`, then run `just stub <path>`;",
    "   - write the edge cases in the tests before coding.",
    "",
    "Do not fetch or summarize the problem statement. Do not write README.md, mine, brute, generate, or "
      + "tests (AGENTS.md §1).",
  );
}

function hintTask(): string {
  return lines(
    "Give exactly one hint, at the level named on the `next hint:` line in the gate output above.",
    "",
    "- **Level 1 (nudge).** A question or observation that points at the property of the problem "
      + "that matters. Name no technique and no data structure.",
    "- **Level 2 (technique).** Name the technique or pattern (e.g. \"prefix sums\", \"monotonic "
      + "stack\", \"two pointers on a sorted array\") and say in one or two sentences why it fits "
      + "*this* problem. Give no steps.",
    "- **Level 3 (structural outline).** The shape of the algorithm as 3-6 plain-language steps, "
      + "plus the invariant that makes it correct. Still no code, no pseudocode, and none of their "
      + "identifiers. If `analysis/hints.md` already has a level-3 hint, do not repeat it. Refine the "
      + "step their current `mine` shows they are stuck on.",
    "",
    "Use their `mine`, `brute`, and tests to aim at their actual gap. Never mention reference "
      + "implementations, editorials, or the optimal complexity at level 1.",
    "",
    "Record the hint with exactly one Bash call of this shape. The heredoc delimiter must be `EOF` on "
      + "the first line and alone on the last line. Do not chain any other command; a guard blocks "
      + "everything else, including reads, so this is the only tool call you may make:",
    "",
    "    uv run scripts/meta.py record-hint --level N <<'EOF'",
    "    HINT TEXT",
    "    EOF",
    "",
    "Then reply with the hint text and one line: `Recorded as hint <number> in analysis/hints.md.`",
  );
}

function doneTask(args: string): string {
  const minutes = args.trim();
  const minutesLine = minutes
    ? `4. Run \`uv run scripts/meta.py done --minutes ${minutes}\`.`
    : "4. Run `uv run scripts/meta.py done`. Minutes default to the wall time since `started`.";
  return lines(
    "The exercise path is on the `exercise:` line in the gate output above. Run these in order. **At "
      + "the first failure, stop, report what failed, and change nothing.** Do not edit code or tests "
      + "to make them pass; they are mine.",
    "",
    "1. `just check <path>`: examples, edge cases, and light stress.",
    "2. `just stress <path>`: heavy stress against brute.",
    "3. `just scale <path>`: size sweep plus log-log fit. Keep the slope table for the report.",
    minutesLine,
    "",
    "Report in a few lines:",
    "- minutes;",
    "- `solved_cold`, which is true only with 0 hints;",
    "- `revisit_on` and the interval: 14 days after a first solve, doubled after a cold re-solve, "
      + "back to 14 otherwise;",
    "- the slope table, with one sentence on whether `mine`'s slope matches the complexity claimed in "
      + "README.md.",
    "",
    "Suggest `/assess` next and `just index`.",
  );
}

function assessTask(): string {
  return lines(
    "For the exercise above, read `README.md`, `provided/`, mine, brute, generate, my tests, and "
      + "`analysis/hints.md` if present. Then run "
      + "`uv run scripts/scaling.py <path>/.meta/bench/scaling.jsonl --no-plot`.",
    "",
    "Answer two questions: is a better complexity class likely achievable, and is a meaningful "
      + "constant-factor gain likely? Write `analysis/assessment.md` so it stands alone: a reader who "
      + "has not seen the problem, the exercise, or this conversation must be able to follow it. Use "
      + "full paragraphs, not bullet dumps, and describe what the solution does before judging it.",
    "",
    "Use exactly these sections, in this order:",
    "",
    "1. **Summary.** Open with a sentence of the form \"This is an assessment of whether an "
      + "asymptotic improvement can be made on the solution.\" Name the exercise and state both "
      + "verdicts (`likely` / `unlikely` / `unsure`) in a short paragraph, each with its confidence.",
    "2. **My solution.** A paragraph or two describing what the current implementation does, in "
      + "plain language, and its claimed complexity. Include the per-element work, since the verdicts "
      + "turn on it. Assume the reader has not read the code.",
    "3. **A better approach.** Include this section **only** when the asymptotic verdict is `likely` "
      + "and the alternative is faster or uses less memory. Teach the family of technique at a high "
      + "level: why it works on this problem, what it exploits that the current solution does not, and "
      + "when it would and would not help. No code, no pseudocode, no step lists, and no identifiers "
      + "from the code.",
    "4. **Evidence.** How the verdicts were reached: the fitted slope and R² for each implementation, "
      + "the problem's input bounds, what the solution does per element, and any structural reasoning. "
      + "Every number you cite must come from the scaling output. Say so when the sweep cannot resolve "
      + "the effect you are reasoning about.",
    "5. **Questions to think about.** Questions only, no answers.",
    "",
    "For the asymptotic question, state the before and after complexity classes and name the family "
      + "of technique (e.g. \"a linear scan with a running state\", \"sorting plus two pointers\"). "
      + "For the constant-factor question, name the kind of gain (allocation or copying, interpreter "
      + "overhead, recursion, cache behaviour, I/O, an unnecessary `log n` factor). Give each a verdict "
      + "and a confidence. No code, no pseudocode, no step lists. Follow the citation rule in AGENTS.md "
      + "§4. Do not touch `exercise.toml`.",
  );
}

function referenceTask(): string {
  return lines(
    "1. Run `just check <path>`. **My tests must pass before you write anything.** If they fail, stop "
      + "and report.",
    "2. Read README.md, mine, brute, generate, my tests, and `analysis/` (especially `assessment.md`).",
    "3. Write the reference implementation in the exercise's existing `reference.*`, with the same "
      + "interface as mine:",
    "   - Python: `src/<pkg>/reference.py`;",
    "   - Rust: `src/reference.rs`;",
    "   - C++: `reference.hpp`, `namespace reference { struct Solution … }`, keeping it a distinct type.",
    "",
    "   It may be asymptotically better, or the same idea with a better constant factor. If you "
      + "conclude there is **no meaningful improvement**, leave `reference.*` re-exporting mine and say "
      + "so. That is a valid outcome.",
    "4. Never edit README.md, mine, brute, generate, or my tests. If you think a case is missing, add it to "
      + "`analysis/proposed-tests.md` as input, expected output, and why it matters.",
    "5. Run `just check <path>` and `just stress <path>`. The suite is instantiated for mine and "
      + "reference, so both must pass.",
    "6. Run `just scale <path>`, `just bench <path>`, then "
      + "`uv run scripts/bench_report.py <path>`.",
    "7. **Speedup claims.** Claim a speedup only where `analysis/bench-tables.md` marks the pair "
      + "*claimable*: 95% CIs separated **and** the difference beyond the larger per-call standard "
      + "deviation. Otherwise write \"no measurable difference\". Quote the numbers from that file.",
    "8. Run `uv run scripts/meta.py set-status referenced`.",
    "",
    "Report: what reference does differently, the slope comparison, and the claimable / not-claimable "
      + "verdicts.",
  );
}

function compareTask(): string {
  return lines(
    "1. Run `uv run scripts/bench_report.py <path>`. It regenerates `analysis/bench-tables.md` and "
      + "`analysis/figures/*.png` from `.meta/bench/`.",
    "2. Read `analysis/bench-tables.md`, mine, reference, `analysis/assessment.md`, and README.md.",
    "3. Write `analysis/comparison.md` in **full prose**: paragraphs, not bullet dumps. Cover:",
    "   - what the implementations do differently and why that should matter;",
    "   - empirical scaling: the fitted slopes and whether they match the claimed complexity;",
    "   - constant factors: means, confidence intervals, and ratios, and which differences are "
      + "*claimable* (separated and beyond sd), noting any that are separated but not claimable;",
    "   - whether any difference matters at the problem's real input sizes;",
    "   - what I should take away.",
    "",
    "   Embed the figures with `![…](figures/scaling.png)` and "
      + "`![…](figures/constant-factor.png)` where present.",
    "4. **Every number in the text must appear in `analysis/bench-tables.md`,** copied as written. Do "
      + "not round differently, derive new numbers, or estimate. If a number you want is not there, say "
      + "the data does not show it.",
    "",
    "Do not change `exercise.toml` or any file outside `analysis/`.",
  );
}

function reviewTask(): string {
  return lines(
    "Read my README.md (especially Takeaways), `analysis/hints.md`, and any other `analysis/*.md`. "
      + "Also read `.meta/prompts.jsonl` (what I asked while solving), mine, my tests, "
      + "`notes/tricks.md`, and `notes/patterns/README.md`.",
    "",
    "1. **`analysis/review.md`** with these sections:",
    "   - **Tricks to remember**: 1-3 transferable insights, phrased so they would trigger recognition "
      + "on a new problem.",
    "   - **Where I got stuck**: from the hints and prompts, briefly.",
    "   - **Related problems**: 3-5. Each needs a URL you actually retrieved in this session with "
      + "WebSearch/WebFetch. Anything you did not retrieve gets `[unverified]` (AGENTS.md §4).",
    "2. **`notes/tricks.md`**: append one short entry: "
      + "`- YYYY-MM-DD: <trick> ([<slug>](../<path>)) · [<pattern>](patterns/<pattern>.md)`.",
    "3. **Pattern page** (`<pattern>` is kebab-case, e.g. `prefix-sums`). If "
      + "`notes/patterns/<pattern>.md` exists, add this exercise to its list. Otherwise create it with "
      + "a one-paragraph description, when it applies, and an exercises list, and add a line for it "
      + "between the markers in `notes/patterns/README.md`.",
    "4. Run `uv run scripts/meta.py tags <pattern> <existing tags…>`, keeping the existing tags and "
      + "putting the pattern first. Then run `uv run scripts/meta.py set-status reviewed`.",
    "",
    "Report the tricks in two lines and suggest `just index`.",
  );
}

function dueTask(): string {
  return lines(
    "Summarize the due list above in a few lines:",
    "- what is overdue (most overdue first);",
    "- what is due today;",
    "- what comes up this week.",
    "",
    "Recommend one to start with, preferring the most overdue, and among equals the one whose "
      + "interval is shortest (least consolidated). To start a re-solve: `just revisit <path>` then "
      + "`/start <lang> <slug>`. Change nothing.",
  );
}

export const COMMAND_DESCRIPTIONS: Record<string, string> = {
  start: "Start an exercise: scaffold it with `just new` if needed, make it active, and start the clock.",
  hint: "Next graduated hint for the active exercise (nudge, then technique, then structural outline). Never code.",
  done: "Finish the active attempt: tests, stress, and scale, then record minutes and the revisit date.",
  assess: "For a solved exercise, say whether an asymptotic or constant-factor improvement likely exists. No code.",
  reference: "Deep tier: write reference.*, run the same tests and benchmarks over mine and reference, report measurable differences.",
  compare: "For a referenced exercise, generate figures and tables from .meta/bench/ and write analysis/comparison.md.",
  review: "Review a solved exercise: tricks, related problems with verified URLs, notes, and pattern pages.",
  due: "List exercises due for a spaced cold re-solve and suggest what to do first.",
};

export function renderTask(skill: string, args: string): string {
  switch (skill) {
    case "start":
      return startTask(args);
    case "hint":
      return hintTask();
    case "done":
      return doneTask(args);
    case "assess":
      return assessTask();
    case "reference":
      return referenceTask();
    case "compare":
      return compareTask();
    case "review":
      return reviewTask();
    case "due":
      return dueTask();
    default:
      return "";
  }
}

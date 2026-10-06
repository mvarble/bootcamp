# What this repo is for, and how to use it

## The short version

This repository is a place to practice algorithm problems one at a time, in an organized way, so that the practice actually sticks. You pick a problem, solve it in one language, prove to yourself that your solution is correct and as fast as you think it is, and then come back to it a couple of weeks later to solve it again from scratch. Everything else in here exists to make those few steps quick and to keep a record of how you did.

If you only remember one thing from this document, remember this loop:

```sh
just new python lc0053-maximum-subarray    # make a folder for the problem
# ...write your notes, your tests, and your solution...
just check python/exercises/lc0053-maximum-subarray    # does it work?
just stress python/exercises/lc0053-maximum-subarray   # does it *really* work?
just scale python/exercises/lc0053-maximum-subarray    # is it as fast as I claim?
```

That is the whole daily workflow. The rest of this document explains why each of those steps is there, what the files in a problem folder are for, and which parts of the repo you can safely ignore.

## Why not just solve problems on LeetCode's website?

You can, and it is fine for a single problem. The trouble is what happens over weeks. You solve something, feel good, and a month later you cannot remember the trick, you do not know whether you solved it on your own or after peeking at the discussion tab, and you have no idea which problems you are weak at. The website also tells you "accepted" without teaching you to check your own work, which is the skill that matters in an interview or a contest where nobody hands you a hidden test suite.

So this repo tries to give you three habits that the website does not.

The first habit is **checking your own work**. Before you write the real solution, you write down the tricky inputs you can think of (an empty list, all negative numbers, one element) together with the answers you expect. Then you write a second, deliberately dumb solution, which the repo calls the _brute force_. It is slow but so simple that you trust it. Finally you write a small function that invents random inputs. The stress test throws thousands of those random inputs at both of your solutions and complains the moment they disagree. When that happens it shows you the smallest input it could find that breaks things. This catches the bugs your hand-picked examples missed, and it is the single most useful testing trick for this kind of problem.

The second habit is **checking your speed claims**. It is easy to write "this is O(n)" in your notes and be wrong. The `scale` step runs your solution on inputs of growing size, times it, and fits a line through the timings on a log-log plot. The slope of that line is the exponent: a slope near 1 means your code really is linear, near 2 means quadratic. It is a quick, honest check that your analysis matches reality, and it prints a single number you can glance at.

The third habit is **spaced repetition**. When you mark a problem as solved, the repo schedules it to come back in 14 days. If you then re-solve it cold, with no hints, the gap doubles to 28 days, then 56, and so on. If you needed help, it resets to 14. The idea is the same as flashcards: you revisit things just as you are about to forget them, and the ones you have truly learned drift away on their own. `just due` tells you what has come back around.

## What is in a problem folder

When you run `just new python lc0053-maximum-subarray`, you get a folder at `python/exercises/lc0053-maximum-subarray/`. The name is the source (`lc` for LeetCode, `cf` for Codeforces), the problem number, and a short name. It never starts with a digit, because some languages cannot use such a name as a module name.

Inside it, a handful of files are _yours_, meaning that you write them and nobody else touches them.

`README.md` is your notebook for the problem. You restate the problem in your own words (never paste the original; rewording it is itself a check that you understood it), then jot down your approach, its complexity, the edge cases you thought of, and what you want to remember afterwards. Keep it short.

`mine` is your solution. `brute` is the slow, obviously-correct solution described above.

`generate` holds two tiny things: the function that makes random inputs, and a one-line adapter that says how to call a solution. The adapter exists because LeetCode dictates odd method names like `maxSubArray` or `max_sub_array`. Everything else in the folder (the tests, the stress test, the timing) calls your code only through that one line, so none of it has to be edited per problem.

The test file (`tests/test_cases.py` in Python) holds your examples and edge cases, and it already contains the stress test wired up for you.

`provided/` is where you paste the exact function signature and the sample inputs and outputs from the problem page, for reference.

Everything else in the folder is plumbing that the templates generate and that you should not need to open: build files, the scale entry point, and a `.meta/` directory where the repo keeps its bookkeeping. That bookkeeping records the problem's status, how many minutes it took, how many hints you used, when it is next due, and the timing data from `scale`.

The folder already contains a stub `mine` that fails on purpose, so the tests are red until you solve the problem. That is intended. You watch them go green.

One small chore: once you have pasted the real signature into `mine` (and before you solve it), run `just stub <path>`. That saves the empty version so that, weeks later, `just revisit` can put you back at a blank solution with the right signature.

## The deep tier, which is optional

Most problems end at the loop above. Occasionally you will solve something and wonder whether it could be faster, and whether it would matter. For those, `just deepen <path>` adds a second implementation slot called `reference`, where you or an assistant can write a better version. It also adds proper micro-benchmarks. Your same tests then run against both implementations automatically, and `just bench <path>` measures them side by side. The comparison only counts a speedup as real if it is larger than the ordinary noise between runs. That rule matters: when I tested it with two identical copies of the same code, a naive comparison claimed one was faster. You do not need any of this to practice; it is there for when curiosity strikes.

## Why three languages?

For practice! Each language has its own corner of the repo (`python/`, `rust/`, `cpp/`) with the same folder layout and the same `just` commands. **You do not solve a problem in all three.** Each problem lives in exactly one language, the one you chose when you ran `just new`. The three corners look alike only so that, on the rare day you try a problem in Rust, nothing about the routine changes.

Each language also has a small shared library, `algolib`, for data structures you will reuse across problems, such as the union-find structure that is in there now. LeetCode-style solutions should stay self-contained, because you would have to paste them into a website anyway. The library is there for Codeforces-style problems and for building up a toolkit you understand.

Each language also has a `harness` folder, which is just the timing code that `scale` uses. You can ignore it.

If you end up practicing only in Python, you can ignore the `rust/` and `cpp/` folders entirely. They do no harm sitting there.

## The assistant commands, and the rules they follow

Part of the original goal was to learn to use a coding agent as a tool rather than as a crutch. So the repo defines a few slash commands for the agent, and a set of rules (in `AGENTS.md`) that keep it from doing your work for you.

The most important rule is that the agent never edits your files (`README.md`, `mine`, `brute`, `generate`, and your tests) unless you ask it to in that very message. That is enforced by a guard that blocks the edit, not just by politeness. If you ever do want it to edit them, you create a file called `.agent/allow-owned-edits` yourself, and delete it afterwards. The reason is simple: if an assistant quietly fixes your solution, you did not solve the problem, and your records say you did.

The commands follow the life of a problem. `/start` sets up a problem and starts the clock. `/hint` gives you one hint, gently at first (a nudge), then naming the technique, then sketching the outline, and never writing code; each hint is counted. `/done` runs your tests, the stress test, and the timing, and if everything passes it records how long you took, whether you solved it without hints, and when it is due again. After that, `/assess` tells you whether a faster approach probably exists, without telling you what it is. `/review` writes up the tricks worth remembering and links related problems, adding them to your running notes in `notes/`. `/due` tells you what has come back around. The commands for the deep tier, `/reference` and `/compare`, are there when you want them. Each command checks that the problem is at the right stage first. `/assess` refuses to run on a problem you have not solved, for example, because that would be a spoiler.

You never _need_ these. Every step they take can be done by hand with the `just` commands. They are a convenience and a way to practice working with an agent. Note that at the time of writing none of them has been tried in a real session yet. `/due` is a harmless one to try first.

A log of what you type to the agent is kept alongside each problem, so that `/review` can see where you got stuck.

## What a normal session looks like

Say you sit down to practice. You run `just due` to see whether anything is waiting for a re-solve; if so, you do that first with `just revisit <path>`, which archives your old solution and hands you a blank one. Otherwise you pick a new problem and run `just new python <slug>` (or `/start`).

You open the folder's `README.md` and write, in a few sentences, what the problem is asking. You paste the signature and samples into `provided/` and the signature into `mine` and `brute`, then run `just stub <path>`. You add the sample cases and a few edge cases of your own to the test file. You write `brute` first, because it is quick and it gives the stress test something to compare against, then you write `mine`.

You run `just check <path>` until it is green, then `just stress <path>` to throw thousands of random cases at it. When that passes, `just scale <path>` confirms the speed you claimed in your notes. You finish by writing a line or two under "Takeaways" and marking it done, either with `/done` or by running `just done <path>` (a thin wrapper over `scripts/meta.py done`, which is the only thing that touches the state file).

That is it. Fifteen minutes of setup-free practice with a record you can trust.

## What you can ignore

Almost everything outside the exercise folders is machinery you will rarely touch.

`templates/` is what `just new` copies from. `scripts/` holds the small programs behind the `just` commands. `.github/` runs the tests on GitHub when you push. `.claude/` is the agent integration. `algolib` and `harness` sit in each language folder. The `example-max-subarray` folders are worked examples (maximum subarray sum, solved in all three languages) that show what a finished problem looks like; they are left out of the index and the due list.

When you want to see everything at once, `just index` rebuilds the table in the main `README.md`, and `just --list` shows every command with a one-line description.

## Where to start right now

Open `python/exercises/example-max-subarray/` and read it top to bottom: the README, then `mine.py`, `brute.py`, `generate.py`, and `tests/test_cases.py`. It is a complete, small example of exactly what you will be writing. Then pick a problem you like and run `just new python <slug>`.

# The `just` commands

Every command in this repo is a recipe in the `justfile` at the top of the repository. You run them from anywhere inside the repo, and `just --list` prints them all with a one-line reminder. Most of them take the path of a problem folder, such as `python/exercises/lc0053-maximum-subarray`. You can give that path relative to wherever you are standing; the commands work out the rest. They look at the first part of the path to decide which language they are dealing with, and at the problem's `.meta/exercise.toml` to learn its state.

The commands fall into four groups. Some create and reset problems, some run tests, some measure speed, and two report on your progress. They are described below roughly in the order you would meet them.

## Creating and resetting problems

### `just new <lang> <slug>`

This creates a new problem folder by copying the templates for that language into `<lang>/exercises/<slug>/`. For example, `just new python lc0053-maximum-subarray` makes a Python folder for LeetCode problem 53. It refuses slugs that start with a digit or contain capitals or underscores, and it refuses to overwrite a folder that already exists.

The command reads the start of the slug to decide what kind of problem this is. A slug beginning with `cf` followed by a digit is treated as a Codeforces problem, and anything else as a LeetCode-style one; you can override the guess with `--source lc` or `--source cf`. The difference matters because the two kinds are shaped differently. A LeetCode problem is a class with a method you fill in. A Codeforces problem reads text from standard input and prints an answer. So a Codeforces folder also gets a small "shim" file where you turn the input text into data and your answer back into text, plus a test that feeds every sample file in `provided/samples/` through your program and compares the output. You can also pass `--url` with the problem's address, which is then recorded and linked from the README.

Behind the scenes, `new` also writes the bookkeeping file `.meta/exercise.toml` (status "attempting", the start time, zero hints, and so on) and saves a copy of the blank `mine` file, which `revisit` uses later.

### `just stub <path>`

After you paste the real signature into `mine` but before you solve anything, run this once. It saves your blank-but-correctly-named `mine` as the version that `revisit` will reset to. It refuses to run if `mine` no longer looks blank. It checks for the "not implemented" marker the template puts in, which is `NotImplementedError` in Python, `todo!()` in Rust, and a thrown "not implemented" error in C++. That way you can't accidentally save your finished solution as the blank one.

### `just revisit <path>`

This starts a cold re-solve of a problem you have already solved. It copies your current solution into `.meta/attempts/` under today's date, so nothing is lost. It then replaces `mine` with the saved blank version, sets the problem back to "attempting", resets the hint count, and restarts the clock. It refuses if the problem is already in progress. When you finish again, the scheduler looks at whether you used hints and decides whether to double the gap before the next revisit or reset it to 14 days.

### `just deepen <path>`

This moves a problem into the optional deep tier. It adds a `reference` implementation, which at first is simply your `mine` under another name, and a benchmark file, and it switches the problem's tier to "deep". After that, every test in the folder runs twice, once for `mine` and once for `reference`. Nothing of yours is edited; the command only touches the wiring files.

How it does that differs by language. In Python it only has to add the new files, because the tests already ask Python which implementations exist and run once for each one they find. In Rust, the tests are written inside a macro that stamps out one copy per implementation, so `deepen` adds one line that stamps out a copy for `reference`. It also registers the new module and adds the benchmarking library to the problem's `Cargo.toml`. In C++, the tests are "typed tests", which run once for each type in a list, so `deepen` adds `reference::Solution` to that list and turns on the benchmark target in the problem's `CMakeLists.txt`.

## Running tests

### `just check <path>`

This runs all the tests for one problem: your examples, your edge cases, a light stress test, and, for Codeforces problems, the sample files. If the problem has been deepened, it runs them for both implementations. This is the command you run over and over while solving. In Python it runs pytest on the problem's `tests` folder, in Rust it runs `cargo test` for that one crate, and in C++ it builds just that problem's test program and runs the tests whose names start with the slug.

### `just stress <path>`

This is the heavy version of the random testing. The stress test asks your generator for a random input of some size `n` from some seed, runs both `mine` and `brute` on it, and fails if they disagree. `check` does this a modest number of times; `stress` does it thousands of times. The size of each input is kept small (under 64) on purpose, because small failing inputs are the ones you can actually reason about.

Each language does this with its own testing tools. Python uses the Hypothesis library with a "stress" profile of 3,000 examples. When it finds a failure, it shrinks the size and seed to the smallest example that still fails. Rust uses the proptest library, which shrinks failures in the same way; `stress` raises its case count to 5,000 and builds in release mode so it runs quickly. C++ has no shrinking library in use here, so it runs a plain loop of 5,000 seeds with the size growing slowly from 0 to 63. That way the first failure it reports is already a small one. In Rust and C++ you can change the count by setting `PROPTEST_CASES` or `STRESS_ITERS` in front of the command.

### `just test <lang>`

This runs every test in one language's corner of the repo: the shared library, the timing harness, and every problem. For C++ you can add a second word to pick the build flavour, as in `just test cpp asan`. The `asan` flavour builds with the address and undefined-behaviour sanitizers, which catch memory errors that a normal build would silently survive; `debug` is the default.

On GitHub the tests run with the setting `SKIP_ATTEMPTING=1`, which leaves out any problem still marked "attempting". Its tests are meant to fail until you solve it, and you don't want a red build every time you push half-finished work. Each language skips those problems differently. Python tells pytest not to collect those folders, Rust passes `--exclude` for each such crate to cargo, and C++ simply doesn't add those folders to the build. Locally the setting is off, so you see everything.

### `just test-all`

This runs `just test` for all three languages, followed by `test-tooling`.

### `just test-tooling`

This tests the repo's own machinery rather than your problems. That means the Python scripts behind these commands (the scheduling rules, the templates, the index and the due list) and the pi extension that guards your files and provides the slash commands. You would only run it after changing that machinery.

## Measuring speed

### `just scale <path>`

This checks whether your solution grows as fast as you think it does. It builds or loads your problem and times every implementation (`mine`, `brute`, and `reference` if present) on inputs of doubling size. It runs the smallest sizes many times over so the timings aren't just clock noise, and it stops growing an implementation once a single run takes more than half a second. That way the slow `brute` drops out early while `mine` keeps going to large sizes. Every measurement is appended to `.meta/bench/scaling.jsonl`. A script then fits a straight line through the most recent run on a log-log scale, prints the slope for each implementation, and saves a plot as `scaling.png` next to the data. A slope near 1 means linear time, a little above 1 often means n log n, and near 2 means quadratic.

The timing itself happens in each language's own `harness` folder, so that it measures the language's real speed. Python times the calls directly. Rust and C++ first have to stop the compiler from being clever. An optimizing compiler will happily skip a calculation whose result is never used, or do it once instead of a thousand times, which would make everything look instantaneous. So both pass the input and the result through a small "black box" that the compiler cannot see into. Rust and C++ also use a release (optimized) build for this, since timing a debug build tells you little. The input is always generated before the clock starts, so only your solution is being timed.

### `just bench <path>`

This only works on deep-tier problems. Where `scale` asks how the running time *grows*, `bench` asks how two implementations compare at a fixed size, which is the question to ask when you think `reference` is a constant-factor improvement over `mine`. It runs each implementation at two sizes (1,000 and 100,000) many times and saves the raw results in `.meta/bench/`.

Each language uses the standard benchmarking tool for that language. Python uses pytest-benchmark, Rust uses Criterion, and C++ uses Google Benchmark with ten repetitions. All three record not just an average but how much the timings vary from run to run. That matters because of the rule this repo applies when comparing: a speedup only counts if the difference between the two averages is larger than the ordinary jitter of a single run. The comparison report that turns these files into tables and figures is `scripts/bench_report.py`, which the `/compare` command runs for you.

## Keeping track

### `just due`

This lists the problems whose revisit date has arrived or passed, showing how overdue each one is, followed by the ones coming up in the next week. It reads every problem's `.meta/exercise.toml` and skips the `example-*` folders. When something is due, `just revisit <path>` is how you start it.

### `just index`

This rebuilds the table of problems in the main `README.md`, with one row per problem. Each row shows the pattern (the problem's first tag), language, source, tier, status, minutes, hints, whether you solved it cold, and when it is next due. Rows are grouped by pattern, so similar problems sit together. It only replaces the part of the README between the two `index` marker comments and leaves the rest of the file alone. The `example-*` folders are left out.

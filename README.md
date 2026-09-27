# bootcamp

LeetCode / Codeforces practice, grouped by pattern, with spaced re-solves. Python is the primary language, with Rust and C++ alongside.

Each exercise includes:
- edge cases chosen before coding;
- a stress test against my own brute-force oracle;
- an empirical complexity check (size sweep + log-log slope).

An opt-in **deep** tier adds a reference implementation and constant-factor benchmarks.

## Workflow

```sh
just new python lc0053-maximum-subarray      # or /start python lc0053-maximum-subarray <url>
just stub python/exercises/lc0053-maximum-subarray    # after pasting the real signature into mine
just test python                              # examples + edge cases + light stress
just stress python/exercises/lc0053-maximum-subarray  # heavy stress vs brute
just scale  python/exercises/lc0053-maximum-subarray  # size sweep + slope fit
just deepen python/exercises/lc0053-maximum-subarray  # opt-in deep tier
just revisit python/exercises/lc0053-maximum-subarray # archive mine, reset to stub
just due                                       # what's due for a cold re-solve
just index                                     # rebuild the table below
```

Agent skills: `/start`, `/hint`, `/done`, `/assess`, `/reference`, `/compare`, `/review`, `/due`. See [AGENTS.md](AGENTS.md) for the rules agents follow.

## Exercises

<!-- index:start -->
_No exercises yet._
<!-- index:end -->

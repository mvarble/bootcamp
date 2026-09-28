# Review: lc0347-top-k-frequent-elements

## Tricks to remember

- **Count first, then select.** Every "the k most frequent / least frequent / highest-priority"
  problem splits into one forced linear pass that builds a value→count map, and a second phase that
  selects from the distinct keys. The counting pass is the same every time; the real decision, and the
  only place a better complexity class can live, is how the second phase selects. Recognizing the
  split tells you where to spend your design effort.

- **A rank key bounded by the input size means you can bucket instead of compare.** When the quantity
  you rank by is an integer whose range is capped by `n` — frequencies always run from 1 to `n` — you
  can use that integer as an array position and read the top of the distribution off in order, turning
  comparison-based selection (`O(n log n)` or `O(n log k)`) into `O(n)`. The trigger to watch for is
  "the key is a count bounded by the input length," not the specific problem.

- **Top-k selection has three interchangeable families, and they trade worst cases.** A size-`k`
  heap, a quickselect partition, and a bounded-key bucket all solve the same selection; the heap gives
  `O(n log k)` deterministically, quickselect averages `O(n)` with a quadratic worst case, and the
  bucket is `O(n)` when the key range is bounded. Naming all three is what lets you choose rather than
  reach for the first one you remember.

## Where I got stuck

Nothing algorithmic is on record. The exercise was solved cold with zero hints in ten minutes, and
`.meta/prompts.jsonl` contains exactly one prompt from the attempt — a process question about why the
verbatim stub has to be pasted into `provided/` when a `stub.py` already exists. That confusion was
about the exercise scaffolding, not the problem, so there is no solving gap to report here.

## Related problems

Each URL below was retrieved in this session; anything not retrieved would be marked `[unverified]`
per AGENTS.md §4.

- [451. Sort Characters By Frequency](https://walkccc.me/LeetCode/problems/0451/) — the same
  bucket-by-frequency idea applied to characters, except it needs the full frequency-ordered output
  rather than only the top `k`.
- [692. Top K Frequent Words](https://walkccc.me/LeetCode/problems/0692/) — this problem's shape plus a
  lexicographic tie-break; the bucket approach still works, but each frequency bucket must be ordered
  internally to satisfy the tie-break.
- [215. Kth Largest Element in an Array](https://walkccc.me/LeetCode/problems/0215/) — selection
  without a full sort, and the clearest place to compare the heap and quickselect families directly.
- [1636. Sort Array by Increasing Frequency](https://walkccc.me/LeetCode/problems/1636/) — frequency
  as an ordering key with a value tie-break, the comparison-sort baseline against which the bucket
  version should be judged.

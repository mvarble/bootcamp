# Assessment: lc0347-top-k-frequent-elements

## Summary

This is an assessment of whether an asymptotic improvement can be made on the solution to the
problem in `python/exercises/lc0347-top-k-frequent-elements`. The asymptotic verdict is **likely**:
the current solution costs `O(n)` to count frequencies plus a selection over the distinct values that
can reach `O(m log k)` and therefore `O(n log n)` in the worst case, while a genuinely `O(n)` approach
exists. Confidence in that class comparison is high. The constant-factor verdict is also **likely**:
the per-element frequency pass performs more hash work than it needs to, and a lower-overhead counting
routine should improve on it. Confidence there is medium, because the scaling data cannot quantify the
size of the win.

## My solution

The solution first walks the input and builds a dictionary mapping each distinct value to the number
of times it occurs. On every input element it performs a membership test and then a second dictionary
access to update the count, so each element costs two hash operations, plus a store on the
repeated-value path. Once the frequencies are known, it runs a keyed top-k selection over the distinct
values, comparing them by frequency, and returns the `k` values with the largest counts. Its README
claims `O(n log n)`. The sharper statement is `O(n + m log k)`, where `m` is the number of distinct
values, which matches the claimed bound in the worst case when `k` is comparable to `m`.

## A better approach

The improvement family is counting by frequency — bucketing the distinct values by how often they
occur. The observation it exploits is that a frequency is an integer between 1 and `n`, so frequencies
can serve as positions rather than as comparison keys. Assigning every distinct value a position
determined by its count, and then sweeping those positions from the highest frequency downward,
surfaces the `k` most frequent values directly, with no comparison-based selection anywhere. This works
precisely because the range of possible frequencies is bounded by the length of the input, which is the
structure the current heap selection ignores. It pays off most when the number of distinct values and
`k` are both large, which is the regime where the current selection carries its logarithm; when `k` is
small, the heap approach is already close in cost. It uses `O(n)` auxiliary space for the positions,
which is broadly comparable to the dictionary the current solution already maintains, so it is not a
memory regression in practice.

## Evidence

The scaling fit over ten sizes from `2^8` to `2^17` gives mine a log-log slope of 0.89 with an R² of
0.984, and brute a slope of 0.73 with an R² of 0.950. A slope near 1 is what a linear pass looks like,
so mine's fit is consistent with the `O(n)` counting pass dominating the measured time — but a single
slope cannot resolve a logarithmic factor in the selection term. The stronger signal is that brute fits
lower than mine even though brute's selection step is theoretically the worse of the two. The sweep is
mostly timing the counting pass that both implementations share, not the step that separates them, so
the fitted slopes should not be read as evidence that mine is already near-optimal. They are evidence
that this input family never exercises the selection.

The generator reinforces that reading. It draws values from a fixed bounded integer range, so the
number of distinct keys is bounded by a constant independent of `n`, and the selection over those keys
is not stressed as `n` grows. The `O(n log n)` worst case therefore never appears in the data, and the
class argument has to rest on what mine does per element and on the existence of the `O(n)` family,
not on the fit.

For the problem's bounds, the retrieved statement gives `1 <= nums.length <= 10^4`, with `k` between 1
and the number of distinct elements ([NeetCode](https://neetcode.io/solutions/top-k-frequent-elements)).
At that size the current solution and the bucketing approach are both comfortably fast, so the
asymptotic gain is real but practically marginal; the constant-factor improvement on the counting pass
is arguably the more relevant lever at this bound. Published analyses put the heap approach at
`O(n log k)` ([walkccc](https://walkccc.me/LeetCode/problems/0347/)) or `O(n + m log k)`
([AlgoMonster](https://algo.monster/liteproblems/347)), and the bucket approach at `O(n)`
([walkccc](https://walkccc.me/LeetCode/problems/0347/)). The official LeetCode page itself returned
HTTP 403 in this session; the statement was instead read from
[leetcode.ca](https://leetcode.ca/all/347.html), which does not list numeric constraints.

On the constant factor, the removable work is the duplicate hash probe in the counting loop and the
per-comparison Python call used as a key inside the selection. The former scales with `n`; the latter
scales with the number of distinct keys, which the generator bounds, so the selection is a small and
roughly fixed slice of the runtime. There is no recursion and no I/O in the hot path, and memory
allocation or copying in the selection does not look like a meaningful lever on these inputs. A
lower-overhead counting routine — a C-level counter, or an increment that probes the dictionary once
instead of twice — targets the pass that actually dominates.

## Questions to think about

- Which input shape separates the two selection classes: many distinct keys with a large `k`, or heavy
  duplication with a small `k`?
- If brute fits at 0.73 while mine fits at 0.89, which part of the two implementations is the sweep
  actually timing?
- Is the goal the better asymptotic class, or the smaller constant on the counting pass at the stated
  `nums.length` bound?
- How would the input family have to change for the selection term, rather than the shared counting
  prefix, to set the slope?
- If the counting loop were reduced to one lookup per element, how much of the remaining time would be
  the interpreter loop itself versus the hash operations?

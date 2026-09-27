# example-max-subarray

lc · tags and status: `.meta/exercise.toml` · scaffolding demo (excluded from the index and due list)

## Problem (my paraphrase)

Given a non-empty list of integers, return the largest sum you can get from a
contiguous, non-empty stretch of it.

## Approach

Kadane: scan left to right, keeping the best sum of a stretch that *ends here*.
Either extend the previous stretch or start fresh at this element, whichever is
larger; the answer is the best of those running values.

## Complexity

- Time: O(n) (brute: O(n²) over all start/end pairs using prefix sums)
- Space: O(1)

## Edge cases (chosen before coding)

- single element, negative
- all negative: answer is the largest single element, not 0
- all zeros
- the best stretch is the whole array / a prefix / a suffix

## Takeaways

- "Best ending here" turns an O(n²) search over intervals into one pass.
- Initialise from the first element, not 0, or all-negative inputs break.

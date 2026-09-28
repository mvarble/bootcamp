# lc0347-top-k-frequent-elements

[lc](https://leetcode.com/problems/top-k-frequent-elements/description/) · tags and status: `.meta/exercise.toml`

## Problem (my paraphrase)

Given a `nums` and `k`, return a list `out` (in any order) of distinct elements within `nums` that are amongst the `k` most frequent elements.

## Approach

My immediate instinct is to just look up the Python documentation and see if they have a heap queue.
Then I just have to use that datastructure as is.

If I did not have the ability to look it up, I would come up with a brute force solution:

- Make a map of `element: count` pairs by iterating over the list and bumping the value.
- Visit the map and build unzipped lists of the `element` and `count` entries, ordered by `count`.
- slice the `element` list from the previous step up to `k`.

## Complexity

- Time: `O(n log n)`
- Space: n/a

## Edge cases (chosen before coding)

There aren't really any edge cases, since we have the following constraints:

- `k` is in the range [1, the number of unique elements in the array]. (so we won't be handed `k == 0` or `k` too large).
- It is guaranteed that the answer is unique. (so we won't have to bump one out in case of tie).

## Takeaways

- The brute force method doesn't seem much slower than using maxheap.
  This should not be too surprising, seeing as I am only potentially speeding up the sorting.
- [The assessment](./analysis/assessment.md) tells me where I can improve the solution.
- (More of a meta takeaway) I spent way more time building the test harness.
  Time would be better used if I let AI do this for me.

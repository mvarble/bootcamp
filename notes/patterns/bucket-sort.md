# Bucket Sort

Bucket sort here means using a bounded integer key as an array index instead of comparing keys:
when the quantity you rank by (a frequency, a count, a digit, a bounded value) is an integer between 0
and `n`, you can drop each distinct key into the slot named by that quantity and then read the slots
back in rank order. It turns a comparison-based sort or a size-`k` heap selection into a linear pass,
at the cost of `O(n)` auxiliary space. It applies whenever the rank key has a known range that grows
only as fast as the input; it does not apply when the key is unbounded or continuous, where a heap or
quickselect is the better choice.

## Exercises

- [lc0347-top-k-frequent-elements](../../python/exercises/lc0347-top-k-frequent-elements) — top `k`
  by frequency; frequencies run 1..`n`, so bucket by frequency to reach `O(n)`.

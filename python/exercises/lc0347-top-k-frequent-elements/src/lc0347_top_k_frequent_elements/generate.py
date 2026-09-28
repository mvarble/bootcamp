"""Random inputs, plus the adapter that tests, stress, scale, and benches call implementations through."""

import random

# Sizes for `just scale`; None uses the harness default (2^8 .. 2^17).
SCALE_SIZES = None


def generate(n: int, seed: int) -> tuple[list[int], int]:
    """A random input of size n, deterministic in seed."""
    rng = random.Random(seed)

    # first generate the ordered counts of elements
    counts = []
    running_sum = 0
    max = n
    while True:
        next = random.randint(1, max)
        if running_sum + next >= n:
            counts.append(n - running_sum)
            break
        running_sum += next
        counts.append(next)
        max = next
    assert sum(counts) == n

    # then decide where we must cut off
    k = random.randint(1, len(counts))
    if k < len(counts) - 1:
        while k < len(counts) and counts[k - 1] == counts[k]:
            k += 1

    # generate the elements
    out = []
    elms = [rng.randint(-100, 100) for _ in counts]

    # randomly sample the elements by their counts
    while len(counts) != 0:
        elm_index = random.randint(0, len(counts) - 1)
        out.append(elms[elm_index])
        counts[elm_index] -= 1
        if counts[elm_index] == 0:
            elms = elms[:elm_index] + elms[(elm_index + 1) :]
            counts = counts[:elm_index] + counts[(elm_index + 1) :]

    assert len(out) == n
    return out, k


def call(impl, x):
    """Run implementation module `impl` (mine, brute, reference) on input x.

    Pass a copy if the implementation mutates its argument.
    """
    return impl.Solution().topKFrequent(list(x[0]), x[1])

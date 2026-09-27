"""My slow, obviously-correct oracle: every (start, end) pair via prefix sums, O(n^2)."""

from itertools import accumulate
from typing import List, Optional  # noqa: F401


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        prefix = [0, *accumulate(nums)]
        n = len(nums)
        return max(prefix[j] - prefix[i] for i in range(n) for j in range(i + 1, n + 1))

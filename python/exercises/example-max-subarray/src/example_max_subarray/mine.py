"""My solution: Kadane's scan, O(n) time, O(1) space."""

from typing import List, Optional  # noqa: F401  (names LeetCode stubs assume)


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        best = ending_here = nums[0]
        for x in nums[1:]:
            ending_here = max(x, ending_here + x)
            best = max(best, ending_here)
        return best

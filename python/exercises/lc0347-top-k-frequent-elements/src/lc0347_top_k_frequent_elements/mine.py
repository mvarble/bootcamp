import heapq


class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        # build the map of (element, count) pairs
        # `O(n)`
        elms_counts = {}
        for num in nums:
            if num not in elms_counts:
                elms_counts[num] = 1
            else:
                elms_counts[num] += 1

        # build the sorted zipped list
        elms_counts = heapq.nlargest(
            k,
            ((elm, num) for elm, num in elms_counts.items()),
            key=lambda p: p[1],
        )
        return [elm for (elm, num) in elms_counts]

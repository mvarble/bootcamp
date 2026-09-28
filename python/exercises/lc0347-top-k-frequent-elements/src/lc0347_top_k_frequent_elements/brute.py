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

        # build the unzipped ordered lists
        elms = []
        counts = []
        for elm, count in elms_counts.items():
            # slow, but surely correct ordered insertion
            # `O(n)`
            index = len(elms)
            for i in range(index):
                if counts[i] < count:
                    index = i
                    break
            elms.insert(index, elm)
            counts.insert(index, count)

        return elms[:k]

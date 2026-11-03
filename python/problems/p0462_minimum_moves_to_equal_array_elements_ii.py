import numpy as np

class Solution:
    def minMoves2(self, nums: list[int]) -> int:
        median = int(np.median(nums))

        count = 0
        for element in nums:
            count += abs(median - element)

        return count

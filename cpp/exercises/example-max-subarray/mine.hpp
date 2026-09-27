#pragma once
// My solution: Kadane's scan, O(n) time, O(1) space.

#include "harness/lc_prelude.hpp"

namespace mine {
using namespace std;

class Solution {
 public:
  int maxSubArray(vector<int>& nums) {
    int best = nums[0], ending_here = nums[0];
    for (size_t i = 1; i < nums.size(); ++i) {
      ending_here = max(nums[i], ending_here + nums[i]);
      best = max(best, ending_here);
    }
    return best;
  }
};

}  // namespace mine

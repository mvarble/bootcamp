#pragma once
// My slow, obviously-correct oracle: every (start, end) pair via prefix sums, O(n^2).

#include "harness/lc_prelude.hpp"

namespace brute {
using namespace std;

class Solution {
 public:
  int maxSubArray(vector<int>& nums) {
    vector<long long> prefix{0};
    for (int x : nums) prefix.push_back(prefix.back() + x);
    long long best = LLONG_MIN;
    for (size_t i = 0; i < nums.size(); ++i)
      for (size_t j = i + 1; j <= nums.size(); ++j) best = max(best, prefix[j] - prefix[i]);
    return static_cast<int>(best);
  }
};

}  // namespace brute

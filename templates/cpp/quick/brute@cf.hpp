#pragma once
// My slow, obviously-correct oracle. Same signature as mine::Solution::solve.

#include "generate.hpp"
#include "harness/lc_prelude.hpp"

namespace brute {

struct Solution {
  static Output solve(const Input& x) {
    (void)x;
    throw std::logic_error("not implemented");
  }
};

}  // namespace brute

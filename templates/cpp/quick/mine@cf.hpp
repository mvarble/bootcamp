#pragma once
// My solution: a pure function of the parsed input. shim.hpp does the parsing and formatting.

#include "generate.hpp"
#include "harness/lc_prelude.hpp"

namespace mine {

struct Solution {
  static Output solve(const Input& x) {
    (void)x;
    throw std::logic_error("not implemented");
  }
};

}  // namespace mine

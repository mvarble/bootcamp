// My tests: examples and edge cases chosen before coding, then stress against brute.
// Every TYPED_TEST runs once per implementation listed in impls.hpp.

#include <gtest/gtest.h>

#include <cstddef>
#include <cstdint>
#include <utility>
#include <vector>

#include "brute.hpp"
#include "generate.hpp"
#include "harness/gtest.hpp"
#include "harness/testing.hpp"
#include "impls.hpp"

using CaseList = std::vector<std::pair<Input, Output>>;

template <class S>
class Cases : public ::testing::Test {
 protected:
  static void check(const CaseList& cases) {
    for (const auto& [x, want] : cases) EXPECT_EQ(call<S>(x), want);
  }
};
TYPED_TEST_SUITE(Cases, harness::GtestTypes<ImplTypes>, ImplNames);

TYPED_TEST(Cases, Examples) {
  TestFixture::check({
      {{-2, 1, -3, 4, -1, 2, 1, -5, 4}, 6},
      {{1}, 1},
      {{5, 4, -1, 7, 8}, 23},
  });
}

TYPED_TEST(Cases, EdgeCases) {
  TestFixture::check({
      {{-5}, -5},              // single negative
      {{-3, -1, -2}, -1},      // all negative: best single element, not 0
      {{0, 0, 0}, 0},
      {{2, 3, 4}, 9},          // whole array
      {{4, -10, 1}, 4},        // prefix
      {{1, -10, 4, 5}, 9},     // suffix
  });
}

TYPED_TEST(Cases, Stress) {
  const int iters = harness::stress_iters();
  for (int i = 0; i < iters; ++i) {
    const auto n = static_cast<std::size_t>(i) * 64 / static_cast<std::size_t>(iters);  // ascending n
    const auto seed = static_cast<std::uint64_t>(i);
    const Input x = generate(n, seed);
    ASSERT_EQ(call<TypeParam>(x), call<brute::Solution>(x)) << "n=" << n << " seed=" << seed;
  }
}

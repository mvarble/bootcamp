#pragma once
// Random inputs, plus the adapter that tests, stress, scale, and benches call implementations through.

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <random>
#include <vector>

using Input = std::vector<int>;
using Output = int;

// Sizes for `just scale`; empty uses the harness default (2^10 ..= 2^22).
inline const std::vector<std::size_t> kScaleSizes{};

// A random non-empty input of length max(n, 1), deterministic in seed.
// Small values make ties and all-negative runs common.
inline Input generate(std::size_t n, std::uint64_t seed) {
  std::mt19937_64 rng(seed);
  std::uniform_int_distribution<int> value(-10, 10);
  Input x(std::max<std::size_t>(n, 1));
  for (auto& v : x) v = value(rng);
  return x;
}

// How to run implementation S (mine::Solution, brute::Solution, ...) on an input.
// Copies x because LeetCode signatures take non-const references.
template <class S>
Output call(const Input& x) {
  Input copy = x;
  return S{}.maxSubArray(copy);
}

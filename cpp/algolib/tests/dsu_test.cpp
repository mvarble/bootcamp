#include "algolib/dsu.hpp"

#include <gtest/gtest.h>

#include <algorithm>
#include <cstdint>
#include <random>
#include <set>
#include <utility>
#include <vector>

using algolib::Dsu;

TEST(Dsu, StartsAsSingletons) {
  Dsu d(4);
  EXPECT_EQ(d.len(), 4u);
  EXPECT_EQ(d.components(), 4u);
  for (std::size_t i = 0; i < 4; ++i) {
    EXPECT_EQ(d.find(i), i);
    EXPECT_EQ(d.set_size(i), 1u);
  }
}

TEST(Dsu, UniteAndQueries) {
  Dsu d(6);
  EXPECT_TRUE(d.unite(0, 1));
  EXPECT_TRUE(d.unite(1, 2));
  EXPECT_FALSE(d.unite(0, 2));
  EXPECT_TRUE(d.same(0, 2));
  EXPECT_FALSE(d.same(0, 3));
  EXPECT_EQ(d.set_size(2), 3u);
  EXPECT_EQ(d.components(), 4u);
}

TEST(Dsu, SelfUniteIsNoop) {
  Dsu d(2);
  EXPECT_FALSE(d.unite(1, 1));
  EXPECT_EQ(d.components(), 2u);
}

TEST(Dsu, Empty) {
  Dsu d(0);
  EXPECT_EQ(d.len(), 0u);
  EXPECT_EQ(d.components(), 0u);
}

// Oracle: relabel until fixpoint.
static std::vector<std::size_t> naive_labels(std::size_t n, const std::vector<std::pair<std::size_t, std::size_t>>& edges) {
  std::vector<std::size_t> label(n);
  for (std::size_t i = 0; i < n; ++i) label[i] = i;
  for (bool changed = true; changed;) {
    changed = false;
    for (auto [a, b] : edges) {
      const auto lo = std::min(label[a], label[b]);
      for (auto v : {a, b}) {
        if (label[v] != lo) {
          label[v] = lo;
          changed = true;
        }
      }
    }
  }
  return label;
}

TEST(Dsu, MatchesNaiveOracle) {
  for (std::uint64_t seed = 0; seed < 300; ++seed) {
    std::mt19937_64 rng(seed);
    const std::size_t n = 1 + rng() % 30;
    std::vector<std::pair<std::size_t, std::size_t>> edges(rng() % 60);
    for (auto& [a, b] : edges) a = rng() % n, b = rng() % n;

    Dsu d(n);
    for (auto [a, b] : edges) d.unite(a, b);
    const auto label = naive_labels(n, edges);
    for (std::size_t a = 0; a < n; ++a) {
      for (std::size_t b = 0; b < n; ++b) ASSERT_EQ(d.same(a, b), label[a] == label[b]) << "seed=" << seed;
      ASSERT_EQ(d.set_size(a), static_cast<std::size_t>(std::count(label.begin(), label.end(), label[a])));
    }
    ASSERT_EQ(d.components(), std::set(label.begin(), label.end()).size());
  }
}

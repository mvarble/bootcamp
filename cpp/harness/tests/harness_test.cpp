#include <gtest/gtest.h>

#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <numeric>
#include <sstream>
#include <string>
#include <thread>
#include <unistd.h>
#include <vector>

#include "harness/scaling.hpp"
#include "harness/testing.hpp"
#include "harness/typelist.hpp"

namespace {

using Input = std::vector<long>;

long sum(const Input& x) { return std::accumulate(x.begin(), x.end(), 0L); }

long slow(const Input& x) {
  std::this_thread::sleep_for(std::chrono::milliseconds(3));
  return sum(x);
}

Input iota_gen(std::size_t n, std::uint64_t) {
  Input x(n);
  std::iota(x.begin(), x.end(), 0L);
  return x;
}

}  // namespace

TEST(Scaling, DropsImplsOverBudgetAndWritesOneRecordPerRep) {
  const auto out = std::filesystem::temp_directory_path() / ("harness-test-" + std::to_string(::getpid()) + ".jsonl");
  std::filesystem::remove(out);
  harness::run<Input, long>({{"fast", &sum}, {"slow", &slow}}, &iota_gen, out, {4, 8}, /*reps=*/2, /*budget=*/1e-3);
  std::ifstream in(out);
  std::vector<std::string> lines;
  for (std::string line; std::getline(in, line);) lines.push_back(line);
  std::filesystem::remove(out);
  ASSERT_EQ(lines.size(), 6u);  // n=4: fast+slow, n=8: fast only
  for (const auto& l : lines) EXPECT_NE(l.find(R"("lang": "cpp")"), std::string::npos);
  for (const auto& l : lines) EXPECT_FALSE(l.find(R"("n": 8)") != std::string::npos && l.find("slow") != std::string::npos);
}

TEST(TypeList, VisitsTypesInOrderWithIndex) {
  std::string seen;
  harness::for_each_type(harness::TypeList<int, double>{}, [&]<class T>(std::size_t i) {
    seen += std::to_string(i) + (std::is_same_v<T, int> ? "i" : "d");
  });
  EXPECT_EQ(seen, "0i1d");
}

TEST(Testing, TokensIgnoreWhitespaceLayout) {
  EXPECT_EQ(harness::tokens("1 2\n3\n"), harness::tokens(" 1\n2 3 "));
}

#pragma once
// Helpers for exercise tests: stress iteration count and Codeforces sample files.

#include <gtest/gtest.h>

#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

namespace harness {

// Iterations for seeded stress loops: $STRESS_ITERS (set by `just stress`) or the fallback.
inline int stress_iters(int fallback = 200) {
  if (const char* env = std::getenv("STRESS_ITERS")) return std::max(1, std::atoi(env));
  return fallback;
}

inline std::vector<std::string> tokens(const std::string& text) {
  std::istringstream in(text);
  return {std::istream_iterator<std::string>(in), std::istream_iterator<std::string>()};
}

inline std::string slurp(const std::filesystem::path& p) {
  std::ifstream f(p);
  return {std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()};
}

// Runs every <dir>/*.in through `run` and compares whitespace-separated tokens with the matching .out.
inline void check_samples(const std::filesystem::path& dir, const std::function<void(std::istream&, std::ostream&)>& run) {
  std::vector<std::filesystem::path> inputs;
  if (std::filesystem::is_directory(dir)) {
    for (const auto& e : std::filesystem::directory_iterator(dir))
      if (e.path().extension() == ".in") inputs.push_back(e.path());
  }
  std::sort(inputs.begin(), inputs.end());
  if (inputs.empty()) GTEST_SKIP() << "no samples in " << dir;
  for (const auto& in_path : inputs) {
    auto out_path = in_path;
    out_path.replace_extension(".out");
    SCOPED_TRACE(in_path.filename().string());
    ASSERT_TRUE(std::filesystem::exists(out_path)) << "missing " << out_path;
    std::istringstream in(slurp(in_path));
    std::ostringstream out;
    run(in, out);
    EXPECT_EQ(tokens(out.str()), tokens(slurp(out_path)));
  }
}

}  // namespace harness

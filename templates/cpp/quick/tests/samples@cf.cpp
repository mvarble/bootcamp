// Wiring: every provided/samples/*.in through run(), compared token-by-token with the matching .out.

#include <gtest/gtest.h>

#include <filesystem>

#include "harness/testing.hpp"
#include "shim.hpp"

TEST(Samples, MatchExpectedOutput) {
  harness::check_samples(std::filesystem::path(EXERCISE_DIR) / "provided" / "samples", run);
}

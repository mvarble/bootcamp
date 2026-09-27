#pragma once
// Wiring: the implementations that tests, stress, scale, and bench are instantiated for.

#include <array>
#include <cstddef>
#include <string>

#include "harness/typelist.hpp"
#include "mine.hpp"

using ImplTypes = harness::TypeList<mine::Solution>;
inline constexpr std::array kImplNames{"mine"};

// GoogleTest name generator: typed tests show up as Cases/mine.Examples, Cases/reference.Examples, ...
struct ImplNames {
  template <class T>
  static std::string GetName(int i) {
    return kImplNames[static_cast<std::size_t>(i)];
  }
};

#pragma once
// Adapts harness::TypeList to GoogleTest typed tests.

#include <gtest/gtest.h>

#include "harness/typelist.hpp"

namespace harness {

template <class List>
struct AsGtestTypes;

template <class... Ts>
struct AsGtestTypes<TypeList<Ts...>> {
  using type = ::testing::Types<Ts...>;
};

template <class List>
using GtestTypes = typename AsGtestTypes<List>::type;

}  // namespace harness

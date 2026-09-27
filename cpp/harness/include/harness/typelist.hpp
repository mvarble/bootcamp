#pragma once
// A compile-time list of implementation types. impls.hpp in each exercise names
// its implementations once; tests, scale, and bench are all instantiated from it.

#include <cstddef>
#include <utility>

namespace harness {

template <class... Ts>
struct TypeList {};

// Calls f.template operator()<T>(index) for each T in the list, in order.
template <class... Ts, class F>
void for_each_type(TypeList<Ts...>, F&& f) {
  std::size_t i = 0;
  (f.template operator()<Ts>(i++), ...);
}

}  // namespace harness

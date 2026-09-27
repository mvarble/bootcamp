// Wiring: `example-max-subarray_scale [OUT.jsonl]` (release preset) times every implementation over a size sweep.

#include <cstddef>

#include "brute.hpp"
#include "generate.hpp"
#include "harness/scaling.hpp"
#include "impls.hpp"

int main(int argc, char** argv) {
  harness::Impls<Input, Output> impls;
  harness::for_each_type(ImplTypes{}, [&]<class S>(std::size_t i) { impls.emplace_back(kImplNames[i], &call<S>); });
  impls.emplace_back("brute", &call<brute::Solution>);
  return harness::scaling_main(impls, &generate, kScaleSizes, EXERCISE_DIR, argc, argv);
}

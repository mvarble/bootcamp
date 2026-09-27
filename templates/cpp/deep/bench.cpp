// Wiring (deep tier): Google Benchmark, one benchmark per implementation and size.
// `just bench <path>` runs repetitions and writes raw JSON (incl. mean/stddev/cv
// aggregates) to .meta/bench/gbench.json.

#include <benchmark/benchmark.h>

#include <cstddef>
#include <string>
#include <vector>

#include "generate.hpp"
#include "impls.hpp"

namespace {
const std::vector<std::size_t> kBenchSizes{1'000, 100'000};
}  // namespace

int main(int argc, char** argv) {
  harness::for_each_type(ImplTypes{}, [&]<class S>(std::size_t i) {
    for (const std::size_t n : kBenchSizes) {
      const std::string name = std::string(kImplNames[i]) + "/" + std::to_string(n);
      benchmark::RegisterBenchmark(name.c_str(), [n](benchmark::State& state) {
        Input x = generate(n, 0);
        for (auto _ : state) {
          benchmark::DoNotOptimize(x);
          Output result = call<S>(x);
          benchmark::DoNotOptimize(result);
        }
      });
    }
  });
  benchmark::Initialize(&argc, argv);
  benchmark::RunSpecifiedBenchmarks();
  benchmark::Shutdown();
}

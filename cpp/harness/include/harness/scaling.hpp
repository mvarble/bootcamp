#pragma once
// Size-sweep timing shared by every exercise's `<slug>_scale` target.
//
// For each size n the input is generated once, outside the timed region; each
// implementation is then timed `reps` times. Input and result go through
// do_not_optimize so the compiler can neither hoist the call out of the batch
// loop nor drop it. Every sample is appended to a JSONL file as
// {impl, n, seconds, rep, run, lang}. An implementation whose median exceeds
// `budget` seconds is dropped from larger sizes.

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace harness {

template <class T>
inline void do_not_optimize(const T& value) {
  asm volatile("" : : "r,m"(value) : "memory");
}

template <class I, class O>
using Impl = std::pair<std::string, O (*)(const I&)>;

template <class I, class O>
using Impls = std::vector<Impl<I, O>>;

// 2^10 ..= 2^22.
inline std::vector<std::size_t> default_sizes() {
  std::vector<std::size_t> sizes;
  for (int k = 10; k <= 22; ++k) sizes.push_back(std::size_t{1} << k);
  return sizes;
}

// Seconds per call of f(x). Fast calls are batched until a sample spans min_time.
template <class I, class O>
double measure(O (*f)(const I&), const I& x, double min_time = 2e-3) {
  using clock = std::chrono::steady_clock;
  std::uint64_t iters = 1;
  for (;;) {
    const auto t0 = clock::now();
    for (std::uint64_t i = 0; i < iters; ++i) {
      do_not_optimize(x);
      O result = f(x);
      do_not_optimize(result);
    }
    const double dt = std::chrono::duration<double>(clock::now() - t0).count();
    if (dt >= min_time) return dt / static_cast<double>(iters);
    iters = std::max(iters * 2, static_cast<std::uint64_t>(static_cast<double>(iters) * min_time / std::max(dt, 1e-9) * 1.2));
  }
}

inline std::string iso_utc_now() {
  const std::time_t t = std::time(nullptr);
  std::tm tm{};
  gmtime_r(&t, &tm);
  char buf[32];
  std::strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", &tm);
  return buf;
}

template <class I, class O>
void run(Impls<I, O> alive, I (*generate)(std::size_t, std::uint64_t), const std::filesystem::path& out,
         const std::vector<std::size_t>& sizes, int reps = 5, double budget = 0.5, std::uint64_t seed = 0) {
  if (out.has_parent_path()) std::filesystem::create_directories(out.parent_path());
  std::ofstream file(out, std::ios::app);
  const std::string run_id = iso_utc_now();
  for (const std::size_t n : sizes) {
    if (alive.empty()) break;
    const I x = generate(n, seed);
    std::erase_if(alive, [&](const Impl<I, O>& impl) {
      std::vector<double> samples;
      for (int rep = 0; rep < reps; ++rep) {
        const double s = measure(impl.second, x);
        samples.push_back(s);
        file << R"({"impl": ")" << impl.first << R"(", "n": )" << n << R"(, "seconds": )" << s
             << R"(, "rep": )" << rep << R"(, "run": ")" << run_id << R"(", "lang": "cpp"})" << '\n';
      }
      std::sort(samples.begin(), samples.end());
      const double median = samples[samples.size() / 2];
      std::cout << impl.first << "  n=" << n << "  median=" << median << "s" << std::endl;
      return median > budget;
    });
  }
  std::cout << "appended to " << out.string() << std::endl;
}

// Entry point for scale.cpp: argv[1] (optional) overrides <exercise>/.meta/bench/scaling.jsonl.
template <class I, class O>
int scaling_main(const Impls<I, O>& impls, I (*generate)(std::size_t, std::uint64_t), const std::vector<std::size_t>& sizes,
                 const char* exercise_dir, int argc, char** argv) {
  const std::filesystem::path out =
      argc > 1 ? std::filesystem::path(argv[1]) : std::filesystem::path(exercise_dir) / ".meta" / "bench" / "scaling.jsonl";
  run(impls, generate, out, sizes.empty() ? default_sizes() : sizes);
  return 0;
}

}  // namespace harness

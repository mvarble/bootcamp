# Helpers shared by every exercise's one-line CMakeLists.txt.

set(BOOTCAMP_WARNINGS -Wall -Wextra -Wpedantic)

# Google Benchmark is fetched only when some deep-tier exercise asks for it.
function(bootcamp_require_benchmark)
  if(TARGET benchmark::benchmark)
    return()
  endif()
  FetchContent_Declare(
    benchmark
    URL https://github.com/google/benchmark/archive/refs/tags/v1.9.5.tar.gz
    URL_HASH SHA256=9631341c82bac4a288bef951f8b26b41f69021794184ece969f8473977eaa340
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  )
  set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
  set(BENCHMARK_ENABLE_GTEST_TESTS OFF CACHE BOOL "" FORCE)
  set(BENCHMARK_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
  set(BENCHMARK_ENABLE_WERROR OFF CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(benchmark)
endfunction()

# bootcamp_exercise(<slug> [CF] [DEEP])
#
# Targets, all prefixed with the slug:
#   <slug>_lib    interface library: the exercise dir on the include path + harness
#   <slug>_tests  tests/cases.cpp (+ tests/samples.cpp for CF), discovered into CTest as <slug>/...
#   <slug>_scale  size sweep -> .meta/bench/scaling.jsonl (build with the release preset)
#   <slug>_main   CF only: stdin/stdout entry point
#   <slug>_bench  DEEP only: Google Benchmark constant-factor comparison
function(bootcamp_exercise slug)
  cmake_parse_arguments(PARSE_ARGV 1 ARG "CF;DEEP" "" "")
  set(dir "${CMAKE_CURRENT_SOURCE_DIR}")

  add_library(${slug}_lib INTERFACE)
  target_include_directories(${slug}_lib INTERFACE "${dir}")
  target_link_libraries(${slug}_lib INTERFACE harness)
  target_compile_definitions(${slug}_lib INTERFACE EXERCISE_DIR="${dir}")

  set(test_sources tests/cases.cpp)
  if(ARG_CF)
    list(APPEND test_sources tests/samples.cpp)
  endif()
  add_executable(${slug}_tests ${test_sources})
  target_link_libraries(${slug}_tests PRIVATE ${slug}_lib GTest::gtest_main)
  target_compile_options(${slug}_tests PRIVATE ${BOOTCAMP_WARNINGS})
  # NO_PRETTY_TYPES keeps ImplNames labels (Cases/mine.Stress) instead of C++ type names.
  gtest_discover_tests(${slug}_tests TEST_PREFIX "${slug}/" DISCOVERY_MODE PRE_TEST NO_PRETTY_TYPES)

  add_executable(${slug}_scale scale.cpp)
  target_link_libraries(${slug}_scale PRIVATE ${slug}_lib)
  target_compile_options(${slug}_scale PRIVATE ${BOOTCAMP_WARNINGS})

  if(ARG_CF)
    add_executable(${slug}_main main.cpp)
    target_link_libraries(${slug}_main PRIVATE ${slug}_lib)
    target_compile_options(${slug}_main PRIVATE ${BOOTCAMP_WARNINGS})
  endif()

  if(ARG_DEEP)
    bootcamp_require_benchmark()
    add_executable(${slug}_bench bench.cpp)
    target_link_libraries(${slug}_bench PRIVATE ${slug}_lib benchmark::benchmark)
    target_compile_options(${slug}_bench PRIVATE ${BOOTCAMP_WARNINGS})
  endif()
endfunction()

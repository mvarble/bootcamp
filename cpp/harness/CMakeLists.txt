# Header-only infrastructure shared by exercises: scaling runs, type lists, stress/sample helpers.
add_library(harness INTERFACE)
target_include_directories(harness INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_executable(harness_tests tests/harness_test.cpp)
target_link_libraries(harness_tests PRIVATE harness GTest::gtest_main)
target_compile_options(harness_tests PRIVATE ${BOOTCAMP_WARNINGS})
gtest_discover_tests(harness_tests TEST_PREFIX "harness/" DISCOVERY_MODE PRE_TEST)

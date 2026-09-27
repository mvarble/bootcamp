add_library(algolib INTERFACE)
target_include_directories(algolib INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_executable(algolib_tests tests/dsu_test.cpp)
target_link_libraries(algolib_tests PRIVATE algolib GTest::gtest_main)
target_compile_options(algolib_tests PRIVATE ${BOOTCAMP_WARNINGS})
gtest_discover_tests(algolib_tests TEST_PREFIX "algolib/" DISCOVERY_MODE PRE_TEST)

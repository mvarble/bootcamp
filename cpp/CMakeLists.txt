cmake_minimum_required(VERSION 3.24...4.4)
project(bootcamp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)

# GoogleTest, pinned by release tarball + hash.
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/releases/download/v1.18.0/googletest-1.18.0.tar.gz
  URL_HASH SHA256=6e3191c1455468b3fc35a417fb565c1c5071aee1b7e7f85e30cf48a98d37d8b5
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
set(BUILD_GMOCK OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()
include(GoogleTest)
include(cmake/Bootcamp.cmake)

add_subdirectory(harness)
add_subdirectory(algolib)

# Every exercises/<slug>/ with a CMakeLists.txt. With SKIP_ATTEMPTING=1 (CI),
# exercises whose status is "attempting" are left out: their stubs fail by design.
file(GLOB exercise_dirs LIST_DIRECTORIES true "${CMAKE_CURRENT_SOURCE_DIR}/exercises/*")
foreach(dir IN LISTS exercise_dirs)
  if(NOT EXISTS "${dir}/CMakeLists.txt")
    continue()
  endif()
  if("$ENV{SKIP_ATTEMPTING}" STREQUAL "1" AND EXISTS "${dir}/.meta/exercise.toml")
    file(STRINGS "${dir}/.meta/exercise.toml" attempting REGEX "^status *= *\"attempting\"")
    if(attempting)
      message(STATUS "Skipping in-progress exercise ${dir}")
      continue()
    endif()
  endif()
  add_subdirectory("${dir}")
endforeach()

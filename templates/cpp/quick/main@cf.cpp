// Wiring: the Codeforces-style entry point, `build/<preset>/exercises/{{slug}}/{{slug}}_main < input`.

#include <iostream>

#include "shim.hpp"

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);
  run(std::cin, std::cout);
}

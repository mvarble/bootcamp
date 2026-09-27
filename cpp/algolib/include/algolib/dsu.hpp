#pragma once
// Disjoint-set union (union-find).

#include <cstddef>
#include <numeric>
#include <utility>
#include <vector>

namespace algolib {

// Disjoint-set union over 0..n-1 with path halving and union by size.
// find/unite run in amortized O(alpha(n)).
class Dsu {
 public:
  explicit Dsu(std::size_t n) : parent_(n), size_(n, 1), components_(n) {
    std::iota(parent_.begin(), parent_.end(), std::size_t{0});
  }

  [[nodiscard]] std::size_t len() const { return parent_.size(); }

  // Number of disjoint sets.
  [[nodiscard]] std::size_t components() const { return components_; }

  std::size_t find(std::size_t x) {
    while (parent_[x] != x) {
      parent_[x] = parent_[parent_[x]];
      x = parent_[x];
    }
    return x;
  }

  // Merges the sets of a and b. Returns false if they were already joined.
  bool unite(std::size_t a, std::size_t b) {
    a = find(a);
    b = find(b);
    if (a == b) return false;
    if (size_[a] < size_[b]) std::swap(a, b);
    parent_[b] = a;
    size_[a] += size_[b];
    --components_;
    return true;
  }

  bool same(std::size_t a, std::size_t b) { return find(a) == find(b); }

  // Size of the set containing x.
  std::size_t set_size(std::size_t x) { return size_[find(x)]; }

 private:
  std::vector<std::size_t> parent_;
  std::vector<std::size_t> size_;
  std::size_t components_;
};

}  // namespace algolib

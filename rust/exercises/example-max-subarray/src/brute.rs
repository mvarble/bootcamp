//! My slow, obviously-correct oracle: every (start, end) pair via prefix sums, O(n^2).

pub struct Solution;

impl Solution {
    pub fn max_sub_array(nums: Vec<i32>) -> i32 {
        let mut prefix = vec![0i64];
        for &x in &nums {
            prefix.push(prefix.last().unwrap() + i64::from(x));
        }
        let n = nums.len();
        let best = (0..n).flat_map(|i| (i + 1..=n).map(move |j| (i, j))).map(|(i, j)| prefix[j] - prefix[i]).max();
        best.expect("non-empty input") as i32
    }
}

//! My solution: Kadane's scan, O(n) time, O(1) space.

pub struct Solution;

impl Solution {
    pub fn max_sub_array(nums: Vec<i32>) -> i32 {
        let (mut best, mut ending_here) = (nums[0], nums[0]);
        for &x in &nums[1..] {
            ending_here = x.max(ending_here + x);
            best = best.max(ending_here);
        }
        best
    }
}

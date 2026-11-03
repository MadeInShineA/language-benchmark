pub struct Solution;

impl Solution {
    pub fn min_moves2(mut numbers: Vec<i32>) -> i32 {
        numbers.sort();

        let numbers_size = numbers.len();
        let median = numbers[numbers_size / 2];

        numbers.iter().map(|element| (median - element).abs()).sum()
    }
}

//! Parse the input text, solve with `mine`, and format the answer.

pub fn run(input: &str) -> String {
    let tokens: Vec<&str> = input.split_ascii_whitespace().collect();
    let _ = (tokens, crate::mine::solve);
    todo!("parse, solve, format")
}

//! Wiring: implementation modules, plus `impls::<name>` and `IMPLS` built from `generate::call!`.
//! Tests, stress, scale, and benches all call implementations through these.

pub mod brute;
pub mod generate;
pub mod mine;
pub mod shim;

macro_rules! wire {
    ($($imp:ident),+) => {
        /// One plain function per implementation: `impls::mine(&input)`.
        pub mod impls {
            use crate::generate::{Input, Output, call};
            $(pub fn $imp(x: &Input) -> Output { call!($imp, x) })+
        }

        /// Every implementation by name, brute last.
        pub const IMPLS: &[(&str, fn(&generate::Input) -> generate::Output)] =
            &[$((stringify!($imp), impls::$imp as fn(&generate::Input) -> generate::Output)),+];
    };
}

wire!(mine, brute);

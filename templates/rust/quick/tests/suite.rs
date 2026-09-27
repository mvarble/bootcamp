//! Wiring: instantiate my suite (tests/cases/mod.rs) once per implementation.

#[macro_use]
mod cases;

suite!(mine);

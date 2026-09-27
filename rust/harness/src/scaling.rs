//! Size-sweep timing shared by every exercise's `cargo run --release --example scale`.
//!
//! For each size `n` the input is generated once, outside the timed region; each
//! implementation is then timed `reps` times, with its result passed through
//! `black_box` so the optimizer cannot drop the call. Every sample is appended to
//! a JSONL file as `{impl, n, seconds, rep, run, lang}`. An implementation whose
//! median exceeds `budget` seconds is dropped from larger sizes.

use std::fs::{self, OpenOptions};
use std::hint::black_box;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

/// 2^10 ..= 2^22.
pub const DEFAULT_SIZES: &[usize] = &[
    1 << 10, 1 << 11, 1 << 12, 1 << 13, 1 << 14, 1 << 15, 1 << 16,
    1 << 17, 1 << 18, 1 << 19, 1 << 20, 1 << 21, 1 << 22,
];

pub struct Config<'a> {
    pub sizes: &'a [usize],
    pub reps: usize,
    pub budget: f64,
    pub seed: u64,
}

impl Default for Config<'_> {
    fn default() -> Self {
        Self { sizes: DEFAULT_SIZES, reps: 5, budget: 0.5, seed: 0 }
    }
}

/// Seconds per call of `f(x)`. Fast calls are batched until a sample spans `min_time`.
pub fn measure<I, O>(f: fn(&I) -> O, x: &I, min_time: f64) -> f64 {
    let mut iters: u64 = 1;
    loop {
        let t0 = Instant::now();
        for _ in 0..iters {
            black_box(f(black_box(x)));
        }
        let dt = t0.elapsed().as_secs_f64();
        if dt >= min_time {
            return dt / iters as f64;
        }
        iters = (iters * 2).max((iters as f64 * min_time / dt.max(1e-9) * 1.2) as u64);
    }
}

pub fn run<I, O>(
    impls: &[(&str, fn(&I) -> O)],
    generate: fn(usize, u64) -> I,
    out: &Path,
    cfg: &Config,
) -> io::Result<()> {
    if let Some(dir) = out.parent() {
        fs::create_dir_all(dir)?;
    }
    let mut file = OpenOptions::new().create(true).append(true).open(out)?;
    let run_id = iso_utc_now();
    let mut alive: Vec<(&str, fn(&I) -> O)> = impls.to_vec();
    for &n in cfg.sizes {
        if alive.is_empty() {
            break;
        }
        let x = generate(n, cfg.seed);
        alive.retain(|&(name, f)| {
            let mut samples = Vec::with_capacity(cfg.reps);
            for rep in 0..cfg.reps {
                let s = measure(f, &x, 2e-3);
                samples.push(s);
                writeln!(
                    file,
                    r#"{{"impl": "{name}", "n": {n}, "seconds": {s:e}, "rep": {rep}, "run": "{run_id}", "lang": "rust"}}"#
                )
                .expect("write scaling record");
            }
            samples.sort_by(f64::total_cmp);
            let median = samples[samples.len() / 2];
            println!("{name:>10}  n={n:>9}  median={median:.3e}s");
            median <= cfg.budget
        });
    }
    println!("appended to {}", out.display());
    Ok(())
}

/// Entry point for `examples/scale.rs`: `[OUT.jsonl]` defaults to `<exercise>/.meta/bench/scaling.jsonl`.
pub fn main<I, O>(impls: &[(&str, fn(&I) -> O)], generate: fn(usize, u64) -> I, sizes: &[usize], manifest_dir: &str) {
    let out = std::env::args()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| Path::new(manifest_dir).join(".meta/bench/scaling.jsonl"));
    let cfg = Config { sizes: if sizes.is_empty() { DEFAULT_SIZES } else { sizes }, ..Config::default() };
    run(impls, generate, &out, &cfg).expect("scaling run");
}

/// Current UTC time as `YYYY-MM-DDTHH:MM:SSZ` (std has no calendar formatting).
fn iso_utc_now() -> String {
    let secs = SystemTime::now().duration_since(UNIX_EPOCH).expect("clock after epoch").as_secs() as i64;
    let (days, rem) = (secs.div_euclid(86_400), secs.rem_euclid(86_400));
    // Howard Hinnant's civil_from_days.
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = yoe + era * 400 + i64::from(m <= 2);
    format!("{y:04}-{m:02}-{d:02}T{:02}:{:02}:{:02}Z", rem / 3600, rem % 3600 / 60, rem % 60)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sum(x: &Vec<u64>) -> u64 {
        x.iter().sum()
    }

    fn slow(x: &Vec<u64>) -> u64 {
        std::thread::sleep(std::time::Duration::from_millis(3));
        x.iter().sum()
    }

    #[test]
    fn drops_impls_over_budget_and_writes_one_record_per_rep() {
        let out = std::env::temp_dir().join(format!("harness-test-{}.jsonl", std::process::id()));
        let _ = fs::remove_file(&out);
        let impls: [(&str, fn(&Vec<u64>) -> u64); 2] = [("fast", sum), ("slow", slow)];
        let cfg = Config { sizes: &[4, 8], reps: 2, budget: 1e-3, seed: 0 };
        run(&impls, |n, _| (0..n as u64).collect(), &out, &cfg).unwrap();
        let text = fs::read_to_string(&out).unwrap();
        fs::remove_file(&out).unwrap();
        assert_eq!(text.lines().count(), 2 + 2 + 2); // n=4: fast+slow, n=8: fast only
        assert!(text.lines().all(|l| l.contains(r#""lang": "rust""#)));
        assert!(!text.lines().any(|l| l.contains(r#""n": 8"#) && l.contains("slow")));
    }

    #[test]
    fn iso_timestamp_shape() {
        let s = iso_utc_now();
        assert_eq!(s.len(), 20);
        assert!(s.starts_with("20") && s.ends_with('Z'));
    }
}

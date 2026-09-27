#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["matplotlib==3.11.2"]
# ///
"""Empirical complexity from a scale run: per implementation, fit log(seconds) = k·log(n) + c.

usage: scaling.py <scaling.jsonl> [--run latest|all|RUN] [--floor SECONDS] [--no-plot]

Uses the median of each (impl, n) group. Points below --floor seconds are dropped
from the fit because fixed per-call overhead flattens the curve there. Writes
scaling.png next to the JSONL unless --no-plot.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def load(path: Path, run: str) -> list[dict]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not records:
        sys.exit(f"{path}: no records")
    if run == "latest":
        run = records[-1]["run"]
    return records if run == "all" else [r for r in records if r["run"] == run]


def medians(records: list[dict]) -> dict[str, list[tuple[int, float]]]:
    groups: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        groups[r["impl"]][r["n"]].append(r["seconds"])
    return {impl: sorted((n, statistics.median(s)) for n, s in by_n.items()) for impl, by_n in groups.items()}


def fit(points: list[tuple[int, float]]) -> tuple[float, float, float]:
    """Least squares on (log n, log t). Returns (slope, intercept, r²)."""
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(t) for _, t in points]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return slope, intercept, (1 - ss_res / ss_tot) if ss_tot else 1.0


def pow2(n: int) -> str:
    k = math.log2(n)
    return f"2^{int(k)}" if k.is_integer() else str(n)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("--run", default="latest", help="run id, 'latest' (default), or 'all'")
    ap.add_argument("--floor", type=float, default=1e-5, help="ignore medians below this many seconds (default 1e-5)")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    records = load(args.jsonl, args.run)
    series = medians(records)
    runs = sorted({r["run"] for r in records})
    print(f"{args.jsonl}  run: {runs[0] if len(runs) == 1 else f'{len(runs)} runs'}  lang: {records[0]['lang']}")
    print(f"{'impl':<12}{'points':>7}  {'n range':<16}{'slope':>7}{'R²':>8}")
    fits = {}
    for impl, pts in series.items():
        used = [(n, t) for n, t in pts if t >= args.floor]
        if len(used) < 3:
            print(f"{impl:<12}{len(used):>7}  {'(too few points above floor)':<16}")
            continue
        slope, intercept, r2 = fit(used)
        fits[impl] = (slope, intercept, used)
        span = f"{pow2(used[0][0])}..{pow2(used[-1][0])}"
        print(f"{impl:<12}{len(used):>7}  {span:<16}{slope:>7.2f}{r2:>8.3f}")
    print("slope k means time ~ n^k: 1 is linear, ~1.1 often n log n, 2 is quadratic.")

    if not args.no_plot:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6.4, 4.2), layout="constrained")
        for impl, pts in series.items():
            (line,) = ax.plot([n for n, _ in pts], [t for _, t in pts], "o-", label=impl, markersize=4)
            if impl in fits:
                slope, intercept, used = fits[impl]
                ns = [used[0][0], used[-1][0]]
                ax.plot(ns, [math.exp(intercept) * n**slope for n in ns], "--", color=line.get_color(), alpha=0.6,
                        label=f"{impl} fit: k={slope:.2f}")
        ax.set(xscale="log", yscale="log", xlabel="n", ylabel="seconds per call (median)",
               title=args.jsonl.parent.parent.parent.name)
        ax.axhline(args.floor, color="gray", linewidth=0.8, linestyle=":")
        ax.legend(fontsize="small")
        out = args.jsonl.with_name("scaling.png")
        fig.savefig(out, dpi=120)
        print(f"plot: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Size-sweep timing shared by every exercise's `python -m <pkg>.scale` entrypoint.

For each size n the input is generated once, outside the timed region; each
implementation is then timed `reps` times. Every sample is appended to a JSONL
file as {impl, n, seconds, rep, run, lang}. An implementation whose median
exceeds `budget` seconds is dropped from larger sizes, so a quadratic brute
force stops early while the fast implementations keep going.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import statistics
import sys
import time
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

DEFAULT_SIZES = tuple(2**k for k in range(8, 18))
IMPL_MODULES = ("mine", "brute", "reference")


def measure(f: Callable[[Any], Any], x: Any, *, min_time: float = 2e-3) -> float:
    """Seconds per call of f(x). Fast calls are batched until a sample spans min_time."""
    iters = 1
    while True:
        t0 = time.perf_counter()
        for _ in range(iters):
            f(x)
        dt = time.perf_counter() - t0
        if dt >= min_time:
            return dt / iters
        iters = max(iters * 2, int(iters * min_time / max(dt, 1e-9) * 1.2))


def run(
    impls: Mapping[str, Callable[[Any], Any]],
    generate: Callable[[int, int], Any],
    out: Path,
    *,
    lang: str,
    sizes: Iterable[int] | None = None,
    reps: int = 5,
    budget: float = 0.5,
    seed: int = 0,
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().astimezone().isoformat(timespec="seconds")
    alive = dict(impls)
    with out.open("a") as fh:
        for n in sizes or DEFAULT_SIZES:
            if not alive:
                break
            x = generate(n, seed)
            for name, f in list(alive.items()):
                samples = []
                for rep in range(reps):
                    s = measure(f, x)
                    samples.append(s)
                    record = {"impl": name, "n": n, "seconds": s, "rep": rep, "run": run_id, "lang": lang}
                    fh.write(json.dumps(record) + "\n")
                median = statistics.median(samples)
                print(f"{name:>10}  n={n:>9}  median={median:.3e}s", flush=True)
                if median > budget:
                    del alive[name]
    print(f"appended to {out}")


def discover(pkg: str, generate_module: ModuleType) -> dict[str, Callable[[Any], Any]]:
    """{name: x -> generate.call(module, x)} for each implementation module that exists in pkg."""
    impls = {}
    for name in IMPL_MODULES:
        if importlib.util.find_spec(f"{pkg}.{name}") is not None:
            module = importlib.import_module(f"{pkg}.{name}")
            impls[name] = lambda x, m=module: generate_module.call(m, x)
    return impls


def main(pkg: str, generate_module: ModuleType, default_out: Path) -> None:
    """CLI used by exercise scale modules: `python -m <pkg>.scale [OUT.jsonl]`."""
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default_out
    run(
        discover(pkg, generate_module),
        generate_module.generate,
        out,
        lang="python",
        sizes=getattr(generate_module, "SCALE_SIZES", None),
    )

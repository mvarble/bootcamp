"""Wiring: `python -m example_max_subarray.scale [OUT.jsonl]` times every implementation over a size sweep."""

from pathlib import Path

from harness.scaling import main

from . import generate

if __name__ == "__main__":
    main(__package__, generate, Path(__file__).resolve().parents[2] / ".meta" / "bench" / "scaling.jsonl")

"""Wiring: every provided/samples/*.in through shim.run, compared token-by-token with the matching .out."""

from pathlib import Path

import pytest

from {{pkg}}.shim import run

SAMPLES = sorted((Path(__file__).resolve().parents[1] / "provided" / "samples").glob("*.in"))


@pytest.mark.parametrize("sample", SAMPLES, ids=lambda p: p.stem)
def test_sample(sample):
    assert run(sample.read_text()).split() == sample.with_suffix(".out").read_text().split()

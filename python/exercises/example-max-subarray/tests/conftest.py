"""Wiring: every test that takes `impl` runs once per implementation (mine, plus reference once deepened)."""

import importlib
import importlib.util

import pytest

PKG = "example_max_subarray"
IMPLS = [name for name in ("mine", "reference") if importlib.util.find_spec(f"{PKG}.{name}")]


@pytest.fixture(scope="session", params=IMPLS)
def impl(request):
    return importlib.import_module(f"{PKG}.{request.param}")

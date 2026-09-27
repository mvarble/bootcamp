"""Workspace-wide pytest wiring.

- Hypothesis profiles: `default` for every run, `stress` for `just stress`
  (selected with `--hypothesis-profile=stress`).
- With SKIP_ATTEMPTING=1 (set in CI), exercises whose status is `attempting`
  are not collected: their stubs fail by design.
"""

import os
import tomllib
from pathlib import Path

from hypothesis import HealthCheck, settings

# importlib mode names a test module by its path from rootdir, so
# algolib/tests/test_dsu.py becomes "algolib.tests.test_dsu". If the real
# package is not imported yet, pytest registers the *directory* python/algolib/
# as a namespace package called "algolib", shadowing src/algolib. Import the
# real packages first so pytest reuses them.
import algolib  # noqa: E402, F401
import harness  # noqa: E402, F401

settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile(
    "stress",
    max_examples=3000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("default")


def pytest_ignore_collect(collection_path: Path, config) -> bool | None:
    if os.environ.get("SKIP_ATTEMPTING") != "1":
        return None
    meta = collection_path / ".meta" / "exercise.toml"
    if collection_path.parent.name == "exercises" and meta.is_file():
        if tomllib.loads(meta.read_text())["status"] == "attempting":
            return True
    return None

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

import due
import index
import meta

SCRIPTS = Path(__file__).resolve().parents[1]


@pytest.fixture
def exercises(make_exercise):
    make_exercise("python", "lc0001-two-sum", status="solved", tags=["hashing"], revisit_on="2026-01-10",
                  revisit_interval_days=14)
    make_exercise("rust", "cf1850a-critics", status="attempting")
    make_exercise("python", "example-max-subarray", status="solved", tags=["kadane"], revisit_on="2026-01-01")


def test_index_skips_examples_and_groups_by_pattern(repo, exercises):
    (repo / "README.md").write_text("# x\n\n<!-- index:start -->\nold\n<!-- index:end -->\ntail\n")
    subprocess.run([sys.executable, SCRIPTS / "index.py", "--root", repo], check=True, capture_output=True)
    text = (repo / "README.md").read_text()
    assert "example-max-subarray" not in text and "\nold\n" not in text and text.endswith("tail\n")
    lines = [line for line in text.splitlines() if line.startswith("| ") and "---" not in line][1:]
    assert [line.split(" | ")[1] for line in lines] == [
        "[lc0001-two-sum](python/exercises/lc0001-two-sum)",
        "[cf1850a-critics](rust/exercises/cf1850a-critics)",
    ]
    assert lines[0].startswith("| hashing |") and lines[1].startswith("| untagged |")


def test_index_empty(repo):
    (repo / "README.md").write_text("<!-- index:start -->\n<!-- index:end -->\n")
    assert index.render(repo) == "_No exercises yet._"


def test_due_skips_examples_and_unscheduled(repo, exercises):
    assert [path for _, path, _ in due.scheduled(repo)] == ["python/exercises/lc0001-two-sum"]
    out = subprocess.run([sys.executable, SCRIPTS / "due.py", "--root", repo, "--today", "2026-01-12"],
                         check=True, capture_output=True, text=True).stdout
    assert "due as of 2026-01-12: 1" in out and "2d overdue" in out
    out = subprocess.run([sys.executable, SCRIPTS / "due.py", "--root", repo, "--today", "2026-01-05"],
                         check=True, capture_output=True, text=True).stdout
    assert "due as of 2026-01-05: 0" in out and "in 5d" in out


def test_meta_fixture_is_isolated(repo):
    assert meta.ROOT == repo and date.today().year >= 2026


def test_scrub_bench_drops_hostname_and_paths(tmp_path):
    f = tmp_path / "gbench.json"
    f.write_text('{"context": {"host_name": "box", "executable": "/home/me/x", "num_cpus": 8}, "benchmarks": []}')
    subprocess.run([sys.executable, SCRIPTS / "scrub_bench.py", f, tmp_path / "missing.json"], check=True)
    assert json.loads(f.read_text()) == {"context": {"num_cpus": 8}, "benchmarks": []}

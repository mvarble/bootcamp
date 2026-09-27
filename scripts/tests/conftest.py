import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import meta  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """An empty fake repo root; meta.py state paths point into it."""
    monkeypatch.setattr(meta, "ROOT", tmp_path)
    monkeypatch.setattr(meta, "ACTIVE", tmp_path / ".agent" / "active")
    return tmp_path


@pytest.fixture
def make_exercise(repo):
    def make(lang="python", slug="lc0001-two-sum", **fields):
        ex = repo / lang / "exercises" / slug
        (ex / ".meta").mkdir(parents=True)
        doc = meta.new_meta(lang, "lc", "https://leetcode.com/problems/two-sum/")
        for k, v in fields.items():
            doc[k] = v
        meta.save(ex, doc)
        return ex

    return make

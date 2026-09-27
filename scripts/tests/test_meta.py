from datetime import date

import pytest

import meta


@pytest.mark.parametrize(
    ("previous", "cold", "expected"),
    [(0, True, 14), (0, False, 14), (14, True, 28), (28, True, 56), (56, False, 14), (14, False, 14)],
)
def test_next_interval(previous, cold, expected):
    assert meta.next_interval(previous, cold) == expected


def test_first_cold_solve_schedules_14_days():
    doc = meta.new_meta("python", "lc", "")
    meta.mark_done(doc, 20, date(2026, 1, 1))
    assert (doc["status"], doc["minutes"], doc["solved_cold"]) == ("solved", 20, True)
    assert (doc["revisit_interval_days"], doc["revisit_on"]) == (14, "2026-01-15")


def test_cold_resolve_doubles_and_hinted_resolve_resets():
    doc = meta.new_meta("python", "lc", "")
    meta.mark_done(doc, 20, date(2026, 1, 1))
    meta.mark_revisit(doc)
    assert (doc["status"], doc["solved_cold"], doc["hints_used"]) == ("attempting", False, 0)
    meta.mark_done(doc, 10, date(2026, 1, 15))
    assert (doc["revisit_interval_days"], doc["revisit_on"]) == (28, "2026-02-12")
    meta.mark_revisit(doc)
    doc["hints_used"] = 1
    meta.mark_done(doc, 30, date(2026, 2, 12))
    assert (doc["solved_cold"], doc["revisit_interval_days"], doc["revisit_on"]) == (False, 14, "2026-02-26")


def test_done_requires_attempting():
    doc = meta.new_meta("python", "lc", "")
    doc["status"] = "solved"
    with pytest.raises(meta.GateError):
        meta.mark_done(doc, 1, date(2026, 1, 1))


def test_done_minutes_default_to_wall_time_since_start():
    doc = meta.new_meta("python", "lc", "")
    doc["started"] = "2000-01-01T00:00:00+00:00"
    meta.mark_done(doc, None, date(2026, 1, 1))
    assert doc["minutes"] > 60 * 24 * 365


@pytest.mark.parametrize(
    ("skill", "status", "tier", "ok"),
    [
        ("hint", "attempting", "quick", True),
        ("hint", "solved", "quick", False),
        ("assess", "solved", "quick", True),
        ("assess", "attempting", "quick", False),
        ("reference", "solved", "deep", True),
        ("reference", "solved", "quick", False),
        ("compare", "referenced", "deep", True),
        ("compare", "solved", "deep", False),
        ("review", "referenced", "deep", True),
        ("review", "solved", "quick", True),
        ("review", "reviewed", "quick", False),
    ],
)
def test_gate_matrix(skill, status, tier, ok):
    doc = meta.new_meta("python", "lc", "")
    doc["status"], doc["tier"] = status, tier
    if ok:
        meta.check_gate(skill, doc)
    else:
        with pytest.raises(meta.GateError):
            meta.check_gate(skill, doc)


def test_status_transitions():
    doc = meta.new_meta("python", "lc", "")
    doc["status"] = "solved"
    with pytest.raises(meta.GateError):
        meta.set_status(doc, "referenced")  # quick tier
    doc["tier"] = "deep"
    meta.set_status(doc, "referenced")
    meta.set_status(doc, "reviewed")
    with pytest.raises(meta.GateError):
        meta.set_status(doc, "reviewed")
    with pytest.raises(meta.GateError):
        meta.set_status(doc, "solved")


def test_gate_cli_exit_codes(make_exercise, capsys):
    assert meta.main(["gate", "hint"]) == meta.GATE_FAILED  # nothing active
    ex = make_exercise()
    assert meta.main(["activate", str(ex)]) == 0
    assert meta.main(["gate", "hint"]) == 0
    assert meta.main(["gate", "assess"]) == meta.GATE_FAILED
    assert meta.main(["gate", "due"]) == 0
    assert "needs status solved" in capsys.readouterr().err


def test_record_hint_appends_numbered_entries(make_exercise, monkeypatch):
    ex = make_exercise()
    meta.main(["activate", str(ex)])
    for text in ("first nudge", "second: prefix sums"):
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(text))
        assert meta.main(["record-hint"]) == 0
    hints = (ex / "analysis" / "hints.md").read_text()
    assert "## Hint 1 (nudge)" in hints and "## Hint 2 (technique)" in hints
    assert meta.load(ex)["hints_used"] == 2
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("x"))
    assert meta.main(["record-hint", "--level", "1"]) == meta.GATE_FAILED  # next is level 3


def test_hint_materials_exclude_reference_and_other_analysis(make_exercise):
    ex = make_exercise()
    pkg = ex / "src" / "lc0001_two_sum"
    pkg.mkdir(parents=True)
    for name in ("mine.py", "brute.py", "generate.py", "reference.py", "scale.py"):
        (pkg / name).write_text(f"# {name}\n")
    (ex / "tests").mkdir()
    (ex / "tests" / "test_cases.py").write_text("# cases\n")
    (ex / "tests" / "conftest.py").write_text("# wiring\n")
    (ex / "analysis").mkdir()
    (ex / "analysis" / "assessment.md").write_text("SPOILER\n")
    (ex / "analysis" / "hints.md").write_text("# Hints\n")
    (ex / "README.md").write_text("# readme\n")
    text = meta.hint_materials(ex, meta.load(ex))
    for present in ("mine.py", "brute.py", "generate.py", "test_cases.py", "README.md", "hints.md"):
        assert present in text
    for absent in ("reference.py", "scale.py", "conftest.py", "SPOILER"):
        assert absent not in text


def test_attempting_lists_slugs(make_exercise, capsys):
    make_exercise(slug="lc0001-a")
    make_exercise(slug="lc0002-b", status="solved")
    assert meta.main(["attempting", "python"]) == 0
    assert capsys.readouterr().out.strip() == "lc0001-a"

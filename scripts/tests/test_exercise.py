import pytest

import exercise
import meta


@pytest.fixture
def fake_repo(repo, monkeypatch):
    monkeypatch.setattr(exercise, "ROOT", repo)
    return repo


@pytest.mark.parametrize("lang", meta.LANGS)
@pytest.mark.parametrize("slug", ["lc0001-two-sum", "cf1850a-to-my-critics"])
def test_new_renders_variant_without_placeholders(fake_repo, lang, slug):
    assert exercise.main(["new", lang, slug]) == 0
    ex = fake_repo / lang / "exercises" / slug
    files = [p for p in ex.rglob("*") if p.is_file()]
    assert all("@lc" not in str(p) and "@cf" not in str(p) and "{{" not in str(p) for p in files)
    assert all("{{" not in p.read_text() for p in files)
    is_cf = slug.startswith("cf")
    assert any(p.name.startswith("shim.") for p in files) == is_cf
    assert (ex / "provided" / "samples").is_dir() == is_cf
    doc = meta.load(ex)
    assert (doc["source"], doc["lang"], doc["tier"], doc["status"]) == ("cf" if is_cf else "lc", lang, "quick", "attempting")
    assert exercise.stub_path(ex, lang).read_text() == exercise.mine_path(ex, lang).read_text()


@pytest.mark.parametrize("slug", ["1two-sum", "Two-Sum", "two_sum", "two--sum", "two-"])
def test_new_rejects_bad_slugs(fake_repo, slug):
    assert exercise.main(["new", "python", slug]) == 2


@pytest.mark.parametrize("lang", meta.LANGS)
def test_deepen_adds_reference_and_rewires(fake_repo, lang):
    exercise.main(["new", lang, "lc0001-two-sum"])
    ex = fake_repo / lang / "exercises" / "lc0001-two-sum"
    assert exercise.main(["deepen", str(ex)]) == 0
    assert meta.load(ex)["tier"] == "deep"
    assert (ex / "analysis" / "README.md").is_file()
    assert any(p.name.startswith("reference.") for p in ex.rglob("*"))
    if lang == "rust":
        assert "wire!(mine, reference, brute);" in (ex / "src" / "lib.rs").read_text()
        assert "suite!(reference);" in (ex / "tests" / "suite.rs").read_text()
        assert "[[bench]]" in (ex / "Cargo.toml").read_text()
    if lang == "cpp":
        assert "DEEP)" in (ex / "CMakeLists.txt").read_text()
        assert "reference::Solution" in (ex / "impls.hpp").read_text()
    assert exercise.main(["deepen", str(ex)]) == 2  # already deep


def test_stub_refuses_solved_mine_and_revisit_restores_it(fake_repo):
    exercise.main(["new", "python", "lc0001-two-sum"])
    ex = fake_repo / "python" / "exercises" / "lc0001-two-sum"
    mine = exercise.mine_path(ex, "python")
    mine.write_text(mine.read_text().replace("def solve(self, nums: List[int])", "def twoSum(self, nums: List[int])"))
    assert exercise.main(["stub", str(ex)]) == 0
    stub = mine.read_text()
    mine.write_text("class Solution:\n    def twoSum(self, nums):\n        return [0, 1]\n")
    assert exercise.main(["stub", str(ex)]) == 2  # solved: no sentinel
    assert exercise.main(["revisit", str(ex)]) == 2  # still attempting
    doc = meta.load(ex)
    meta.mark_done(doc, 5, __import__("datetime").date(2026, 1, 1))
    meta.save(ex, doc)
    assert exercise.main(["revisit", str(ex)]) == 0
    assert mine.read_text() == stub
    archived = list((ex / ".meta" / "attempts").iterdir())
    assert len(archived) == 1 and "return [0, 1]" in archived[0].read_text()
    assert meta.load(ex)["status"] == "attempting"

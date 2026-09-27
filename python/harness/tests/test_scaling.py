import json

from harness.scaling import measure, run


def test_measure_batches_fast_calls():
    assert 0 < measure(lambda x: x, 1, min_time=1e-4) < 1e-3


def test_run_writes_one_record_per_rep_and_drops_slow_impls(tmp_path):
    out = tmp_path / "bench" / "scaling.jsonl"
    impls = {"fast": lambda x: sum(x), "slow": lambda x: sum(x) + sum(range(10**6))}
    run(impls, lambda n, seed: list(range(n)), out, lang="python", sizes=[4, 8], reps=2, budget=1e-4)
    records = [json.loads(line) for line in out.read_text().splitlines()]
    assert {r["impl"] for r in records if r["n"] == 4} == {"fast", "slow"}
    assert {r["impl"] for r in records if r["n"] == 8} == {"fast"}
    assert set(records[0]) == {"impl", "n", "seconds", "rep", "run", "lang"}
    assert all(r["seconds"] > 0 for r in records)

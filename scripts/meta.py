#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["tomlkit==0.15.1"]
# ///
"""Exercise state: status machine, skill gates, hint log, done/revisit scheduling.

Every change to <exercise>/.meta/exercise.toml goes through this script (AGENTS.md §2).
Commands act on the active exercise (.agent/active) unless --path is given.

  meta.py gate <skill>              check a skill's gate; print context (exit 3 if it fails)
  meta.py activate <path>           make <path> active; ensure `started` for an attempt
  meta.py record-hint [--level N]   append stdin as the next hint in analysis/hints.md; hints_used += 1
  meta.py done [--minutes N]        attempting -> solved; minutes, solved_cold, revisit schedule
  meta.py set-status <status>       solved -> referenced (deep) | solved/referenced -> reviewed
  meta.py tags <tag>...             replace the tag list (used by /review for patterns)
  meta.py show                      print exercise.toml
  meta.py attempting <lang>         slugs whose status is `attempting` (CI exclusion)
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import tomlkit

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / ".agent" / "active"
LANGS = ("python", "rust", "cpp")
FIRST_INTERVAL_DAYS = 14
HINT_LEVELS = {1: "nudge", 2: "technique", 3: "structural outline"}
GATE_FAILED = 3  # >= 2 so an injected `!` command aborts the skill (exit 1 is tolerated for some commands)

# skill -> (allowed statuses or None for no status gate, required tier or None)
GATES: dict[str, tuple[set[str] | None, str | None]] = {
    "start": (None, None),
    "hint": ({"attempting"}, None),
    "done": ({"attempting"}, None),
    "assess": ({"solved"}, None),
    "reference": ({"solved"}, "deep"),
    "compare": ({"referenced"}, None),
    "review": ({"solved", "referenced"}, None),
    "due": (None, None),
}

# Where each language keeps the files a hint may read (besides README.md and provided/).
OWNED_STEMS = ("mine", "brute", "generate", "shim")


class GateError(Exception):
    pass


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today() -> date:
    return date.today()


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def exercise_dir(path: str | Path | None) -> Path:
    """Resolve --path, or the active exercise, to an absolute exercise directory."""
    if path is None:
        if not ACTIVE.is_file() or not ACTIVE.read_text().strip():
            raise GateError("no active exercise: run /start (or `meta.py activate <path>`) first")
        path = ACTIVE.read_text().strip()
    p = Path(path)
    if not p.is_absolute():
        p = Path.cwd() / p if (Path.cwd() / p).is_dir() else ROOT / p
    p = p.resolve()
    parts = p.relative_to(ROOT).parts if p.is_relative_to(ROOT) else ()
    if len(parts) != 3 or parts[0] not in LANGS or parts[1] != "exercises":
        raise GateError(f"not an exercise directory: {path} (expected <lang>/exercises/<slug>)")
    if not (p / ".meta" / "exercise.toml").is_file():
        raise GateError(f"missing {rel(p)}/.meta/exercise.toml")
    return p


def load(ex: Path) -> tomlkit.TOMLDocument:
    return tomlkit.parse((ex / ".meta" / "exercise.toml").read_text())


def save(ex: Path, doc: tomlkit.TOMLDocument) -> None:
    (ex / ".meta" / "exercise.toml").write_text(tomlkit.dumps(doc))


def new_meta(lang: str, source: str, url: str) -> tomlkit.TOMLDocument:
    doc = tomlkit.document()
    doc.add(tomlkit.comment("Exercise state. Agents change it only via scripts/meta.py; `tags` is fine to edit by hand."))
    for key, value in {
        "source": source,
        "url": url,
        "lang": lang,
        "tier": "quick",
        "status": "attempting",
        "tags": [],
        "started": now(),
        "minutes": 0,
        "hints_used": 0,
        "solved_cold": False,
        "revisit_on": "",
        "revisit_interval_days": 0,
    }.items():
        doc[key] = value
    return doc


def check_gate(skill: str, doc: tomlkit.TOMLDocument) -> None:
    if skill not in GATES:
        raise GateError(f"unknown skill {skill!r}; known: {', '.join(GATES)}")
    statuses, tier = GATES[skill]
    if statuses is not None and doc["status"] not in statuses:
        need = " or ".join(sorted(statuses))
        raise GateError(f"/{skill} needs status {need}; this exercise is {doc['status']!r}")
    if tier is not None and doc["tier"] != tier:
        raise GateError(f"/{skill} needs tier {tier!r}; this exercise is {doc['tier']!r} (run `just deepen <path>`)")


def next_interval(previous_days: int, solved_cold: bool) -> int:
    """First solve: 14 days. Re-solve: double after a cold solve, back to 14 otherwise."""
    if previous_days <= 0:
        return FIRST_INTERVAL_DAYS
    return previous_days * 2 if solved_cold else FIRST_INTERVAL_DAYS


def mark_done(doc: tomlkit.TOMLDocument, minutes: int | None, on: date) -> None:
    if doc["status"] != "attempting":
        raise GateError(f"done needs status 'attempting'; this exercise is {doc['status']!r}")
    if minutes is None:
        started = datetime.fromisoformat(str(doc["started"])) if doc["started"] else None
        minutes = math.ceil((datetime.now().astimezone() - started).total_seconds() / 60) if started else 0
    cold = int(doc["hints_used"]) == 0
    interval = next_interval(int(doc["revisit_interval_days"]), cold)
    doc["minutes"] = minutes
    doc["solved_cold"] = cold
    doc["revisit_interval_days"] = interval
    doc["revisit_on"] = (on + timedelta(days=interval)).isoformat()
    doc["status"] = "solved"


def mark_revisit(doc: tomlkit.TOMLDocument) -> None:
    """A cold re-solve starts: back to attempting, fresh hint count and clock."""
    doc["status"] = "attempting"
    doc["solved_cold"] = False
    doc["hints_used"] = 0
    doc["started"] = now()


def set_status(doc: tomlkit.TOMLDocument, status: str) -> None:
    current = doc["status"]
    if status == "referenced":
        if doc["tier"] != "deep" or current != "solved":
            raise GateError(f"referenced needs tier 'deep' and status 'solved' (have {doc['tier']!r}, {current!r})")
    elif status == "reviewed":
        if current not in ("solved", "referenced"):
            raise GateError(f"reviewed needs status 'solved' or 'referenced' (have {current!r})")
    else:
        raise GateError(f"set-status only handles referenced/reviewed; use activate/done/revisit for {status!r}")
    doc["status"] = status


def owned_files(ex: Path) -> list[Path]:
    """README, provided/, mine/brute/generate/shim, and my test cases: everything a hint may read."""
    files = [ex / "README.md"] if (ex / "README.md").is_file() else []
    files += sorted(p for p in (ex / "provided").rglob("*") if p.is_file())
    for p in sorted(ex.rglob("*")):
        if not p.is_file() or {".meta", "analysis", "provided", "__pycache__"} & set(p.relative_to(ex).parts):
            continue
        if p.name.split(".")[0] in OWNED_STEMS:
            files.append(p)
        elif p.relative_to(ex).parts[0] == "tests" and "cases" in p.relative_to(ex / "tests").as_posix():
            files.append(p)
    return files


def hint_materials(ex: Path, doc: tomlkit.TOMLDocument) -> str:
    level = min(int(doc["hints_used"]) + 1, 3)
    out = [f"next hint: level {level} ({HINT_LEVELS[level]})"]
    hints = ex / "analysis" / "hints.md"
    for p in owned_files(ex) + ([hints] if hints.is_file() else []):
        out.append(f"\n===== {rel(p)} =====\n{p.read_text()}")
    return "\n".join(out)


def context_lines(ex: Path, doc: tomlkit.TOMLDocument) -> str:
    return (
        f"exercise: {rel(ex)}\n"
        f"lang: {doc['lang']}  source: {doc['source']}  tier: {doc['tier']}  status: {doc['status']}\n"
        f"hints_used: {doc['hints_used']}  minutes: {doc['minutes']}  solved_cold: {str(doc['solved_cold']).lower()}\n"
        f"revisit_on: {doc['revisit_on'] or '-'}  interval: {doc['revisit_interval_days']}d  url: {doc['url'] or '-'}"
    )


def cmd_gate(args: argparse.Namespace) -> None:
    if args.skill not in GATES:
        raise GateError(f"unknown skill {args.skill!r}; known: {', '.join(GATES)}")
    if GATES[args.skill] == (None, None):
        print(f"gate ok: /{args.skill} (no gate)")
        return
    ex = exercise_dir(args.path)
    doc = load(ex)
    check_gate(args.skill, doc)
    print(f"gate ok: /{args.skill}\n{context_lines(ex, doc)}")
    if args.skill == "hint":
        print("\n" + hint_materials(ex, doc))


def cmd_activate(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path_arg)
    doc = load(ex)
    if args.url and not doc["url"]:
        doc["url"] = args.url
    if doc["status"] == "attempting" and not doc["started"]:
        doc["started"] = now()
    save(ex, doc)
    ACTIVE.parent.mkdir(exist_ok=True)
    ACTIVE.write_text(rel(ex) + "\n")
    print(f"active: {rel(ex)}\n{context_lines(ex, doc)}")
    if doc["status"] != "attempting":
        print(f"note: status is {doc['status']!r}; `just revisit {rel(ex)}` starts a cold re-solve")


def cmd_record_hint(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path)
    doc = load(ex)
    check_gate("hint", doc)
    level = min(int(doc["hints_used"]) + 1, 3)
    if args.level is not None and args.level != level:
        raise GateError(f"expected hint level {level}, got {args.level}")
    text = sys.stdin.read().strip()
    if not text:
        raise GateError("empty hint on stdin")
    hints = ex / "analysis" / "hints.md"
    hints.parent.mkdir(exist_ok=True)
    number = int(doc["hints_used"]) + 1
    header = "" if hints.is_file() else f"# Hints for {ex.name}\n"
    entry = f"\n## Hint {number} ({HINT_LEVELS[level]}) {today().isoformat()}\n\n{text}\n"
    with hints.open("a") as fh:
        fh.write(header + entry)
    doc["hints_used"] = number
    save(ex, doc)
    print(f"recorded hint {number} (level {level}) in {rel(hints)}")


def cmd_done(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path)
    doc = load(ex)
    mark_done(doc, args.minutes, today())
    save(ex, doc)
    print(f"solved\n{context_lines(ex, doc)}")


def cmd_set_status(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path)
    doc = load(ex)
    set_status(doc, args.status)
    save(ex, doc)
    print(f"status: {args.status}\n{context_lines(ex, doc)}")


def cmd_tags(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path)
    doc = load(ex)
    doc["tags"] = sorted(set(args.tags))
    save(ex, doc)
    print(f"tags: {', '.join(doc['tags'])}")


def cmd_show(args: argparse.Namespace) -> None:
    ex = exercise_dir(args.path)
    print((ex / ".meta" / "exercise.toml").read_text(), end="")


def cmd_attempting(args: argparse.Namespace) -> None:
    import tomllib

    slugs = []
    for meta in sorted((ROOT / args.lang / "exercises").glob("*/.meta/exercise.toml")):
        if tomllib.loads(meta.read_text())["status"] == "attempting":
            slugs.append(meta.parents[1].name)
    print(" ".join(slugs))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def command(name: str, fn, *, path: bool = True) -> argparse.ArgumentParser:
        p = sub.add_parser(name)
        if path:
            p.add_argument("--path", help="exercise dir (default: .agent/active)")
        p.set_defaults(fn=fn)
        return p

    command("gate", cmd_gate).add_argument("skill")
    p = command("activate", cmd_activate, path=False)
    p.add_argument("path_arg", metavar="path")
    p.add_argument("--url", default="")
    command("record-hint", cmd_record_hint).add_argument("--level", type=int)
    command("done", cmd_done).add_argument("--minutes", type=int)
    command("set-status", cmd_set_status).add_argument("status")
    command("tags", cmd_tags).add_argument("tags", nargs="+")
    command("show", cmd_show)
    command("attempting", cmd_attempting, path=False).add_argument("lang", choices=LANGS)

    args = parser.parse_args(argv)
    try:
        args.fn(args)
    except GateError as e:
        print(f"gate failed: {e}", file=sys.stderr)
        return GATE_FAILED
    return 0


if __name__ == "__main__":
    sys.exit(main())

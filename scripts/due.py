#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""List exercises due for a cold re-solve (revisit_on <= today), plus the next week's.

usage: due.py [--root DIR] [--today YYYY-MM-DD] [--ahead DAYS]

`example-*` exercises are left out. Start a re-solve with `just revisit <path>`.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from datetime import date, timedelta
from pathlib import Path


def scheduled(root: Path) -> list[tuple[date, str, dict]]:
    out = []
    for meta in sorted(root.glob("*/exercises/*/.meta/exercise.toml")):
        ex = meta.parents[1]
        m = tomllib.loads(meta.read_text())
        if ex.name.startswith("example-") or not m.get("revisit_on"):
            continue
        out.append((date.fromisoformat(m["revisit_on"]), ex.relative_to(root).as_posix(), m))
    return sorted(out, key=lambda e: (e[0], e[1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--today", type=date.fromisoformat, default=date.today())
    ap.add_argument("--ahead", type=int, default=7)
    args = ap.parse_args()

    entries = scheduled(args.root)
    due = [e for e in entries if e[0] <= args.today]
    soon = [e for e in entries if args.today < e[0] <= args.today + timedelta(days=args.ahead)]

    def show(items: list[tuple[date, str, dict]]) -> None:
        for when, path, m in items:
            delta = (args.today - when).days
            age = f"{delta}d overdue" if delta > 0 else ("today" if delta == 0 else f"in {-delta}d")
            tags = ",".join(m.get("tags", [])) or "untagged"
            print(f"  {when}  {age:<12} {path}  [{m['status']}, {tags}, interval {m['revisit_interval_days']}d]")

    print(f"due as of {args.today}: {len(due)}")
    show(due)
    print(f"coming up in {args.ahead}d: {len(soon)}")
    show(soon)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Rebuild the exercise table in the root README from every <lang>/exercises/*/.meta/exercise.toml.

usage: index.py [--root DIR]

Rows are grouped by first tag (the pattern), then slug. `example-*` exercises
are scaffolding demos and are left out. Only the text between the
<!-- index:start --> and <!-- index:end --> markers is replaced.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

START, END = "<!-- index:start -->", "<!-- index:end -->"
HEADER = "| Pattern | Exercise | Lang | Source | Tier | Status | Min | Hints | Cold | Revisit |\n|---|---|---|---|---|---|---|---|---|---|"


def rows(root: Path) -> list[str]:
    entries = []
    for meta in sorted(root.glob("*/exercises/*/.meta/exercise.toml")):
        ex = meta.parents[1]
        if ex.name.startswith("example-"):
            continue
        m = tomllib.loads(meta.read_text())
        tags = list(m.get("tags", []))
        pattern = tags[0] if tags else "untagged"
        source = f"[{m['source']}]({m['url']})" if m.get("url") else m["source"]
        cold = "yes" if m.get("solved_cold") else "no"
        rel = ex.relative_to(root).as_posix()
        cells = [
            pattern if not tags[1:] else f"{pattern} ({', '.join(tags[1:])})",
            f"[{ex.name}]({rel})",
            m["lang"],
            source,
            m["tier"],
            m["status"],
            str(m.get("minutes", 0)),
            str(m.get("hints_used", 0)),
            cold if m["status"] != "attempting" else "-",
            m.get("revisit_on") or "-",
        ]
        entries.append(((pattern == "untagged", pattern, ex.name, m["lang"]), "| " + " | ".join(cells) + " |"))
    return [line for _, line in sorted(entries)]


def render(root: Path) -> str:
    body = rows(root)
    return HEADER + "\n" + "\n".join(body) if body else "_No exercises yet._"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    readme = args.root / "README.md"
    text = readme.read_text()
    if START not in text or END not in text:
        sys.exit(f"{readme}: missing {START} / {END} markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    table = render(args.root)
    readme.write_text(f"{head}{START}\n{table}\n{END}{tail}")
    print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())

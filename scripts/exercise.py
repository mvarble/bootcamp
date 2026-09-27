#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["tomlkit==0.15.1"]
# ///
"""Exercise files: scaffold from templates, deepen, revisit, snapshot the stub.

  exercise.py new <lang> <slug> [--source lc|cf] [--url URL]
  exercise.py deepen <path>
  exercise.py revisit <path>
  exercise.py stub <path>

Templates live in templates/{common,<lang>}/{quick,deep}/. Path components may
contain {{pkg}}; a component tagged @lc or @cf is used only for that source.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import meta

ROOT = meta.ROOT
TEMPLATES = ROOT / "templates"
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
VARIANT_RE = re.compile(r"@(lc|cf)")
MINE = {"python": "src/{pkg}/mine.py", "rust": "src/mine.rs", "cpp": "mine.hpp"}
# `just stub` refuses to snapshot a mine that no longer contains its language's not-implemented marker.
STUB_SENTINEL = {"python": "NotImplementedError", "rust": "todo!(", "cpp": "not implemented"}


class Refused(Exception):
    pass


def pkg_of(slug: str) -> str:
    return slug.replace("-", "_")


def substitute(text: str, subs: dict[str, str]) -> str:
    for key, value in subs.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def render(src: Path, dest: Path, source: str, subs: dict[str, str]) -> list[Path]:
    """Copy a template tree into dest, choosing @lc/@cf variants and filling placeholders."""
    written = []
    if not src.is_dir():
        return written
    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        parts = []
        for part in f.relative_to(src).parts:
            m = VARIANT_RE.search(part)
            if m and m.group(1) != source:
                break
            parts.append(substitute(VARIANT_RE.sub("", part), subs))
        else:
            out = dest.joinpath(*parts)
            if out.exists():
                raise Refused(f"refusing to overwrite {meta.rel(out)}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(substitute(f.read_text(), subs))
            written.append(out)
    return written


def mine_path(ex: Path, lang: str) -> Path:
    return ex / MINE[lang].format(pkg=pkg_of(ex.name))


def stub_path(ex: Path, lang: str) -> Path:
    return ex / ".meta" / ("stub" + mine_path(ex, lang).suffix)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise Refused(f"{meta.rel(path)}: expected exactly one {old!r} (was the wiring edited by hand?)")
    path.write_text(text.replace(old, new))


def cmd_new(args: argparse.Namespace) -> None:
    lang, slug = args.lang, args.slug
    if not SLUG_RE.match(slug):
        raise Refused(f"bad slug {slug!r}: lowercase words joined by '-', starting with a letter (lc0053-maximum-subarray)")
    source = args.source or ("cf" if re.match(r"^cf\d", slug) else "lc")
    ex = ROOT / lang / "exercises" / slug
    if ex.exists():
        raise Refused(f"{meta.rel(ex)} already exists")
    subs = {
        "slug": slug,
        "pkg": pkg_of(slug),
        "source": source,
        "url": args.url,
        "link": f"[{source}]({args.url})" if args.url else source,
    }
    written = render(TEMPLATES / "common" / "quick", ex, source, subs)
    written += render(TEMPLATES / lang / "quick", ex, source, subs)
    (ex / ".meta").mkdir()
    meta.save(ex, meta.new_meta(lang, source, args.url))
    shutil.copyfile(mine_path(ex, lang), stub_path(ex, lang))
    print(f"created {meta.rel(ex)} ({lang}, {source}, quick tier): {len(written)} files")
    print("next: paraphrase the problem in README.md, paste the verbatim stub/samples into provided/,")
    print(f"      put the real signature in mine and brute, then `just stub {meta.rel(ex)}`")


def cmd_deepen(args: argparse.Namespace) -> None:
    ex = meta.exercise_dir(args.path)
    doc = meta.load(ex)
    if doc["tier"] == "deep":
        raise Refused(f"{meta.rel(ex)} is already deep tier")
    lang, source = str(doc["lang"]), str(doc["source"])
    subs = {"slug": ex.name, "pkg": pkg_of(ex.name), "source": source, "url": str(doc["url"])}
    written = render(TEMPLATES / "common" / "deep", ex, source, subs)
    written += render(TEMPLATES / lang / "deep", ex, source, subs)
    if lang == "rust":
        replace_once(ex / "src" / "lib.rs", "pub mod mine;\n", "pub mod mine;\npub mod reference;\n")
        replace_once(ex / "src" / "lib.rs", "wire!(mine, brute);", "wire!(mine, reference, brute);")
        replace_once(ex / "tests" / "suite.rs", "suite!(mine);\n", "suite!(mine);\nsuite!(reference);\n")
        cargo = ex / "Cargo.toml"
        replace_once(cargo, "proptest.workspace = true\n", "proptest.workspace = true\ncriterion.workspace = true\n")
        cargo.write_text(cargo.read_text() + '\n[[bench]]\nname = "impls"\nharness = false\n')
    elif lang == "cpp":
        cmake = ex / "CMakeLists.txt"
        text = cmake.read_text()
        if len(re.findall(r"bootcamp_exercise\(([^)]*)\)", text)) != 1:
            raise Refused(f"{meta.rel(cmake)}: expected one bootcamp_exercise(...) call")
        cmake.write_text(re.sub(r"bootcamp_exercise\(([^)]*)\)", r"bootcamp_exercise(\1 DEEP)", text))
        impls = ex / "impls.hpp"
        replace_once(impls, '#include "mine.hpp"\n', '#include "mine.hpp"\n#include "reference.hpp"\n')
        replace_once(impls, "TypeList<mine::Solution>", "TypeList<mine::Solution, reference::Solution>")
        replace_once(impls, 'kImplNames{"mine"}', 'kImplNames{"mine", "reference"}')
    doc["tier"] = "deep"
    meta.save(ex, doc)
    print(f"deepened {meta.rel(ex)}: {len(written)} new files; reference re-exports mine until /reference")


def cmd_revisit(args: argparse.Namespace) -> None:
    ex = meta.exercise_dir(args.path)
    doc = meta.load(ex)
    if doc["status"] == "attempting":
        raise Refused(f"{meta.rel(ex)} is already attempting")
    lang = str(doc["lang"])
    mine, stub = mine_path(ex, lang), stub_path(ex, lang)
    attempts = ex / ".meta" / "attempts"
    attempts.mkdir(exist_ok=True)
    archive = attempts / f"{date.today().isoformat()}{mine.suffix}"
    n = 2
    while archive.exists():
        archive = attempts / f"{date.today().isoformat()}-{n}{mine.suffix}"
        n += 1
    shutil.copyfile(mine, archive)
    shutil.copyfile(stub, mine)
    meta.mark_revisit(doc)
    meta.save(ex, doc)
    print(f"archived {meta.rel(mine)} -> {meta.rel(archive)}; reset to {meta.rel(stub)}; status attempting")


def cmd_stub(args: argparse.Namespace) -> None:
    ex = meta.exercise_dir(args.path)
    lang = str(meta.load(ex)["lang"])
    mine = mine_path(ex, lang)
    if STUB_SENTINEL[lang] not in mine.read_text():
        raise Refused(f"{meta.rel(mine)} has no {STUB_SENTINEL[lang]!r} marker; it looks solved, so not snapshotting it")
    shutil.copyfile(mine, stub_path(ex, lang))
    print(f"stub snapshot: {meta.rel(mine)} -> {meta.rel(stub_path(ex, lang))}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new")
    p.add_argument("lang", choices=meta.LANGS)
    p.add_argument("slug")
    p.add_argument("--source", choices=("lc", "cf"))
    p.add_argument("--url", default="")
    p.set_defaults(fn=cmd_new)
    for name, fn in (("deepen", cmd_deepen), ("revisit", cmd_revisit), ("stub", cmd_stub)):
        p = sub.add_parser(name)
        p.add_argument("path")
        p.set_defaults(fn=fn)
    args = parser.parse_args(argv)
    try:
        args.fn(args)
    except (Refused, meta.GateError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

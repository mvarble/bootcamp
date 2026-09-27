#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Remove machine-identifying fields from benchmark JSON before it is committed.

usage: scrub_bench.py FILE.json...

pytest-benchmark records the hostname (machine_info.node) and Google Benchmark
records the hostname and the executable's absolute path (context.host_name,
context.executable). The repo is public, so `just bench` drops those. CPU model
and OS version are kept: they are what make the numbers interpretable.
"""

import json
import sys
from pathlib import Path

PRIVATE_KEYS = {"node", "host_name", "executable"}


def scrub(value):
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k not in PRIVATE_KEYS}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


for name in sys.argv[1:]:
    path = Path(name)
    if path.is_file():
        path.write_text(json.dumps(scrub(json.loads(path.read_text())), indent=4) + "\n")

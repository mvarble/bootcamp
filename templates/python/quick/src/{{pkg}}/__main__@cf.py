"""Wiring: the Codeforces-style entry point, `python -m {{pkg}} < input`."""

import sys

from .shim import run

sys.stdout.write(run(sys.stdin.read()))

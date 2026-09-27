"""Parse the input text, solve with mine, and format the answer."""

from . import mine


def run(text: str) -> str:
    tokens = text.split()
    raise NotImplementedError(f"parse {len(tokens)} tokens, call {mine.solve.__name__}, format")

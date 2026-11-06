"""Module 3: Text normalization / case folding."""
from __future__ import annotations

import unicodedata
from typing import Iterable, List

_APOSTROPHES = str.maketrans("", "", "'\u2019")


def normalize(token: str, strip_accents: bool = True) -> str:
    """Case-fold, Unicode-normalize, optionally strip accents and apostrophes.

    The '*' wildcard character passes through untouched.
    """
    token = unicodedata.normalize("NFKD", token).casefold()
    if strip_accents:
        token = "".join(c for c in token if not unicodedata.combining(c))
    token = unicodedata.normalize("NFKC", token)
    return token.translate(_APOSTROPHES)


def normalize_tokens(tokens: Iterable[str]) -> List[str]:
    """Normalize a sequence of tokens, dropping any that become empty."""
    return [n for n in (normalize(t) for t in tokens) if n]

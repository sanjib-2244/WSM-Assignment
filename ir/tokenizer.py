"""Module 2: Tokenization (splits raw text into word tokens, no normalization)."""
from __future__ import annotations

import re
from typing import List

# Words may contain internal apostrophes: don't, O'Brien.
_WORD = re.compile(r"\w+(?:['\u2019]\w+)*")
# Query mode additionally keeps '*' wildcard characters inside a token.
_WORD_WILDCARD = re.compile(r"[\w*]+(?:['\u2019][\w*]+)*")


def tokenize(text: str, keep_wildcards: bool = False) -> List[str]:
    """Split `text` into tokens. Set keep_wildcards=True for query terms."""
    pattern = _WORD_WILDCARD if keep_wildcards else _WORD
    return pattern.findall(text)

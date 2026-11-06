"""Module 6: Wildcard processing using a permuterm index.

Every term t is stored as all rotations of t + '$'. A pattern is rotated so
that its last '*' is at the end, turning it into a prefix lookup (binary
search). Patterns with several '*' are post-filtered with a regex.
"""
from __future__ import annotations

import re
from bisect import bisect_left
from typing import Iterable, List, Set, Tuple


class PermutermIndex:
    def __init__(self, vocabulary: Iterable[str]) -> None:
        vocab = set(vocabulary)
        entries: List[Tuple[str, str]] = []
        for term in vocab:
            s = term + "$"
            for i in range(len(s)):
                entries.append((s[i:] + s[:i], term))
        entries.sort()
        self._keys = [k for k, _ in entries]
        self._terms = [t for _, t in entries]
        self._all_terms = vocab

    @staticmethod
    def is_wildcard(pattern: str) -> bool:
        return "*" in pattern

    def expand(self, pattern: str) -> Set[str]:
        """Return all vocabulary terms matching `pattern` ('*' = any chars)."""
        if "*" not in pattern:
            return {pattern} if pattern in self._all_terms else set()
        if pattern.strip("*") == "":
            return set(self._all_terms)

        q = pattern + "$"
        last = q.rindex("*")
        rotated = q[last + 1:] + q[:last + 1]       # last '*' now at the end
        prefix = rotated[:rotated.index("*")]        # literal part before first '*'

        regex = re.compile(".*".join(re.escape(p) for p in pattern.split("*")))
        matches: Set[str] = set()
        i = bisect_left(self._keys, prefix)
        while i < len(self._keys) and self._keys[i].startswith(prefix):
            term = self._terms[i]
            if term not in matches and regex.fullmatch(term):
                matches.add(term)
            i += 1
        return matches

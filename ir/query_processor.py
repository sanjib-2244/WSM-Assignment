"""Module 5: Query processing.

Grammar (precedence low -> high):
    expr     := and_expr ( OR and_expr )*
    and_expr := unary ( [AND] unary )*          # AND may be implicit
    unary    := NOT unary | primary
    primary  := '(' expr ')' | "phrase words" | term
Operators must be UPPERCASE. Terms may contain '*' wildcards.
"""
from __future__ import annotations

import re
from typing import List, Optional, Set

from .inverted_index import InvertedIndex
from .normalizer import normalize_tokens
from .tokenizer import tokenize
from .wildcard import PermutermIndex

_LEXER = re.compile(r'"[^"]*"|\(|\)|[^\s()"]+')


class QuerySyntaxError(ValueError):
    pass


class QueryProcessor:
    def __init__(self, index: InvertedIndex, wildcard: PermutermIndex) -> None:
        self.index = index
        self.wildcard = wildcard
        self._toks: List[str] = []
        self._pos = 0

    # ---- public API ---------------------------------------------------
    def search(self, query: str) -> Set[int]:
        self._toks = _LEXER.findall(query)
        self._pos = 0
        if not self._toks:
            return set()
        result = self._parse_or()
        if self._pos != len(self._toks):
            raise QuerySyntaxError(f"Unexpected token: {self._toks[self._pos]!r}")
        return result

    # ---- parser -------------------------------------------------------
    def _peek(self) -> Optional[str]:
        return self._toks[self._pos] if self._pos < len(self._toks) else None

    def _next(self) -> str:
        tok = self._toks[self._pos]
        self._pos += 1
        return tok

    def _parse_or(self) -> Set[int]:
        result = self._parse_and()
        while self._peek() == "OR":
            self._next()
            result |= self._parse_and()
        return result

    def _parse_and(self) -> Set[int]:
        result = self._parse_unary()
        while True:
            tok = self._peek()
            if tok == "AND":
                self._next()
            elif tok is None or tok in ("OR", ")"):
                return result
            result &= self._parse_unary()

    def _parse_unary(self) -> Set[int]:
        if self._peek() == "NOT":
            self._next()
            return self.index.all_doc_ids - self._parse_unary()
        return self._parse_primary()

    def _parse_primary(self) -> Set[int]:
        tok = self._peek()
        if tok is None:
            raise QuerySyntaxError("Query ended unexpectedly")
        if tok == "(":
            self._next()
            result = self._parse_or()
            if self._peek() != ")":
                raise QuerySyntaxError("Missing closing parenthesis")
            self._next()
            return result
        if tok in (")", "AND", "OR"):
            raise QuerySyntaxError(f"Unexpected {tok!r}")
        self._next()
        if tok.startswith('"'):
            return self._phrase(tok.strip('"'))
        return self._term(tok)

    # ---- leaf evaluation ----------------------------------------------
    def _candidates(self, raw: str) -> List[Set[str]]:
        """Tokenize + normalize raw text; each token -> set of matching terms."""
        toks = normalize_tokens(tokenize(raw, keep_wildcards=True))
        return [self.wildcard.expand(t) for t in toks]

    def _term(self, raw: str) -> Set[int]:
        cands = self._candidates(raw)
        if len(cands) > 1:         # token splits into several words -> phrase
            return self._phrase(raw)
        docs: Set[int] = set()
        for term in (cands[0] if cands else ()):
            docs |= self.index.postings(term)
        return docs

    def _phrase(self, raw: str) -> Set[int]:
        cands = self._candidates(raw)
        if not cands or any(not c for c in cands):
            return set()
        docs = set.intersection(*[
            set().union(*(self.index.postings(t) for t in c)) for c in cands])
        hits: Set[int] = set()
        for doc_id in docs:
            starts = {p for t in cands[0] for p in self.index.positions(t, doc_id)}
            for offset, c in enumerate(cands[1:], start=1):
                ok = {p for t in c for p in self.index.positions(t, doc_id)}
                starts = {s for s in starts if s + offset in ok}
                if not starts:
                    break
            if starts:
                hits.add(doc_id)
        return hits

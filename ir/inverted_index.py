"""Module 4: Positional inverted index construction."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Set

from .document_loader import Document
from .normalizer import normalize_tokens
from .tokenizer import tokenize


class InvertedIndex:
    """term -> {doc_id -> [positions]}"""

    def __init__(self) -> None:
        self._index: Dict[str, Dict[int, List[int]]] = defaultdict(dict)
        self._doc_ids: Set[int] = set()

    # ---- construction -------------------------------------------------
    def add_document(self, doc_id: int, terms: Iterable[str]) -> None:
        self._doc_ids.add(doc_id)
        for pos, term in enumerate(terms):
            self._index[term].setdefault(doc_id, []).append(pos)

    @classmethod
    def build(cls, documents: Iterable[Document],
              tokenizer: Callable[[str], List[str]] = tokenize,
              normalizer: Callable[[Iterable[str]], List[str]] = normalize_tokens
              ) -> "InvertedIndex":
        index = cls()
        for doc in documents:
            index.add_document(doc.doc_id, normalizer(tokenizer(doc.text)))
        return index

    # ---- lookup -------------------------------------------------------
    def postings(self, term: str) -> Set[int]:
        return set(self._index[term]) if term in self._index else set()

    def positions(self, term: str, doc_id: int) -> List[int]:
        return self._index[term].get(doc_id, []) if term in self._index else []

    def term_frequency(self, term: str, doc_id: int) -> int:
        return len(self.positions(term, doc_id))

    def document_frequency(self, term: str) -> int:
        return len(self._index[term]) if term in self._index else 0

    @property
    def vocabulary(self) -> List[str]:
        return sorted(self._index)

    @property
    def all_doc_ids(self) -> Set[int]:
        return set(self._doc_ids)

    def __contains__(self, term: str) -> bool:
        return term in self._index

"""Facade wiring all modules together."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .document_loader import Document, load_documents
from .inverted_index import InvertedIndex
from .query_processor import QueryProcessor
from .wildcard import PermutermIndex


@dataclass
class Hit:
    doc: Document
    snippet: str


class SearchEngine:
    def __init__(self, directory: str | Path) -> None:
        self.documents: List[Document] = load_documents(directory)
        self.index = InvertedIndex.build(self.documents)
        self.wildcard = PermutermIndex(self.index.vocabulary)
        self.processor = QueryProcessor(self.index, self.wildcard)

    def search(self, query: str) -> List[Hit]:
        ids = sorted(self.processor.search(query))
        return [Hit(self.documents[i], self._snippet(self.documents[i])) for i in ids]

    @staticmethod
    def _snippet(doc: Document, width: int = 90) -> str:
        flat = " ".join(doc.text.split())
        return flat if len(flat) <= width else flat[:width].rstrip() + "..."

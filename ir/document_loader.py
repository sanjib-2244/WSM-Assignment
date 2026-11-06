"""Module 1: Document loading."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


@dataclass(frozen=True)
class Document:
    doc_id: int
    name: str
    path: Path
    text: str


def load_documents(directory: str | Path,
                   extensions: Sequence[str] = (".txt", ".md")) -> List[Document]:
    """Recursively load every matching text file under `directory`.

    Doc IDs are assigned 0..N-1 in sorted path order so results are stable.
    """
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"Document directory not found: {root}")

    exts = {e.lower() for e in extensions}
    paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts)

    documents: List[Document] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue  # skip unreadable files
        documents.append(Document(len(documents), str(path.relative_to(root)), path, text))
    return documents

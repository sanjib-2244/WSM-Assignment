"""Module 7: Frontend GUI (Tkinter)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .engine import SearchEngine
from .query_processor import QuerySyntaxError


class SearchApp(tk.Tk):
    def __init__(self, engine: SearchEngine) -> None:
        super().__init__()
        self.engine = engine
        self.title("Document Search")
        self.geometry("720x480")
        self.minsize(480, 300)

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.query_var = tk.StringVar()
        self.entry = ttk.Entry(top, textvariable=self.query_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self.on_search())
        self.entry.focus_set()
        ttk.Button(top, text="Search", command=self.on_search).pack(side="left")

        self.status = tk.StringVar(
            value=f"{len(engine.documents)} documents, "
                  f"{len(engine.index.vocabulary)} terms indexed.")
        ttk.Label(self, textvariable=self.status, padding=(10, 0)).pack(anchor="w")

        self.results = ScrolledText(self, wrap="word", state="disabled", padx=8, pady=8)
        self.results.pack(fill="both", expand=True, padx=10, pady=10)

    def _show(self, text: str) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", text)
        self.results.configure(state="disabled")   # read-only

    def on_search(self) -> None:
        query = self.query_var.get().strip()
        if not query:
            self._show('Enter a query.\n\nExamples:  apple  |  pro*  |  "red fox"  |  cat AND NOT dog')
            return
        try:
            hits = self.engine.search(query)
        except QuerySyntaxError as exc:
            self._show(f"Query error: {exc}")
            return
        self.status.set(f"{len(hits)} result(s) for: {query}")
        if not hits:
            self._show("No matching documents.")
            return
        self._show("\n\n".join(f"{i}. {h.doc.name}\n   {h.snippet}"
                               for i, h in enumerate(hits, 1)))


def run(directory: str) -> None:
    SearchApp(SearchEngine(directory)).mainloop()

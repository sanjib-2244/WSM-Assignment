# Document Search Engine

Inverted-index search over a folder of `.txt`/`.md` files, with a Tkinter GUI.
Python 3.9+, standard library only.

```
python main.py                              # launch GUI on data/documents
python main.py --docs path/to/dir           # custom folder
python main.py --query 'pro* AND NOT cat'   # terminal mode
python -m unittest discover -s tests        # run tests
```

| Module | File |
|---|---|
| Document loading | `ir/document_loader.py` |
| Tokenization | `ir/tokenizer.py` |
| Normalization / case folding | `ir/normalizer.py` |
| Inverted index | `ir/inverted_index.py` |
| Query processing | `ir/query_processor.py` |
| Wildcards (permuterm index) | `ir/wildcard.py` |
| GUI | `ir/gui.py` |
| Wiring | `ir/engine.py`, `main.py` |

Query syntax: `word`, `pro*`, `*ing`, `a*e`, `"exact phrase"`, `AND` (implicit), `OR`, `NOT`, `( )`.
Operators must be uppercase.

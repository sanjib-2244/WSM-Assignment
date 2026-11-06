"""Entry point.  python main.py [--docs DIR] [--query "text"]"""
import argparse
from pathlib import Path

DEFAULT_DOCS = Path(__file__).parent / "data" / "documents"


def main() -> None:
    ap = argparse.ArgumentParser(description="Inverted-index document search")
    ap.add_argument("--docs", default=str(DEFAULT_DOCS), help="directory of .txt/.md files")
    ap.add_argument("--query", help="run one query in the terminal instead of opening the GUI")
    args = ap.parse_args()

    if args.query is not None:
        from ir.engine import SearchEngine
        for hit in SearchEngine(args.docs).search(args.query):
            print(f"{hit.doc.name}: {hit.snippet}")
    else:
        from ir.gui import run
        run(args.docs)


if __name__ == "__main__":
    main()

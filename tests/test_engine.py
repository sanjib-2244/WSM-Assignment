import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ir.engine import SearchEngine
from ir.normalizer import normalize
from ir.tokenizer import tokenize
from ir.wildcard import PermutermIndex
from ir.query_processor import QuerySyntaxError

DOCS = Path(__file__).resolve().parent.parent / "data" / "documents"


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = SearchEngine(DOCS)

    def names(self, q):
        return sorted(h.doc.name for h in self.e.search(q))

    def test_tokenize_normalize(self):
        self.assertEqual(tokenize("Don't stop, now!"), ["Don't", "stop", "now"])
        self.assertEqual(normalize("Café"), "cafe")
        self.assertEqual(normalize("Don't"), "dont")

    def test_simple(self):
        self.assertEqual(self.names("FOX"), ["fox.txt"])
        self.assertEqual(self.names("cafe"), ["cafe.txt"])
        self.assertEqual(self.names("DON'T"), ["cafe.txt"])

    def test_boolean(self):
        self.assertEqual(self.names("cat AND dog"), ["pets.txt"])
        self.assertEqual(self.names("fox OR apple"), ["fox.txt", "fruit.txt"])
        self.assertNotIn("fox.txt", self.names("NOT fox"))
        self.assertEqual(self.names("(fox OR cat) AND dog"), ["fox.txt", "pets.txt"])

    def test_phrase(self):
        self.assertEqual(self.names('"quick brown"'), ["fox.txt"])
        self.assertEqual(self.names('"brown quick"'), [])

    def test_wildcards(self):
        self.assertEqual(self.names("program*"), ["python.txt"])
        self.assertEqual(self.names("*ing"), ["python.txt"])
        self.assertEqual(self.names("c*t"), ["cafe.txt", "pets.txt"])
        self.assertEqual(self.names("pro*ing"), ["python.txt"])
        p = PermutermIndex(["apple", "apply", "ample", "bat"])
        self.assertEqual(p.expand("ap*"), {"apple", "apply"})
        self.assertEqual(p.expand("a*le"), {"apple", "ample"})
        self.assertEqual(p.expand("*at"), {"bat"})
        self.assertEqual(p.expand("a*p*e"), {"apple", "ample"})

    def test_errors(self):
        with self.assertRaises(QuerySyntaxError):
            self.e.search("(fox")


if __name__ == "__main__":
    unittest.main()

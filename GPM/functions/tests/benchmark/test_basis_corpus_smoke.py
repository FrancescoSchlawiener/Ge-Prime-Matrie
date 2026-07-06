"""CI Smoke — Basis-Layer Korpus-Abfrage."""

import time
import unittest

from alphabets import AlphabetProfile
from analysis.basis.compare_tiered import CompareTier
from analysis.basis.corpus_compare import find_similar_documents
from analysis.compile.compiler import compile_text


class TestBasisCorpusSmoke(unittest.TestCase):
    def test_tier0_1_fast_on_500_docs(self):
        corpus = []
        for i in range(500):
            doc, _ = compile_text(f"Wort{i} Text Satz.", AlphabetProfile.OG)
            corpus.append((f"d{i}", doc))
        query, _ = compile_text("Wort1 Text.", AlphabetProfile.OG)
        start = time.perf_counter()
        result = find_similar_documents(
            query,
            corpus,
            max_tier=CompareTier.BASIS,
            top_k=5,
            min_basis_score=0.01,
        )
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.15)
        self.assertIsInstance(result.hits, list)


if __name__ == "__main__":
    unittest.main()

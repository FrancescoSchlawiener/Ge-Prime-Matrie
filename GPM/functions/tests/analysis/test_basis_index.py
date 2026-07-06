"""Tests für BasisIndex und query_candidates."""

import unittest

from alphabets import AlphabetProfile
from analysis.basis.index import build_basis_index, extend_basis_index, query_candidates
from analysis.basis.signature import get_basis_signature
from analysis.compile.compiler import compile_text


class TestBasisIndex(unittest.TestCase):
    def test_candidates_subset_of_corpus(self):
        corpus: list[tuple[str, object]] = []
        texts = [
            ("a", "Hallo Welt heute."),
            ("b", "Guten Morgen allerseits."),
            ("c", "Hallo Freunde."),
            ("d", "Quantenphysik Forschung."),
            ("e", "ZZZZ QQQQ WWWW."),
        ]
        for doc_id, text in texts:
            doc, _ = compile_text(text, AlphabetProfile.OG)
            corpus.append((doc_id, doc))

        partitions = build_basis_index(corpus, include_relation_sketch=False)
        query_doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        query_sig = get_basis_signature(query_doc, doc_id="q")
        index = partitions[AlphabetProfile.OG]
        result = query_candidates(index, query_sig, top_k=3, min_shared_primes=2)
        self.assertLessEqual(len(result.candidates), 3)
        self.assertLess(len(result.candidates), len(corpus))

    def test_large_corpus_filtering(self):
        corpus = []
        for i in range(200):
            doc, _ = compile_text(f"Wort{i} Text Satz.", AlphabetProfile.OG)
            corpus.append((f"d{i}", doc))
        partitions = build_basis_index(corpus, include_relation_sketch=False)
        query, _ = compile_text("Wort1 Text.", AlphabetProfile.OG)
        query_sig = get_basis_signature(query, doc_id="q")
        result = query_candidates(
            partitions[AlphabetProfile.OG],
            query_sig,
            top_k=10,
            min_shared_primes=2,
        )
        self.assertLess(len(result.candidates), 200)

    def test_extend_basis_index(self):
        partitions = build_basis_index([], include_relation_sketch=False)
        doc, _ = compile_text("Hallo.", AlphabetProfile.OG)
        extend_basis_index(partitions, [("x", doc)], include_relation_sketch=False)
        self.assertIn(AlphabetProfile.OG, partitions)
        self.assertIn("x", partitions[AlphabetProfile.OG].signatures)


if __name__ == "__main__":
    unittest.main()

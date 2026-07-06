"""Tests für find_similar_documents."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.multiset import anagram_class_key
from analysis.basis.compare_tiered import CompareTier
from analysis.basis.corpus_compare import find_similar_documents
from analysis.basis.index import build_basis_index, query_candidates
from analysis.basis.signature import get_basis_signature
from analysis.compile.compiler import compile_text


class TestCorpusCompare(unittest.TestCase):
    def test_find_similar_end_to_end(self):
        query, _ = compile_text("Hallo Welt Freunde.", AlphabetProfile.OG)
        corpus = []
        for doc_id, text in [
            ("1", "Hallo Welt."),
            ("2", "Hallo Freunde."),
            ("3", "Quantenphysik."),
        ]:
            doc, _ = compile_text(text, AlphabetProfile.OG)
            corpus.append((doc_id, doc))

        result = find_similar_documents(
            query,
            corpus,
            max_tier=CompareTier.BASIS,
            top_k=2,
            min_basis_score=0.01,
        )
        self.assertLessEqual(len(result.hits), 2)
        if result.hits:
            self.assertGreater(result.hits[0].score, 0.0)

    def test_substance_hint_anagram_smoke(self):
        query, _ = compile_text("Hallo.", AlphabetProfile.OG)
        doc_match, _ = compile_text("Hallo.", AlphabetProfile.OG)
        doc_other, _ = compile_text("Quantenphysik Forschung.", AlphabetProfile.OG)
        corpus = [("a", doc_match), ("b", doc_other)]
        partitions = build_basis_index(corpus, include_relation_sketch=False)
        query_sig = get_basis_signature(query, doc_id="q")
        substance = query.header[query.tokens[0].word_id].substance
        hint = anagram_class_key(substance, AlphabetProfile.OG)
        index = partitions[AlphabetProfile.OG]
        with_hint = query_candidates(
            index,
            query_sig,
            substance_hint=hint,
            top_k=5,
        )
        self.assertIsNotNone(with_hint.candidates or with_hint.zero_reason)


if __name__ == "__main__":
    unittest.main()

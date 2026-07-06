"""E5 — auto-minhash bei Korpus >= 10k Dokumente."""

import unittest
from unittest.mock import MagicMock, patch

from alphabets import AlphabetProfile
from analysis.basis.corpus_compare import MINHASH_AUTO_THRESHOLD, find_similar_documents
from analysis.compile.compiler import compile_text


class TestCorpusMinhashAuto(unittest.TestCase):
    def test_threshold_constant(self):
        self.assertEqual(MINHASH_AUTO_THRESHOLD, 10_000)

    @patch("analysis.basis.corpus_compare.build_basis_index")
    @patch("analysis.basis.corpus_compare.get_basis_signature")
    def test_large_corpus_enables_minhash(self, mock_sig, mock_build):
        doc, _ = compile_text("Test.", AlphabetProfile.OG)
        mock_sig.return_value = MagicMock(profile=AlphabetProfile.OG)
        mock_build.return_value = {AlphabetProfile.OG: MagicMock()}

        with patch("analysis.basis.corpus_compare.query_candidates") as mock_query:
            mock_query.return_value = MagicMock(candidates=[], zero_reason=None)
            corpus = [(str(i), doc) for i in range(MINHASH_AUTO_THRESHOLD)]
            find_similar_documents(doc, corpus, top_k=1)

        _, kwargs = mock_build.call_args
        self.assertTrue(kwargs.get("use_minhash"))
        self.assertTrue(kwargs.get("include_typed_sketch") is False or kwargs.get("include_typed_sketch") is not None)

        sig_kwargs = mock_sig.call_args.kwargs
        self.assertTrue(sig_kwargs.get("use_minhash"))

        query_kwargs = mock_query.call_args.kwargs
        self.assertGreater(query_kwargs.get("minhash_min_band", 0.0), 0.0)


if __name__ == "__main__":
    unittest.main()

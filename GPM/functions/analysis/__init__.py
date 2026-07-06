# GPM analysis layer — compare, compile, geometry, binary I/O (Phase 4a+)

from analysis.algebra import (
    counter_cosine,
    coupled_point_similarity,
    fuse_tier_scores,
    profile_log_norm,
    profile_symmetry_guard,
)
from analysis.basis import (
    CompareTier,
    build_basis_signature,
    compare_documents_tiered,
    find_similar_documents,
)
from analysis.binary import read_gpm, write_gpm, load_gpm, analyze_gpm
from analysis.compile.compiler import compile_text, compile_text_to_gpm
from analysis.compile.reconstruct import reconstruct_text

__all__ = [
    "CompareTier",
    "build_basis_signature",
    "compare_documents_tiered",
    "compile_text",
    "compile_text_to_gpm",
    "counter_cosine",
    "coupled_point_similarity",
    "find_similar_documents",
    "fuse_tier_scores",
    "profile_log_norm",
    "profile_symmetry_guard",
    "reconstruct_text",
    "write_gpm",
    "read_gpm",
    "load_gpm",
    "analyze_gpm",
]

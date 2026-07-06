from analysis.substance.compare import (
    compare_substances,
    substance_covers,
    substance_ggt_kgv_distance,
    substance_ggt_kgv_similarity,
    substance_lcm,
    union_letters,
)
from analysis.substance.diff import classify_word_pair, diff_substances

__all__ = [
    "compare_substances",
    "substance_covers",
    "substance_ggt_kgv_distance",
    "substance_ggt_kgv_similarity",
    "substance_lcm",
    "union_letters",
    "diff_substances",
    "classify_word_pair",
    "transition_fields",
]


def __getattr__(name: str):
    if name == "transition_fields":
        from analysis.substance.transition import transition_fields

        return transition_fields
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

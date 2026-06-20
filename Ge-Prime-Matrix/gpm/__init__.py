"""Ge-Prime-Matrix Dateiformat (.gpm) — v4 (tiered S/I, kompakter Separator)."""

__all__ = [
    "compile_text",
    "read_gpm",
    "write_gpm",
    "analyze_gpm",
    "decode_document_text",
    "reconstruct_text",
    "search_by_word",
    "search_by_gcd",
    "search_by_lcm",
    "genome_payload_bytes",
    "body_payload_bytes",
    "GpmDocument",
    "GpmFormatError",
    "GpmHeaderEntry",
    "GpmToken",
]


def __getattr__(name: str):
    if name == "compile_text":
        from gpm.compiler import compile_text

        return compile_text
    if name in ("read_gpm", "write_gpm", "GpmFormatError"):
        from gpm import format as fmt

        return getattr(fmt, name)
    if name in ("GpmDocument", "GpmHeaderEntry", "GpmToken"):
        from gpm import model

        return getattr(model, name)
    if name in (
        "analyze_gpm",
        "decode_document_text",
        "reconstruct_text",
        "search_by_word",
        "search_by_gcd",
        "search_by_lcm",
        "genome_payload_bytes",
        "body_payload_bytes",
    ):
        from gpm import reader

        return getattr(reader, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

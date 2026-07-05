#!/usr/bin/env python3
"""CLI für .gpm — kompilieren, lesen, suchen."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.config import GPM_VERSION, gpm_si_storage_payload
from gpm.compiler import compile_text
from gpm.reader import analyze_gpm, search_by_gcd, search_by_lcm, search_by_word
from gpm.format import read_gpm
from gpm.separator_codec import perm_code_label


def cmd_compile(args: argparse.Namespace) -> int:
    text = Path(args.input).read_text(encoding="utf-8")
    _, blob, stats = compile_text(text)
    Path(args.output).write_bytes(blob)
    print(f"Geschrieben: {args.output} (.gpm v{GPM_VERSION})")
    print(
        f"  {stats.unique_words} eindeutig · {stats.total_tokens} Token · "
        f"{stats.file_bytes} Byte ({stats.compression_ratio:.1%} der Quelle)"
    )
    si = gpm_si_storage_payload()
    print(f"  Genom {stats.header_bytes} B · Geometrie {stats.body_bytes} B · {si['summary']}")
    print(
        f"  Separator: {stats.separator_bytes} B · "
        f"Perm {stats.separator_perm} ({perm_code_label(stats.separator_perm)})"
    )
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    blob = Path(args.input).read_bytes()
    analysis = analyze_gpm(blob)
    print(f".gpm v{analysis.version} · {analysis.file_bytes} Byte")
    print(f"Genom: {analysis.unique_words} Wörter · Body: {analysis.total_tokens} Token")
    print(f"Genom {analysis.header_bytes} B · Geometrie {analysis.body_bytes} B")
    if analysis.version >= 4:
        si = gpm_si_storage_payload(gpm_version=analysis.version)
        print(f"  {si['summary']}")
    print(
        f"Separator: {analysis.separator_bytes} B · "
        f"Perm {analysis.separator_perm} ({perm_code_label(analysis.separator_perm)})"
    )
    print("— Rekonstruiert (Auszug) —")
    print(analysis.reconstructed_text[:500])
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    doc = read_gpm(Path(args.input).read_bytes())
    if args.mode == "lcm":
        if not args.query2:
            print("kgV-Modus: query2 erforderlich (z. B. search file.gpm MUT WUT --mode lcm)")
            return 1
        result = search_by_lcm(doc, args.query, args.query2)
        print(
            f"kgV-Treffer: {result['unique_words']} Wörter, {result['token_hits']} Token · "
            f"kgV={result['lcm_value']}"
        )
        print(f"  Union: {result['union_letters']}")
        for row in result["matches"][:20]:
            print(f"  [{row['word_id']}] {row['original']} S={row['substance']}")
    elif args.mode == "gcd":
        result = search_by_gcd(doc, args.query)
        print(f"ggT-Treffer: {result['unique_words']} Wörter, {result['token_hits']} Token")
        for row in result["matches"][:20]:
            print(f"  [{row['word_id']}] {row['original']} ggT={row['gcd_value']}")
    else:
        result = search_by_word(doc, args.query)
        print(f"Substanz-Match: {result['occurrences']} Vorkommen")
        for pos in result["positions"][:20]:
            print(f"  Position {pos['position']} · Word-ID {pos['word_id']} · I={pos['perm_index']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ge-Prime-Matrix .gpm Tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_compile = sub.add_parser("compile", help="Text → .gpm")
    p_compile.add_argument("input", help="Quelltext (.txt)")
    p_compile.add_argument("-o", "--output", default="document.gpm")
    p_compile.set_defaults(func=cmd_compile)

    p_read = sub.add_parser("read", help=".gpm analysieren")
    p_read.add_argument("input", help=".gpm Datei")
    p_read.set_defaults(func=cmd_read)

    p_search = sub.add_parser("search", help="In .gpm suchen")
    p_search.add_argument("input", help=".gpm Datei")
    p_search.add_argument("query", help="Suchwort (ggT/Substanz) bzw. Wort 1 (kgV)")
    p_search.add_argument("query2", nargs="?", default="", help="Wort 2 für kgV-Modus")
    p_search.add_argument("--mode", choices=("substance", "gcd", "lcm"), default="substance")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

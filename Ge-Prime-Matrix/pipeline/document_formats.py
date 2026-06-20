"""Byte-genaue Größen gängiger Dokument- und Archivformate (nur stdlib)."""

from __future__ import annotations

import io
import zlib
import zipfile


def utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


def human_bytes(num: int) -> str:
    if num < 1024:
        return f"{num} B"
    if num < 1024 * 1024:
        return f"{num / 1024:.1f} KB".replace(".", ",")
    return f"{num / (1024 * 1024):.2f} MB".replace(".", ",")


def txt_file_bytes(text: str, *, bom: bool = False) -> int:
    return utf8_len(text) + (3 if bom else 0)


def md_file_bytes(text: str, *, title: str = "Quelle") -> int:
    safe_title = title.replace('"', "'")[:80]
    body = f'---\ntitle: "{safe_title}"\nencoding: utf-8\n---\n\n{text}'
    return utf8_len(body)


def html_file_bytes(text: str, *, title: str = "Quelle") -> int:
    from html import escape

    safe_title = escape(title[:120])
    safe_body = escape(text)
    doc = (
        "<!DOCTYPE html>\n"
        '<html lang="de">\n<head>\n'
        '<meta charset="utf-8">\n'
        f"<title>{safe_title}</title>\n"
        "</head>\n<body>\n"
        f"<pre>{safe_body}</pre>\n"
        "</body>\n</html>\n"
    )
    return utf8_len(doc)


def zip_utf8_bytes(text: str, *, arcname: str = "quelle.txt") -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(arcname, text.encode("utf-8"))
    return len(buf.getvalue())


def _pdf_literal(raw: bytes) -> str:
    parts = ["("]
    for byte in raw:
        if byte in (0x28, 0x29, 0x5C):
            parts.append(f"\\{byte:03o}")
        elif 32 <= byte <= 126:
            parts.append(chr(byte))
        else:
            parts.append(f"\\{byte:03o}")
    parts.append(")")
    return "".join(parts)


def _pdf_page_stream(lines: list[str]) -> bytes:
    ops = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    for line in lines:
        ops.append(_pdf_literal(line.encode("utf-8")))
        ops.append("Tj T*")
    ops.append("ET")
    return "\n".join(ops).encode("ascii")


def pdf_page_count(text: str, *, lines_per_page: int = 48) -> int:
    """Seitenanzahl wie in build_minimal_pdf (48 Zeilen pro Seite)."""
    lines = text.splitlines() or [""]
    return max(1, (len(lines) + lines_per_page - 1) // lines_per_page)


def build_minimal_pdf(text: str, *, lines_per_page: int = 48) -> bytes:
    """Minimales PDF 1.4, Helvetica, Flate-Streams — exakte Byte-Zählung."""
    lines = text.splitlines() or [""]
    page_line_groups: list[list[str]] = []
    bucket: list[str] = []
    for line in lines:
        bucket.append(line)
        if len(bucket) >= lines_per_page:
            page_line_groups.append(bucket)
            bucket = []
    if bucket:
        page_line_groups.append(bucket)
    if not page_line_groups:
        page_line_groups = [[""]]

    page_streams = [zlib.compress(_pdf_page_stream(group)) for group in page_line_groups]
    page_count = len(page_streams)

    # Layout: 1 Catalog · 2 Pages · 3 Font · 4…3+N Content · 4+N…3+2N Page
    font_id = 3
    content_start = 4
    page_start = content_start + page_count
    page_ids = list(range(page_start, page_start + page_count))
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)

    parts: list[bytes] = [b"%PDF-1.4\n"]
    offsets: list[int] = []
    expected_id = 1

    def emit(content: bytes) -> int:
        nonlocal expected_id
        obj_id = expected_id
        expected_id += 1
        offsets.append(sum(len(p) for p in parts))
        parts.append(f"{obj_id} 0 obj\n".encode("ascii"))
        parts.append(content)
        parts.append(b"\nendobj\n")
        return obj_id

    emit(b"<< /Type /Catalog /Pages 2 0 R >>")
    emit(f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode("ascii"))
    emit(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for idx in range(page_count):
        stream = page_streams[idx]
        stream_obj = (
            f"<< /Length {len(stream)} /Filter /FlateDecode >>\nstream\n".encode("ascii")
            + stream
            + b"\nendstream"
        )
        emit(stream_obj)

    for idx in range(page_count):
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_start + idx} 0 R >>"
        )
        emit(page_obj.encode("ascii"))

    xref_pos = sum(len(p) for p in parts)
    total_objs = page_start + page_count - 1
    parts.append(f"xref\n0 {total_objs + 1}\n".encode("ascii"))
    parts.append(b"0000000000 65535 f \n")
    for off in offsets:
        parts.append(f"{off:010d} 00000 n \n".encode("ascii"))
    parts.append(
        f"trailer\n<< /Size {total_objs + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return b"".join(parts)


def pdf_file_bytes(text: str) -> int:
    return len(build_minimal_pdf(text))

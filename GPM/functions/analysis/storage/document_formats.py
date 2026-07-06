"""Byte sizes for common document formats (stdlib only)."""

from __future__ import annotations

import io
import zipfile


def utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


def txt_file_bytes(text: str, *, bom: bool = False) -> int:
    return utf8_len(text) + (3 if bom else 0)


def md_file_bytes(text: str, *, title: str = "source") -> int:
    safe_title = title.replace('"', "'")[:80]
    body = f'---\ntitle: "{safe_title}"\nencoding: utf-8\n---\n\n{text}'
    return utf8_len(body)


def html_file_bytes(text: str, *, title: str = "source") -> int:
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


def zip_utf8_bytes(text: str, *, arcname: str = "source.txt") -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(arcname, text.encode("utf-8"))
    return len(buf.getvalue())

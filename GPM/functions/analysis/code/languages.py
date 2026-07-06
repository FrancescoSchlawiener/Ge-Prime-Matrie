"""Sprach-Spezifikationen für C(I) Code-Parsing."""

from __future__ import annotations

import os
from dataclasses import dataclass

KEYWORDS_PY = frozenset(
    {
        "def", "class", "if", "elif", "else", "for", "while", "return", "import", "from",
        "pass", "break", "continue", "try", "except", "finally", "with", "as", "raise",
        "yield", "lambda", "async", "await", "global", "nonlocal", "assert", "del",
        "in", "is", "not", "and", "or",
    }
)

KEYWORDS_JS = frozenset(
    {
        "function", "class", "if", "else", "for", "while", "do", "switch", "return",
        "import", "export", "let", "var", "const", "new", "try", "catch", "finally",
        "throw", "typeof", "instanceof", "default", "case", "break", "continue",
        "async", "await", "this", "super", "delete", "void", "in", "of", "from", "as",
    }
)

KEYWORDS_C = frozenset(
    {
        "if", "else", "for", "while", "do", "switch", "case", "break", "continue",
        "return", "struct", "typedef", "enum", "const", "static", "extern", "void",
        "int", "char", "float", "double", "long", "short", "unsigned", "signed",
    }
)

KEYWORDS_JAVA = KEYWORDS_C | frozenset(
    {"public", "private", "protected", "class", "interface", "extends", "implements", "new", "try", "catch", "finally", "throw", "package", "import"}
)

KEYWORDS_GO = frozenset(
    {"package", "import", "func", "var", "const", "type", "struct", "interface", "map", "chan",
     "if", "else", "for", "range", "switch", "case", "default", "break", "continue", "return", "go", "defer"}
)

KEYWORDS_RUST = frozenset(
    {"fn", "let", "mut", "const", "struct", "enum", "impl", "trait", "type", "pub", "use", "mod",
     "if", "else", "match", "loop", "while", "for", "break", "continue", "return", "async", "await", "self", "Self"}
)

KEYWORDS_PHP = frozenset(
    {"function", "class", "interface", "trait", "namespace", "use", "public", "private", "protected",
     "if", "else", "elseif", "for", "foreach", "while", "do", "switch", "case", "break", "continue", "return", "new", "try", "catch", "finally", "throw"}
)

KEYWORDS_CS = frozenset(
    {"namespace", "using", "class", "struct", "interface", "enum", "public", "private", "protected",
     "static", "void", "int", "string", "bool", "if", "else", "for", "foreach", "while", "switch", "case", "break", "continue", "return", "new", "try", "catch", "finally", "throw"}
)

KEYWORDS_SWIFT = frozenset(
    {"func", "var", "let", "class", "struct", "enum", "protocol", "extension", "import",
     "if", "else", "for", "while", "switch", "case", "break", "continue", "return", "try", "catch", "throw", "guard"}
)

KEYWORDS_KT = frozenset(
    {"fun", "val", "var", "class", "interface", "object", "package", "import", "when", "if", "else",
     "for", "while", "do", "break", "continue", "return", "try", "catch", "finally", "throw", "data", "enum"}
)

KEYWORDS_CSS = frozenset({"@media", "@import", "@keyframes"})

KEYWORDS_SQL = frozenset(
    {
        "SELECT", "FROM", "WHERE", "INSERT", "INTO", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER",
        "TABLE", "INDEX", "VIEW", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "ON", "AS", "AND", "OR",
        "NOT", "NULL", "IS", "IN", "VALUES", "SET", "BEGIN", "END", "CASE", "WHEN", "THEN", "ELSE",
        "COMMIT", "ROLLBACK", "GRANT", "REVOKE", "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "UNIQUE",
        "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "DISTINCT", "EXISTS",
    }
)

KEYWORDS_RB = frozenset(
    {"def", "class", "module", "if", "elsif", "else", "unless", "while", "until", "for", "in", "do", "end",
     "begin", "case", "when", "then", "return", "break", "next", "redo", "yield", "require", "include"}
)

KEYWORDS_SH = frozenset(
    {"if", "then", "else", "elif", "fi", "for", "while", "until", "do", "done", "case", "esac", "in",
     "function", "return", "break", "continue", "export", "local", "readonly"}
)

IGNORED_SUFFIXES = frozenset(
    {
        ".min.js", ".min.css", ".map", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
        ".pdf", ".zip", ".gz", ".tar", ".exe", ".dll", ".so", ".dylib", ".woff", ".woff2",
    }
)

FENCE_LANG_ALIASES: dict[str, str] = {
    "py": "py", "python": "py", "python3": "py", "pyw": "py",
    "js": "js", "javascript": "js", "typescript": "js", "ts": "js", "jsx": "js", "tsx": "js",
    "html": "html", "htm": "html", "xhtml": "html",
    "xml": "xml", "sql": "sql", "sh": "sh", "bash": "sh", "shell": "sh",
    "rb": "rb", "ruby": "rb", "json": "json", "md": "markdown", "markdown": "markdown",
    "c": "c", "java": "java", "go": "go", "rs": "rs", "rust": "rs",
}


def resolve_fence_language(info: str) -> str:
    raw = (info or "py").strip().lower()
    return FENCE_LANG_ALIASES.get(raw, raw if raw in LANGUAGES else "py")


@dataclass(frozen=True)
class LanguageSpec:
    id: str
    name: str
    extensions: tuple[str, ...]
    block_style: str  # brace | indent | tag | keyword | flat
    comment_style: str  # c | hash | sql | none
    keywords: frozenset[str] = frozenset()
    keywords_lower: frozenset[str] = frozenset()
    block_pairs: tuple[tuple[str, str], ...] = ()
    case_insensitive: bool = False


def _spec(
    id: str,
    name: str,
    extensions: tuple[str, ...],
    block_style: str,
    comment_style: str,
    keywords: frozenset[str] = frozenset(),
    block_pairs: tuple[tuple[str, str], ...] = (),
    case_insensitive: bool = False,
) -> LanguageSpec:
    kl = frozenset(k.lower() for k in keywords)
    return LanguageSpec(
        id=id,
        name=name,
        extensions=extensions,
        block_style=block_style,
        comment_style=comment_style,
        keywords=keywords,
        keywords_lower=kl,
        block_pairs=block_pairs,
        case_insensitive=case_insensitive,
    )


LANGUAGES: dict[str, LanguageSpec] = {
    "py": _spec("py", "Python", (".py", ".pyw", ".pyi"), "indent", "hash", KEYWORDS_PY),
    "js": _spec("js", "JavaScript/TS", (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"), "brace", "c", KEYWORDS_JS),
    "html": _spec("html", "HTML", (".html", ".htm", ".xhtml"), "tag", "none"),
    "xml": _spec("xml", "XML", (".xml", ".xsd", ".xslt", ".svg"), "tag", "none"),
    "c": _spec("c", "C", (".c", ".h"), "brace", "c", KEYWORDS_C),
    "java": _spec("java", "Java", (".java",), "brace", "c", KEYWORDS_JAVA),
    "go": _spec("go", "Go", (".go",), "brace", "c", KEYWORDS_GO),
    "rs": _spec("rs", "Rust", (".rs",), "brace", "c", KEYWORDS_RUST),
    "php": _spec("php", "PHP", (".php",), "brace", "c", KEYWORDS_PHP),
    "cs": _spec("cs", "C#", (".cs",), "brace", "c", KEYWORDS_CS),
    "swift": _spec("swift", "Swift", (".swift",), "brace", "c", KEYWORDS_SWIFT),
    "kt": _spec("kt", "Kotlin", (".kt", ".kts"), "brace", "c", KEYWORDS_KT),
    "css": _spec("css", "CSS", (".css", ".scss", ".sass", ".less"), "brace", "c", KEYWORDS_CSS),
    "json": _spec("json", "JSON", (".json", ".jsonl"), "flat", "c"),
    "toml": _spec("toml", "TOML", (".toml",), "flat", "hash"),
    "markdown": _spec("markdown", "Markdown", (".md", ".markdown"), "flat", "none"),
    "sql": _spec(
        "sql",
        "SQL",
        (".sql",),
        "keyword",
        "sql",
        KEYWORDS_SQL,
        (("BEGIN", "END"), ("CASE", "END")),
        case_insensitive=True,
    ),
    "rb": _spec(
        "rb",
        "Ruby",
        (".rb",),
        "keyword",
        "hash",
        KEYWORDS_RB,
        (("DO", "END"), ("DEF", "END"), ("CLASS", "END"), ("MODULE", "END"), ("BEGIN", "END")),
        case_insensitive=True,
    ),
    "sh": _spec(
        "sh",
        "Shell",
        (".sh", ".bash"),
        "keyword",
        "hash",
        KEYWORDS_SH,
        (("IF", "FI"), ("FOR", "DONE"), ("WHILE", "DONE"), ("UNTIL", "DONE"), ("CASE", "ESAC")),
        case_insensitive=True,
    ),
}

VOID_HTML_TAGS = frozenset(
    {"BR", "IMG", "INPUT", "HR", "META", "LINK", "AREA", "BASE", "COL", "EMBED", "SOURCE", "TRACK", "WBR"}
)

_EXT_TO_LANG: dict[str, str] = {}
for _spec_entry in LANGUAGES.values():
    for _ext in _spec_entry.extensions:
        _EXT_TO_LANG[_ext.lower()] = _spec_entry.id


def language_for_id(language_id: str) -> LanguageSpec:
    if language_id not in LANGUAGES:
        raise ValueError(f"Unbekannte Sprache: {language_id}")
    return LANGUAGES[language_id]


def is_ignored_path(path: str) -> bool:
    lower = path.lower()
    return any(lower.endswith(suffix) for suffix in IGNORED_SUFFIXES)


def language_for_extension(path: str) -> LanguageSpec | None:
    if is_ignored_path(path):
        return None
    _, ext = os.path.splitext(path)
    lang_id = _EXT_TO_LANG.get(ext.lower())
    if lang_id is None:
        return None
    return LANGUAGES[lang_id]

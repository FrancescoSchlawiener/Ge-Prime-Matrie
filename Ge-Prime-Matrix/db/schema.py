SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT,
    fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_original TEXT NOT NULL,
    word_normalized TEXT NOT NULL,
    substance TEXT NOT NULL,
    perm_index INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'random',
    source_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE(word_normalized, language, source_id)
);

CREATE INDEX IF NOT EXISTS idx_words_language ON words(language);
CREATE INDEX IF NOT EXISTS idx_words_normalized ON words(word_normalized);
CREATE INDEX IF NOT EXISTS idx_words_substance ON words(substance);
"""

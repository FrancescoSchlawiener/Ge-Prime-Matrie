"""Deklarative Registry für Sprachen und Domänen (erweiterbar)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MIN_DB_WORDS_PER_LANGUAGE = 40

LANGUAGE_MIN_CONFIDENCE = 0.45
LANGUAGE_MIN_MARGIN = 0.12

DOMAIN_MIN_MARGIN = 0.08
DOMAIN_UNKNOWN_LANG_THRESHOLD = 0.22

# Gewichte Hybrid-Scoring
LANG_WEIGHT_PATTERNS = 0.55
LANG_WEIGHT_PROFILE = 0.30
LANG_WEIGHT_SIGNALS = 0.15

DOMAIN_WEIGHT_KEYWORDS = 0.45
DOMAIN_WEIGHT_PROFILE = 0.30
DOMAIN_WEIGHT_RELATIONS = 0.25


@dataclass(frozen=True)
class LanguageSpec:
    code: str
    label: str
    function_words: frozenset[str]
    profile_seed: str
    signals: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DomainSpec:
    code: str
    label_de: str
    label_en: str
    keywords: dict[str, frozenset[str]]
    profile_seed: dict[str, str]
    min_confidence: float = 0.28
    min_keyword_hits: int = 2


def _kw(*words: str) -> frozenset[str]:
    return frozenset(w.upper() for w in words)


DE_FUNCTION_WORDS = _kw(
    "der", "die", "das", "und", "ist", "ein", "eine", "einer", "einem", "einen",
    "nicht", "auf", "mit", "fuer", "für", "auch", "nach", "bei", "wird", "wurde",
    "sind", "war", "waren", "haben", "hat", "hatte", "oder", "aber", "wenn", "weil",
    "ueber", "über", "durch", "kann", "koennen", "können", "sein", "seine", "seiner",
    "werden", "wurden", "vom", "zum", "zur", "im", "am", "aus", "als", "noch", "nur",
    "schon", "sehr", "wie", "was", "wer", "wo", "zu", "den", "dem", "des", "von", "in",
)

EN_FUNCTION_WORDS = _kw(
    "the", "and", "is", "a", "an", "to", "of", "in", "that", "it", "for", "as", "was",
    "with", "on", "be", "at", "this", "by", "from", "they", "we", "or", "will", "my",
    "one", "all", "would", "there", "their", "have", "has", "had", "been", "are", "were",
    "not", "but", "if", "when", "which", "who", "what", "can", "could", "should", "into",
    "about", "than", "then", "them", "these", "those", "her", "his", "its", "our", "your",
)

_BUILTIN_LANGUAGES: dict[str, LanguageSpec] = {
    "de": LanguageSpec(
        code="de",
        label="Deutsch",
        function_words=DE_FUNCTION_WORDS,
        profile_seed=(
            "Der die das und ist ein eine nicht auf mit fuer schon auch nach bei "
            "wird sind haben oder aber wenn ueber durch kann sein werden vom zum im am"
        ),
        signals={"eszett_boost": 0.25},
    ),
    "en": LanguageSpec(
        code="en",
        label="Englisch",
        function_words=EN_FUNCTION_WORDS,
        profile_seed=(
            "The and is a to of in that it for as was with on be at this by from "
            "they we or an will my one all would there their have has been are were not"
        ),
        signals={"eszett_penalty": 0.15},
    ),
}

_BUILTIN_DOMAINS: dict[str, DomainSpec] = {
    "general": DomainSpec(
        code="general",
        label_de="Allgemein",
        label_en="General",
        keywords={"de": frozenset(), "en": frozenset()},
        profile_seed={"de": "", "en": ""},
        min_confidence=0.0,
        min_keyword_hits=0,
    ),
    "medical": DomainSpec(
        code="medical",
        label_de="Medizin",
        label_en="Medicine",
        keywords={
            "de": _kw(
                "patient", "patientin", "diagnose", "therapie", "symptom", "symptome",
                "klinik", "krankenhaus", "arzt", "aerztin", "behandlung", "operation",
                "medikament", "krankheit", "infektion", "blut", "herz", "lunge", "tumor",
            ),
            "en": _kw(
                "patient", "diagnosis", "therapy", "symptom", "symptoms", "clinic",
                "hospital", "doctor", "physician", "treatment", "surgery", "medication",
                "disease", "infection", "blood", "heart", "lung", "tumor", "cancer",
            ),
        },
        profile_seed={
            "de": "Patient Diagnose Therapie Symptom Krebs Operation Klinik Arzt Behandlung Krankheit",
            "en": "Patient diagnosis therapy symptom cancer surgery clinic doctor treatment disease hospital",
        },
    ),
    "legal": DomainSpec(
        code="legal",
        label_de="Recht",
        label_en="Legal",
        keywords={
            "de": _kw(
                "vertrag", "paragraph", "klage", "gericht", "urteil", "anwalt", "anwaeltin",
                "mandant", "gesetz", "prozess", "recht", "rechtsanwalt", "kammer", "staatsanwalt",
                "verfassung", "strafe", "haft", "beweis", "zeuge",
            ),
            "en": _kw(
                "contract", "clause", "lawsuit", "court", "verdict", "attorney", "lawyer",
                "plaintiff", "defendant", "statute", "trial", "legal", "judge", "jury",
                "evidence", "witness", "sentence", "appeal", "regulation",
            ),
        },
        profile_seed={
            "de": "Vertrag Paragraph Klage Gericht Urteil Anwalt Mandant Gesetz Prozess Beweis Zeuge",
            "en": "Contract clause lawsuit court verdict attorney plaintiff defendant statute trial judge evidence",
        },
    ),
    "tech": DomainSpec(
        code="tech",
        label_de="Technik",
        label_en="Technology",
        keywords={
            "de": _kw(
                "software", "server", "algorithmus", "datenbank", "netzwerk", "programm",
                "programmierung", "computer", "system", "api", "cloud", "code", "entwickler",
                "hardware", "prozessor", "speicher", "verschluesselung", "protokoll",
            ),
            "en": _kw(
                "software", "server", "algorithm", "database", "network", "program",
                "programming", "computer", "system", "api", "cloud", "code", "developer",
                "hardware", "processor", "memory", "encryption", "protocol", "framework",
            ),
        },
        profile_seed={
            "de": "Software Server Algorithmus Datenbank Netzwerk Programm Computer System Cloud Entwickler",
            "en": "Software server algorithm database network program computer system cloud developer code",
        },
    ),
    "business": DomainSpec(
        code="business",
        label_de="Wirtschaft",
        label_en="Business",
        keywords={
            "de": _kw(
                "unternehmen", "umsatz", "markt", "investition", "kunde", "gewinn", "verlust",
                "aktie", "boerse", "börse", "finanz", "bank", "kredit", "verkauf", "kauf",
                "preis", "kosten", "budget", "strategie", "management",
            ),
            "en": _kw(
                "company", "revenue", "market", "investment", "customer", "profit", "loss",
                "stock", "finance", "bank", "credit", "sales", "purchase", "price", "cost",
                "budget", "strategy", "management", "shareholder", "quarter",
            ),
        },
        profile_seed={
            "de": "Unternehmen Umsatz Markt Investition Kunde Gewinn Finanz Bank Verkauf Strategie Management",
            "en": "Company revenue market investment customer profit finance bank sales strategy management stock",
        },
    ),
    "science": DomainSpec(
        code="science",
        label_de="Wissenschaft",
        label_en="Science",
        keywords={
            "de": _kw(
                "forschung", "studie", "hypothese", "experiment", "methode", "ergebnis",
                "daten", "analyse", "theorie", "modell", "messung", "probieren", "labor",
                "wissenschaft", "forscher", "publikation", "statistik",
            ),
            "en": _kw(
                "research", "study", "hypothesis", "experiment", "method", "result",
                "data", "analysis", "theory", "model", "measurement", "laboratory",
                "science", "scientist", "publication", "statistics", "sample", "variable",
            ),
        },
        profile_seed={
            "de": "Forschung Studie Hypothese Experiment Methode Ergebnis Daten Analyse Theorie Labor Wissenschaft",
            "en": "Research study hypothesis experiment method result data analysis theory laboratory science",
        },
    ),
    "education": DomainSpec(
        code="education",
        label_de="Bildung",
        label_en="Education",
        keywords={
            "de": _kw(
                "schule", "universitaet", "universität", "student", "studentin", "lehrer",
                "lehrerin", "lernen", "unterricht", "pruefung", "prüfung", "kurs", "seminar",
                "professor", "bildung", "klasse", "hausaufgabe", "abschluss",
            ),
            "en": _kw(
                "school", "university", "student", "teacher", "learning", "lesson", "exam",
                "course", "seminar", "professor", "education", "class", "homework",
                "degree", "curriculum", "campus", "enrollment",
            ),
        },
        profile_seed={
            "de": "Schule Universitaet Student Lehrer lernen Unterricht Pruefung Kurs Seminar Professor Bildung",
            "en": "School university student teacher learning lesson exam course seminar professor education class",
        },
    ),
    "news": DomainSpec(
        code="news",
        label_de="Nachrichten",
        label_en="News",
        keywords={
            "de": _kw(
                "berichtet", "meldet", "regierung", "minister", "ministerium", "wahl",
                "ereignis", "nachrichten", "presse", "journalist", "korrespondent",
                "parlament", "politik", "politisch", "behoerde", "behörde", "amt",
            ),
            "en": _kw(
                "reported", "reports", "government", "minister", "ministry", "election",
                "breaking", "officials", "news", "press", "journalist", "correspondent",
                "parliament", "political", "agency", "statement", "spokesperson",
            ),
        },
        profile_seed={
            "de": "Berichtet meldet Regierung Minister Wahl Ereignis Nachrichten Presse Journalist Parlament Politik",
            "en": "Reported government minister election breaking officials news press journalist parliament political",
        },
    ),
}

_LANGUAGES: dict[str, LanguageSpec] = dict(_BUILTIN_LANGUAGES)
_DOMAINS: dict[str, DomainSpec] = dict(_BUILTIN_DOMAINS)


def register_language(spec: LanguageSpec) -> None:
    _LANGUAGES[spec.code] = spec


def register_domain(spec: DomainSpec) -> None:
    _DOMAINS[spec.code] = spec


def get_language(code: str) -> LanguageSpec | None:
    return _LANGUAGES.get(code)


def iter_languages() -> list[LanguageSpec]:
    return list(_LANGUAGES.values())


def get_domain(code: str) -> DomainSpec | None:
    return _DOMAINS.get(code)


def iter_domains(*, active_only: bool = True) -> list[DomainSpec]:
    domains = list(_DOMAINS.values())
    if active_only:
        domains = [d for d in domains if d.code != "general"]
    return domains


def domain_label(spec: DomainSpec, lang_code: str) -> str:
    if lang_code == "en":
        return spec.label_en
    return spec.label_de

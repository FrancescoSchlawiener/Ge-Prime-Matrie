"""Text-Normalisierung und einheitliche UI-Hilfetexte (NORMALIZATION_HELP, INDEX_HELP, …)."""

import re
import unicodedata

from ge_prime.config import MAX_I_CURVE_TOKENS

_UMLAUT_MAP = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "AE",
    "Ö": "OE",
    "Ü": "UE",
}

# Schreibweise-Codes für die GPM-Case-Schicht
CASE_LOWER = 0       # alles klein
CASE_TITLE = 1       # erster Buchstabe groß, Rest klein
CASE_UPPER = 2       # ALLES GROSS
CASE_EXPLICIT = 3    # Mischfall — exakte Form wird separat gespeichert

# Einheitliche Erklärung für UI und Schritte
NORMALIZATION_HELP = {
    "umlauts": (
        "Umlaute werden vor der Berechnung in zwei Buchstaben geschrieben: "
        "ä/Ä → AE, ö/Ö → OE, ü/Ü → UE. Danach gilt nur noch das Alphabet A–Z und ß."
    ),
    "eszett": (
        "Das Eszett ß ist der 27. Buchstabe — mit der Primzahl 103. "
        "Es wird nicht in ss aufgeteilt und behält beim Encodieren seine Form."
    ),
    "eszett_example_1": (
        "Bei Straße bleibt das ß erhalten: das normalisierte Wort ist STRAßE — "
        "ein ß, also der Primfaktor 103 (nicht zwei S mit Primzahl 19)."
    ),
    "eszett_example_2": (
        "Strauß wird zu STRAUß — ebenfalls mit einem ß am Ende."
    ),
    "eszett_example_3": (
        "Strasse (geschrieben mit ss) wird zu STRASSE — zwei Buchstaben S. "
        "Das ist mathematisch ein anderes Wort als STRAßE, auch wenn es umgangssprachlich dasselbe bedeuten kann."
    ),
    "eszett_compare": (
        "Im Tab Vergleichen erkennt der ggT diesen Unterschied: Straße und Strasse teilen Buchstaben, "
        "aber ß zählt nur, wenn es wirklich im Wort steht."
    ),
    "letters": (
        "Es zählen 27 Buchstaben: A–Z und ß. "
        "Beim Encodieren einzelner Wörter werden Leerzeichen und Satzzeichen entfernt; "
        "in .gpm-Dateien bleiben sie im Text erhalten."
    ),
    "original": (
        "Wie du das Wort ursprünglich geschrieben hast (mit ß, Umlauten, Groß/Klein), "
        "wird in der Datenbank und in .gpm-Dateien zusätzlich gespeichert — "
        "damit der Text später exakt rekonstruiert werden kann."
    ),
    "decode_result": (
        "Decodieren aus S und I liefert zuerst die normalisierte Form "
        "(Großbuchstaben, ß bleibt ß). Umlaute erscheinen nur, wenn du die Originalschreibweise mitgeliefert hast."
    ),
    "compare": (
        "Zwei Wörter werden normalisiert und ihre Substanzen verglichen. "
        "Der ggT zeigt gemeinsame Buchstaben; der kgV die Vereinigungsmenge beider Wörter."
    ),
}

# Kurze, tab-spezifische Anleitungen (ohne Wiederholung der Norm-Regeltabelle)
TAB_GUIDE = {
    "encode": (
        "Schreib ein Wort — oder mehrere, durch Leerzeichen getrennt. "
        "Das Tool zieht daraus die Buchstaben, normalisiert still im Hintergrund und rechnet für jedes Wort S und I. "
        "Satzzeichen und Ziffern zwischen Wörtern werden hier ignoriert; "
        "für ganze Sätze mit Kommas, Zeilenumbrüchen oder Emoji nimm den Tab GPM Datei."
    ),
    "decode": (
        "Hier brauchst du die beiden Zahlen aus dem Encodieren: Substanz S und Index I. "
        "Nach dem Decodieren siehst du die normalisierte Form — also Großbuchstaben, ß bleibt ß. "
        "Ob du ursprünglich Müller oder MUELLER eingegeben hattest, erkennt man aus S und I allein nicht; "
        "dafür müsste die Originalschreibweise mitgespeichert sein (Datenbank oder .gpm)."
    ),
    "compare": (
        "Tipp zwei Wörter ein — beliebige Schreibweise. "
        "Im Hintergrund werden beide normalisiert; du siehst dann ggT (Schnittmenge der Buchstaben) "
        "und kgV (Vereinigung). "
        "Gut zum Ausprobieren: gleiche Bedeutung, andere Schreibung — oder Wörter mit gemeinsamen Buchstaben."
    ),
    "diff": (
        "Frag dich: Was bleibt von Wort 1 übrig, wenn alle gemeinsamen Buchstaben mit Wort 2 abgezogen werden? "
        "Oder: Haben beide dieselben Buchstaben, stehen sie aber in anderer Reihenfolge? "
        "Trage zwei Wörter ein — die Beispiele unten zeigen typische Fälle."
    ),
    "gpm": (
        "Hier kompiliert du ganzen Text: Wörter ins Genom, Abfolge in die Wort-Geometrie (I), "
        "technische Zellen (I_Satz) in der Zell-Kette, alles dazwischen in den Separator-Layer. "
        "Groß- und Kleinschreibung bleibt über eine eigene Schicht erhalten — "
        "Straße und straße sind dasselbe Wort im Genom, aber unterschiedlich rekonstruiert. "
        "Wie einzelne Buchstaben normalisiert werden, steht im Tab Konzept."
    ),
    "wortpaar": (
        "Zwei Wörter eingeben — dann wählst du oben Vergleichen (ggT und kgV) "
        "oder Differenz (S_rest, Teilmenge, Anagramm). Die Felder bleiben gleich."
    ),
    "ikurve": (
        "Ingest-Zeile (Plaintext oder .gpm) → I-Kurven vergleichen → geometrische Matrix A/B "
        "mit Spektroskopie-Markierung (Teal/Amber/Kreuzfeuer) und forensischem 3-Zonen-Labor."
    ),
    "cipher": (
        "Klartext oder Chiffretext eingeben, Modus und Schlüssel wählen, "
        "dann verschlüsseln oder entschlüsseln. Für .gpm-Dateien: Editor oben mit GPC-Checkbox."
    ),
    "datenbank": (
        "Übersicht aller gespeicherten Wörter nach Sprache. "
        "Neue Einträge kommen aus Encodieren oder aus Scraper-Läufen."
    ),
}

MATCHING_HELP = {
    "gcd_mode": (
        "ggT-Filter: ein Suchwort — findet Genom-Einträge mit gemeinsamen Primfaktoren "
        "(Schnittmenge der Buchstaben)."
    ),
    "lcm_mode": (
        "kgV-Filter: zwei Suchwörter — berechnet kgV(S₁, S₂) als Vereinigungsmenge. "
        "Ein Genom-Wort passt, wenn seine Substanz durch kgV teilbar ist (S % kgV == 0)."
    ),
    "lcm_example": (
        "Beispiel MUT und WUT: kgV enthält M, W, U und T — Genom-Wörter wie MUTWUT decken beide Begriffe ab."
    ),
    "substance_mode": "Exakter Substanz-Match: nur Wörter mit identischer Substanz S.",
}

DIFF_HELP = {
    "intro": (
        "Die arithmetische Differenz dividiert Substanz durch ggT: "
        "S_rest = S₁ ÷ ggT(S₁, S₂) — welche Buchstaben in Wort 1 übrig bleiben, "
        "wenn alle gemeinsamen Buchstaben mit Wort 2 abgezogen werden."
    ),
    "subset": (
        "Ist S_rest == 1 und S₁ ≠ S₂, enthält Wort 1 nur Buchstaben, die auch in Wort 2 vorkommen — "
        "eine echte Buchstaben-Teilmenge (Multimenge über Primfaktoren), nicht nur Gleichheit."
    ),
    "anagram": (
        "Bei S₁ = S₂ und I₁ ≠ I₂ haben beide Wörter dieselbe Buchstabenmenge, "
        "aber eine andere Anordnung — ein Anagramm, erkannt mit einer Index-Vergleichsoperation."
    ),
    "example_subset": (
        "Beispiel AT und CAT: ggT enthält A und T; S_rest für AT ist 1 — "
        "AT ist Buchstaben-Teilmenge von CAT."
    ),
    "example_anagram": (
        "Beispiel LISTEN und SILENT: gleiche Substanz S, unterschiedlicher Index I — perfektes Anagramm."
    ),
    "multiset_note": (
        "Hinweis: Es geht um die Multimenge der Buchstaben (Primfaktoren), "
        "nicht um ein zusammenhängendes Teilwort im Originalstring."
    ),
}


INDEX_HELP = {
    "intro": (
        "Der Index I ist die Position im Permutationsraum N pro Wort. "
        "Über die Token-Reihenfolge entsteht eine I-Kurve — der rhythmische Fingerabdruck der Satzgeometrie."
    ),
    "i_distance": (
        "Die I-Distanz misst Sprünge zwischen aufeinanderfolgenden Token (delta_ratio) — "
        "typische Satzstrukturen erzeugen ähnliche Sprungmuster im fraktalen Entscheidungsbaum."
    ),
    "plagiarism": (
        "Bei Synonym-Ersatz ändern sich Wörter und Substanz S; die I-Kurven über die Token-Positionen "
        "können dennoch strukturell parallel bleiben — ein Schatten der kopierten Satzgeometrie."
    ),
    "example": (
        "Vergleiche zwei Texte mit gleicher Satzstruktur aber anderen Wörtern: "
        "hoher Geometrie-Score bei niedrigem Literal-Match weist auf parallele I-Kurven hin."
    ),
    "limit_note": (
        "Es wird die Token-Geometrie verglichen, nicht Zeichen-für-Zeichen. "
        "Die Heuristik ersetzt kein juristisches Plagiatsgutachten."
    ),
    "icurve_token_max": f"{MAX_I_CURVE_TOKENS:,}".replace(",", "."),
    "source_note": (
        "Freitext wird kompiliert; eine geladene .gpm nutzt die gespeicherte Geometrie aus dem GPM-Tab."
    ),
    "meta_genome": (
        "Meta-Genom: alle Header-Substanzen nach Häufigkeit zu einem Dokumenten-Vektor V multipliziert — "
        "ggT(V₁, V₂) misst Domänen-Überlappung ohne die Datei zu öffnen."
    ),
    "meta_language": (
        "Sprache: Funktionswort-Muster (der/die/das vs. the/and/is) plus Referenz-Profil — "
        "aus der Wort-DB wenn genug Einträge vorhanden, sonst eingebaute Muster. "
        "Deutsch: zusätzliches ß-Signal. Bei niedriger Konfidenz: „Unklar“ — "
        "der DB-Sprachaudit nutzt dann die de/en-Score-Tendenz."
    ),
    "meta_plagiarism": (
        "Kombinierte Plagiats-Heuristik: I-Kurven-Geometrie plus Meta-Genom-ggT — "
        "starke Signale bei paralleler Satzstruktur und ähnlichem Fachvokabular."
    ),
    "cell_geometry": (
        "Zell-Geometrie (I_Satz): technische Segmente (≤50 Token, Gap-Split bei .!?) — "
        "jede Zelle hat ein Skelett (Häufigkeiten der Wort-Kategorien) und I_Satz im Permutationsraum. "
        "Vergleich der Zell-Ketten via DTW, weil Einfügungen die Grenzen verschieben."
    ),
    "cell_twins": (
        "Strukturelle Zell-Zwillinge: hoher Zell-DTW-Score bei niedrigem Literal-Match — "
        "gleicher Satzbau (Skelett + I_Satz), andere Wörter (Synonym-Ersatz oder strukturelle Kopie)."
    ),
    "substance_align": (
        "Substanz-Ausrichtung: ggT-Kette entlang der Token-Folge — misst Buchstaben-Überlappung "
        "unabhängig von I. Hoher Score bei Synonymen mit gleicher Substanz oder paralleler Buchstabenstruktur."
    ),
    "relation_domain": (
        "Relations-Profil: Domäne als Wort-Bigramme und Substanz-Paare, nicht nur Einzelwörter — "
        "geteilte Beziehungen deuten auf strukturelle Kopie des Satzbau-Musters hin."
    ),
    "db_language": (
        "DB-Sprachaudit: unique Token gegen die Wort-Datenbank (Modus de↔en, alle Sprachen oder Aus). "
        "Läuft auch bei „Unklar (hybrid)“ über die de/en-Score-Tendenz; "
        "Abdeckung = Anteil eindeutig in der audit-Sprache gespeicherter Wörter."
    ),
    "spectroscope": (
        "Spektroskopie in der geometrischen Matrix: Bereich markieren → Teal (Substanz-Teiler), "
        "Amber (Struktur-Zwilling), Kreuzfeuer (beides). Läuft über den eingefrorenen GPM-Cache "
        "nach dem Vergleich — kein erneutes Tippen im I-Kurve-Tab."
    ),
}


CIPHER_HELP = {
    "intro": (
        "Verschlüsselung auf Basis der Ge-Prime-Übersetzung: Wörter werden zu Substanz S "
        "und Index I; der Schlüssel kann ein Wort (→ Primzahlprodukt) oder eine Primzahl sein."
    ),
    "modes": (
        "Wort-, Primzahl-, S+I- und Hardcore-Modus — mit ehrlicher Sicherheitsbewertung. "
        "Hardcore wechselt mehrere Schlüssel (Wort oder prime:N) pro Token ab."
    ),
    "i_shadow": (
        "Die I-Geometrie bleibt im Chiffretext verborgen, solange der Schlüssel fehlt — "
        "analog zur I-Kurven-Analyse, die strukturelle Parallelen ohne Wortgleichheit erkennt."
    ),
    "limit_note": (
        "Symmetrische Demo-Verschlüsselung — kein Ersatz für AES. Max. 2.000 Token; "
        "Satzzeichen werden mitverschlüsselt (Separator-Schicht)."
    ),
    "hardcore_hint": (
        "Hardcore: kommagetrennt, z. B. GEHEIM, prime:17, ALPHA, prime:103 — "
        "Wörter und Primzahlen wechseln unabhängig voneinander."
    ),
    "gpm_encrypt": (
        "Im GPM-Editor optional als verschlüsselte .gpm speichern (Magic GPC): "
        "ohne Schlüssel liefert Lesen und Suche kein Genom — nur Entschlüsselung mit dem gleichen Schlüssel."
    ),
}


def normalize_text_nfc(text: str) -> str:
    """Canonical NFC for full strings at API/ingest boundaries (idempotent)."""
    text = unicodedata.normalize("NFC", text or "")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_word(word: str) -> str:
    """Uppercase, NFC, Umlaute expandieren; ß bleibt eigener Buchstabe (ẞ→ß)."""
    word = unicodedata.normalize("NFC", word.strip())
    for src, dst in _UMLAUT_MAP.items():
        word = word.replace(src, dst)
    word = word.replace("ẞ", "ß")
    return _eszett_aware_upper(word)


def _eszett_aware_upper(text: str) -> str:
    """Großschreibung, die ß als ß erhält (Pythons upper() würde ß→SS machen)."""
    return "".join(ch if ch == "ß" else ch.upper() for ch in text)


def _eszett_aware_full_upper(text: str) -> str:
    """ALLES GROSS inkl. ß → ẞ (echte Versalform des Eszett)."""
    return "".join("ẞ" if ch == "ß" else ch.upper() for ch in text)


def detect_case(run: str) -> int:
    """Bestimmt den Schreibweise-Code eines Original-Wortlaufs."""
    if not run:
        return CASE_LOWER
    if run == _lower(run):
        return CASE_LOWER
    if run == _full_upper(run):
        return CASE_UPPER
    if run == _title(run):
        return CASE_TITLE
    return CASE_EXPLICIT


def apply_case(run: str, code: int) -> str:
    """Wendet einen Schreibweise-Code auf einen (klein geschriebenen) Wortlauf an."""
    if code == CASE_UPPER:
        return _full_upper(run)
    if code == CASE_TITLE:
        return _title(run)
    return _lower(run)


def _lower(text: str) -> str:
    return "".join("ß" if ch in ("ß", "ẞ") else ch.lower() for ch in text)


def _full_upper(text: str) -> str:
    return _eszett_aware_full_upper(text)


def _title(text: str) -> str:
    lowered = _lower(text)
    if not lowered:
        return lowered
    first = lowered[0]
    first_up = "ẞ" if first == "ß" else first.upper()
    return first_up + lowered[1:]


def eszett_step_lines(original: str, normalized: str) -> list[str]:
    """Erklärungszeilen für ß in Encode-Schritten."""
    from ge_prime.core import PRIME_MAP

    lines: list[str] = []
    if "ß" in original or "ẞ" in original:
        prime = PRIME_MAP["ß"]
        lines.append(f"ß/ẞ bleibt eigener Buchstabe (Primzahl {prime}) → {normalized}")
    return lines


def denormalize_word(normalized: str, original: str | None = None) -> str:
    """Return original spelling when available; otherwise heuristic AE→Ä etc."""
    if original is not None:
        return original
    return _heuristic_denormalize(normalized)


def _heuristic_denormalize(normalized: str) -> str:
    """Best-effort reverse: AE→Ä, OE→Ö, UE→Ü (ambiguous for literal AE sequences)."""
    result = normalized
    for pair, umlaut in (("AE", "Ä"), ("OE", "Ö"), ("UE", "Ü")):
        result = re.sub(pair, umlaut, result)
    return result

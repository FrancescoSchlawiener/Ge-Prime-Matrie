"""CLI-Demos für Ge-Prime-Matrix.

Ausführung: ``dev.bat main.py`` (Windows) bzw. ``python main.py``.

Demos:
  demo_encode_decode — Normalisierung, S/I, Rekonstruktion
  demo_compare       — ggT und kgV
  demo_diff          — Teilmenge, Anagramm
  demo_i_curve       — I-Kurven-Vergleich und Geometrie-Score
  demo_cipher        — S(I)-Verschlüsselung (word, hardcore)
  demo_db            — Wörter in SQLite speichern
"""

from ge_prime.compare import compare_substances
from ge_prime.diff import classify_word_pair
from ge_prime.decode import decode_word
from ge_prime.encode import encode_word
from ge_prime.i_curve import analyze_pair
from db.repository import WordRepository
from pipeline.normalize import denormalize_word, normalize_word


def demo_encode_decode():
    test_woerter = ["Straße", "Strasse", "Strauß", "Müller", "FRÄULEIN", "ROBOTERHEIT"]

    for wort in test_woerter:
        print(f"--- Starte Prozess für: {wort} ---")
        normalized = normalize_word(wort)
        S, I = encode_word(normalized)
        rekonstruktion = decode_word(S, I)
        display = denormalize_word(normalized, wort)
        print(f"Original:      {wort}")
        print(f"Normalisiert:  {normalized}")
        print(f"Anzeige:       {display}")
        print(f"Substanz (S):  {S}")
        print(f"Index (I):     {I}")
        print(f"Rekonstruiert: {rekonstruktion}\n")


def demo_compare():
    pairs = [("Straße", "Strasse"), ("SCHAUER", "SCHULE")]
    print("=== ggT- und kgV-Vergleich ===\n")
    for w1, w2 in pairs:
        n1, n2 = normalize_word(w1), normalize_word(w2)
        s1, _ = encode_word(n1)
        s2, _ = encode_word(n2)
        cmp = compare_substances(s1, s2)
        print(f"{w1} vs {w2}: ggT={cmp['gcd_value']}, kgV={cmp['lcm_value']}, Ähnlichkeit={cmp['similarity_ratio']:.4f}")
        print(f"  normalisiert: {n1} / {n2}")
        print(f"  gemeinsam: {cmp['shared_letters']}")
        print(f"  union: {cmp['union_letters']}\n")


def demo_diff():
    pairs = [("AT", "CAT"), ("LISTEN", "SILENT")]
    print("=== Arithmetische Differenz ===\n")
    for w1, w2 in pairs:
        n1, n2 = normalize_word(w1), normalize_word(w2)
        s1, i1 = encode_word(n1)
        s2, i2 = encode_word(n2)
        diff = classify_word_pair(s1, s2, i1, i2, norm_len1=len(n1), norm_len2=len(n2))
        print(f"{w1} vs {w2}: ggT={diff['gcd_value']}, S_rest₁={diff['remainder_s1']}, S_rest₂={diff['remainder_s2']}")
        print(
            f"  Teilmenge 1⊆2={diff['is_subset_1_in_2']}, "
            f"Anagramm={diff['is_anagram']}, Identisch={diff['is_identical']}"
        )
        print(f"  Rest-Buchstaben Wort 1: {diff['remainder_letters_s1']}\n")


def demo_i_curve():
    pairs = [
        ("Der schnelle braune Fuchs springt.", "Der schnelle braune Fuchs springt."),
        (
            "Der schnelle braune Fuchs springt.",
            "Ein flinker brauner Fuchs hüpft hoch.",
        ),
    ]
    print("=== I-Kurven-Vergleich ===\n")
    for text_a, text_b in pairs:
        result = analyze_pair(text_a=text_a, text_b=text_b)
        c = result["comparison"]
        print(f"A: {text_a[:40]}…")
        print(f"B: {text_b[:40]}…")
        print(
            f"  Geometrie={c['geometry_score']:.3f}, "
            f"Literal={c['literal_match_ratio']:.3f}, "
            f"Wellenform-parallel={c['structural_waveform_parallel']}"
        )
        print(f"  {c['interpretation']}\n")


def demo_cipher():
    from ge_prime.cipher import MODE_HARDCORE, MODE_WORD, decrypt_ciphertext, encrypt_text

    text = "Geheim: Der Fuchs springt!"
    print("=== S(I)-Verschlüsselung ===\n")
    for mode, keys in [
        (MODE_WORD, "ALPHA"),
        (MODE_HARDCORE, "GEHEIM, prime:17, BETA, prime:103"),
    ]:
        enc = encrypt_text(text, mode=mode, keys_raw=keys)
        dec = decrypt_ciphertext(enc["ciphertext"], keys_raw=keys)
        sec = enc["security"]
        print(f"Modus {mode}: Score={sec['score']}, Stufe={sec['level']}")
        print(f"  Match: {dec['text'] == text}\n")


def demo_db():
    from pipeline.process import process_word

    repo = WordRepository()
    repo.init_db()
    source_id = repo.get_or_create_source("demo", "local")
    entries = []
    for w in ["HALLO", "Straße", "MÜLLER"]:
        r = process_word(w, source="demo")
        if r:
            entries.append(r)
    stats = repo.insert_words_batch(entries, source_id)
    print(f"DB demo: inserted={stats.inserted}, duplicates={stats.duplicates}, total={repo.total_count()}")
    repo.close()


def main():
    demo_encode_decode()
    demo_compare()
    demo_diff()
    demo_i_curve()
    demo_cipher()
    demo_db()


if __name__ == "__main__":
    main()

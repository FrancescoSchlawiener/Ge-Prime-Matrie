export const feedback = {
  progress: {
    operation: "Operation",
    working: "Arbeitet …",
    polling: "Warte auf Ergebnis …",
    start: "Starte …",
  },
  errors: {
    document_ref_not_found: "Dokument-Referenz nicht gefunden.",
    cipher_key_required: "Cipher-Schlüssel erforderlich.",
    gpm_invalid_stream: "Ungültiger GPM-Stream.",
    value_error: "Ungültige Eingabe.",
    http_error: "HTTP-Fehler.",
    job_not_found: "Job nicht gefunden.",
    job_failed: "Job fehlgeschlagen.",
    cache_miss: "Cache-Miss — neu kompiliert.",
  },
} as const;

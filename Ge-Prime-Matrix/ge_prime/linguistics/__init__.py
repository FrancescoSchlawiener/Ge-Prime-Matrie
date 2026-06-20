"""Sprach- und Domänenerkennung für Meta-Genom / I-Kurve."""

from ge_prime.linguistics.domain import classify_domain
from ge_prime.linguistics.language import classify_language, infer_text_language_code, resolve_db_audit_language
from ge_prime.linguistics.profiles import build_prime_profile, clear_profile_caches, resolve_linguistics_repo
from ge_prime.linguistics.registry import (
    DomainSpec,
    LanguageSpec,
    register_domain,
    register_language,
)

__all__ = [
    "LanguageSpec",
    "DomainSpec",
    "register_language",
    "register_domain",
    "classify_language",
    "infer_text_language_code",
    "resolve_db_audit_language",
    "classify_domain",
    "build_prime_profile",
    "clear_profile_caches",
    "resolve_linguistics_repo",
]

"""Pädagogik-Schritte für gestaffelten Dokument-Vergleich."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered
from analysis.document.model import GpmDocument
from api.schemas.common import Step


def _tier_result_to_dict(result) -> dict:
    data = asdict(result) if is_dataclass(result) else dict(result)
    if "stopped_at" in data and data["stopped_at"] is not None:
        stopped = data["stopped_at"]
        data["stopped_at"] = stopped.name if hasattr(stopped, "name") else int(stopped)
    return data


def build_tiered_compare_steps(
    doc_a: GpmDocument,
    doc_b: GpmDocument,
    tier: int,
) -> tuple[dict, list[Step]]:
    max_tier = CompareTier(min(max(tier, 0), 4))
    result = compare_documents_tiered(doc_a, doc_b, max_tier=max_tier)
    payload = _tier_result_to_dict(result)
    tier_audit = [
        {
            "tier": name,
            "stopped": payload.get("stopped_at"),
            "zero_reason": result.zero_reason,
        }
        for name in result.tiers_run
    ]
    steps = [
        Step(
            id="tier_gate",
            title=f"Tier 0–{max_tier.value} Vergleich",
            detail="Gestaffelter Dokument-Vergleich mit frühem Abbruch.",
            values={
                "tiers_run": ", ".join(result.tiers_run),
                "final_score": round(result.final_score, 6),
                "stopped_at": str(payload.get("stopped_at")),
            },
        ),
    ]
    if result.zero_reason:
        steps.append(
            Step(
                id="zero_reason",
                title="Abbruchgrund",
                detail=result.zero_reason,
                values={"zero_reason": result.zero_reason},
            )
        )
    payload["tier_audit"] = tier_audit
    return payload, steps

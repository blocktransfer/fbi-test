"""Pure aggregate statistical *planning aid* for Compact Council §4.01(a).

Simple random sampling finite-population estimate, conservative p=0.5.
A numerical estimate alone is NOT a representative audit methodology, nor
an approved combined state/federal program or an actual sampled audit.
"""
from __future__ import annotations
from math import ceil


class SamplingInputError(ValueError):
    pass


_Z = {90: 1.645, 95: 1.96, 99: 2.576}
_FIELDS = frozenset({
    "channeler_population", "recipient_population",
    "confidence_percent", "margin_percent", "method",
})


def _required_count(value: object) -> int:
    if type(value) is not int or not 0 <= value <= 1_000_000:
        raise SamplingInputError("Population counts must be nonnegative integers up to one million")
    return value


def sample_size(population: int, confidence_percent: int, margin_percent: int) -> int:
    """SRS estimate with finite population correction, rounded upwards."""
    if population == 0:
        return 0
    z = _Z[confidence_percent]
    error = margin_percent / 100
    variance = z * z * 0.25
    return min(population, ceil(population * variance / (error * error * (population - 1) + variance)))


def estimate(data: dict) -> dict:
    if type(data) is not dict or set(data) != _FIELDS:
        raise SamplingInputError("Only population counts, confidence, margin and sampling method are allowed")
    c = _required_count(data["channeler_population"])
    r = _required_count(data["recipient_population"])
    confidence = data["confidence_percent"]
    margin = data["margin_percent"]
    if type(confidence) is not int or confidence not in _Z:
        raise SamplingInputError("Confidence must be 90, 95 or 99 percent")
    if type(margin) is not int or margin not in (2, 5, 10):
        raise SamplingInputError("Margin must be 2, 5 or 10 percent")
    if type(data["method"]) is not str or data["method"] != "simple_random":
        raise SamplingInputError("Only aggregate simple-random-planning estimates are supported")
    return {
        "section": "4.01(a)",
        "method": "finite_population_srs_approximation",
        "confidence_percent": confidence,
        "margin_percent": margin,
        "channeler_sample_estimate": sample_size(c, confidence, margin),
        "recipient_sample_estimate": sample_size(r, confidence, margin),
        "conservative_assumed_proportion": 0.5,
        "entities_selected": False,
        "representative_sample_verified": False,
        "combined_state_federal_audit_program_approved": False,
        "sample_audit_conducted": False,
        "production_ready": False,
        "limitations": (
            "Statistical sample-size estimate only; does not construct a sampling frame, "
            "stratify roles or jurisdictions, select entities, test nonresponse, verify coverage "
            "or substitute for generally accepted sampling methodology established by officials."
        ),
    }

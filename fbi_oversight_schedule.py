"""Section 4 FBI/Compact Officer scheduling, for synthetic planning only.

No dates are proof an audit occurred and no API request performs an FBI
check, assigns OCA/ORI, grants approval, or publishes a regulator's decision.
"""
from __future__ import annotations
from calendar import monthrange
from datetime import datetime, timedelta
from incident_deadlines import _timestamp, DeadlineError


class OversightInputError(ValueError):
    pass


EVENTS = frozenset({
    "policy_update_notification",  # §4.02
    "personnel_access_change",      # §4.04
    "first_approved_chri_receipt",   # §§4.01(a), 4.03
})
# Numeric schedules need trigger dates; other §4 duties have no numeric clock.
SUPPORTED_FIELDS = frozenset({"event", "occurred_at", "as_of"})


def _utc(value) -> datetime:
    try:
        return _timestamp(value)
    except (DeadlineError, TypeError, AttributeError) as exc:
        raise OversightInputError("Use a timezone-explicit UTC timestamp") from exc


def anniversary(value: datetime, years: int) -> datetime:
    """Calendar-year anniversary, adjusting leap-day to February 28."""
    target_year = value.year + years
    return value.replace(
        year=target_year,
        day=min(value.day, monthrange(target_year, value.month)[1]),
    )


def _next_triennial(start: datetime, as_of: datetime) -> datetime:
    years = 3
    while anniversary(start, years) <= as_of:
        years += 3
    return anniversary(start, years)


def deadlines(data: dict) -> dict:
    if type(data) is not dict or set(data) != SUPPORTED_FIELDS:
        raise OversightInputError("Only event, occurrence and inspection UTC times are permitted")
    event = data["event"]
    if type(event) is not str or event not in EVENTS:
        raise OversightInputError("Unrecognized FBI/Compact Officer oversight event")
    occurred = _utc(data["occurred_at"])
    as_of = _utc(data["as_of"])
    if as_of < occurred:
        raise OversightInputError("Inspection time cannot precede event")
    result = {
        "event": event,
        "trigger_utc": occurred.isoformat(),
        "as_of_utc": as_of.isoformat(),
        "source": "Compact Council Channeling Standard §4, printed page 8",
        "recipients_notified": False,
        "audits_conducted": False,
        "certification_delivered": False,
        "background_checks_completed": False,
        "agency_approval_verified": False,
        "real_chri_processed": False,
        "production_ready": False,
    }
    if event == "policy_update_notification":
        deadline = occurred + timedelta(days=60)
        result.update({
            "section": "4.02",
            "policy_versions_available_by_utc": deadline.isoformat(),
            "deadline_elapsed": as_of >= deadline,
            "responsible_party": "FBI",
            "notes": "Current Standard and CJISSECPOL to be made available to Channelers within 60 calendar days after notification unless otherwise directed. No version delivered here.",
        })
    elif event == "personnel_access_change":
        deadline = occurred + timedelta(hours=24)
        result.update({
            "section": "4.04",
            "access_roster_updated_by_utc": deadline.isoformat(),
            "deadline_elapsed": as_of >= deadline,
            "responsible_party": "FBI",
            "notes": "FBI updates its CHRI-access personnel roster within 24 hours; individual criminal-history checks and passed-check list remain FBI responsibilities.",
        })
    else:
        ninety = occurred + timedelta(days=90)
        one_year = anniversary(occurred, 1)
        three_year = anniversary(occurred, 3)
        result.update({
            "sections": ["4.01(a)", "4.03"],
            "fbi_initial_audit_and_certification_due_utc": ninety.isoformat(),
            "fbi_one_year_audit_reference_utc": one_year.isoformat(),
            "fbi_first_triennial_audit_reference_utc": three_year.isoformat(),
            "fbi_next_triennial_audit_reference_utc": _next_triennial(occurred, as_of).isoformat(),
            "combined_state_federal_first_sample_audit_due_utc": one_year.isoformat(),
            "combined_state_federal_first_triennial_reference_utc": three_year.isoformat(),
            "combined_state_federal_next_triennial_reference_utc": _next_triennial(occurred, as_of).isoformat(),
            "representative_sampling_required": True,
            "fbi_certification_requires_copy_of_audit_results": True,
            "ninety_day_deadline_elapsed": as_of >= ninety,
            "responsible_parties": {
                "channeler_audit": "FBI",
                "combined_sample_program": "Compact Officer/Chief Administrator implementing combined state/federal audits",
            },
            "scheduling_assumption": (
                "Only the first 90-day certification and first combined sample-audit deadline "
                "are explicitly tied by §4 to first CHRI receipt. The one-year and triennial "
                "illustrative dates use first receipt as a planning anchor, not a "
                "source-specified exact due date or evidence of agreement execution."
            ),
            "notes": (
                "First FBI audit certification and copy of results go to FBI Compact Officer "
                "within 90 calendar days after first approved CHRI receipt. "
                "Combined representative-sample audits require generally accepted statistical "
                "sampling methods and must be in place before permission is granted."
            ),
        })
    return result

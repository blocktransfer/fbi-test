"""Strict nonidentifying Channeler §3 planning and safety gates.

ALL operations are dry-run calculations. No actual CJI/CHRI, employee
identifiers, fingerprint images, or Rap Back identifiers are accepted,
retained, transmitted, validated, or deleted by this module.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from calendar import monthrange
from incident_deadlines import _timestamp, DeadlineError

class ChannelerInputError(ValueError):
    pass

EVENTS = frozenset((
    "policy_update_received", "pii_breach_discovered", "security_violation_discovered",
    "contract_termination_discovered", "employee_access_changed",
    "recipient_exchange_terminated", "early_voluntary_termination",
))
DEADLINE_FIELDS = frozenset(("event", "occurred_at"))
RETENTION_FIELDS = frozenset(("received_at", "acknowledged_at", "as_of"))
TRAINING_FIELDS = frozenset((
    "agreement_anniversary", "last_training_at", "assignment_at",
    "recipient_retains_training_by_contract", "as_of"
))
RAPBACK_FIELDS = frozenset((
    "subscription_started_at", "as_of", "recipient_has_validated",
    "fbi_testing_and_approval_reported", "purpose"
))

def utc(value: str) -> datetime:
    try:
        return _timestamp(value)
    except (DeadlineError, TypeError, AttributeError) as exc:
        raise ChannelerInputError("A valid timezone-explicit UTC timestamp is required") from exc

def _schema(data: dict, required: frozenset, permitted: frozenset) -> None:
    if type(data) is not dict or not required.issubset(data) or set(data) - permitted:
        raise ChannelerInputError("Only specified event/time and nonidentifying status fields are permitted")

def plus_year(value: datetime) -> datetime:
    """Calendar anniversary, with Feb. 29 falling back to Feb. 28."""
    year = value.year + 1
    return value.replace(year=year, day=min(value.day, monthrange(year, value.month)[1]))

def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None

def deadlines(data: dict) -> dict:
    """§§3.03–3.04, 3.15, 3.17–3.18: never transmit a notification."""
    _schema(data, DEADLINE_FIELDS, DEADLINE_FIELDS)
    event = data["event"]
    if type(event) is not str or event not in EVENTS:
        raise ChannelerInputError("Unknown Section 3 event")
    occurred = utc(data["occurred_at"])
    first_due = None
    report_due = None
    recipients = ""
    sections = []
    instruction = ""
    if event == "policy_update_received":
        first_due = occurred + timedelta(days=60)
        recipients = "Authorized Recipient"
        sections = ["3.04"]
        instruction = "Notify Recipient of update and provide current policy versions within 60 calendar days unless otherwise directed."
    elif event in ("pii_breach_discovered", "security_violation_discovered", "contract_termination_discovered"):
        first_due = occurred + timedelta(hours=1 if event == "pii_breach_discovered" else 4)
        report_due = occurred + timedelta(days=5) if event != "contract_termination_discovered" else None
        recipients = "Authorized Recipient, Compact Officer/Chief Administrator and FBI"
        sections = ["3.15"]
        instruction = "Written report of a security violation due within five calendar days of DISCOVERY, including corrective actions, summary, occurrence time, intent and frequency." if report_due else "Notify all required recipients within four hours of contract termination discovery."
    elif event == "employee_access_changed":
        first_due = occurred + timedelta(hours=24)
        recipients = "FBI"
        sections = ["3.18"]
        instruction = "Update employee-access records AND notify FBI within 24 hours; suspend CHRI-access assignments immediately if employee committed a security violation (§3.21)."
    elif event == "recipient_exchange_terminated":
        recipients = "Authorized Recipient and approved data custodians"
        sections = ["3.17"]
        instruction = "Delete or return CHRI records and media as prescribed by CJISSECPOL and the outsourcing agreement; no automatic deletion is performed."
    else:
        recipients = "Compact Officer/Chief Administrator and FBI"
        sections = ["3.03"]
        instruction = "Written notice of early voluntary termination is required; §3.03 supplies no numeric deadline."
    return {
        "event": event, "sections": sections,
        "initial_due_utc": _iso(first_due),
        "written_report_due_utc": _iso(report_due),
        "report_deadline_basis": "discovery" if report_due else None,
        "recipients": recipients, "instruction": instruction,
        "messages_sent": False, "personal_information_collected": False,
        "externally_verified": False, "production_ready": False,
    }

def retention_dry_run(data: dict) -> dict:
    """§3.12: earliest confirmed receipt or 30 calendar days, not deletion."""
    _schema(data, frozenset({"received_at", "as_of"}), RETENTION_FIELDS)
    received = utc(data["received_at"])
    now = utc(data["as_of"])
    if now < received:
        raise ChannelerInputError("Inspection time precedes hypothetical CHRI receipt")
    end = received + timedelta(days=30)
    acknowledged = None
    if "acknowledged_at" in data:
        acknowledged = utc(data["acknowledged_at"])
        if acknowledged < received:
            raise ChannelerInputError("Recipient acknowledgment precedes receipt")
        end = min(end, acknowledged)
    return {
        "section": "3.12", "destroy_by_utc": _iso(end),
        "dissemination_availability_end_utc": _iso(received + timedelta(days=30)),
        "requires_immediate_destruction_after_confirmed_receipt": acknowledged is not None,
        "overdue": now >= end,
        "destruction_performed": False, "actual_chri_present": False,
        "contractual_method_and_timing_required": True,
    }

def training_dry_run(data: dict) -> dict:
    """§3.19: a personnel scheduler, never a training certification."""
    _schema(data, frozenset({"agreement_anniversary", "assignment_at",
                              "recipient_retains_training_by_contract", "as_of"}), TRAINING_FIELDS)
    retained = data["recipient_retains_training_by_contract"]
    if type(retained) is not bool:
        raise ChannelerInputError("The Recipient-retained training flag must be boolean")
    anniversary = utc(data["agreement_anniversary"])
    assigned = utc(data["assignment_at"])
    now = utc(data["as_of"])
    if assigned < anniversary:
        raise ChannelerInputError("Assignment predates hypothetical agreement")
    last = utc(data["last_training_at"]) if "last_training_at" in data else None
    if last is not None and last > now:
        raise ChannelerInputError("Training cannot be completed in the future")
    preassignment_ok = last is not None and last <= assigned
    refresher_due = plus_year(last) if last else None
    certification_due = anniversary
    while certification_due <= now:
        certification_due = plus_year(certification_due)
    return {
        "section": "3.19",
        "recipient_retains_training_by_contract_reported": retained,
        "channeler_training_duty_applies": not retained,
        "preassignment_training_reported": preassignment_ok,
        "next_training_due_utc": _iso(refresher_due),
        "next_fbi_certification_anniversary_utc": _iso(certification_due) if not retained else None,
        "completed_training_verified": False, "fbi_certification_sent": False,
        "staff_access_enabled": False,
    }

def rapback_dry_run(data: dict) -> dict:
    """§§3.22–3.25: messaging logistics never make validation decisions."""
    _schema(data, RAPBACK_FIELDS, RAPBACK_FIELDS)
    if data["purpose"] != "synthetic_only":
        raise ChannelerInputError("Only synthetic Rap Back planning is available")
    for key in ("recipient_has_validated", "fbi_testing_and_approval_reported"):
        if type(data[key]) is not bool:
            raise ChannelerInputError("Rap Back flags must be boolean")
    start = utc(data["subscription_started_at"])
    now = utc(data["as_of"])
    if now < start:
        raise ChannelerInputError("Inspection date precedes subscription")
    anniversary = plus_year(start)
    while anniversary <= now:
        anniversary = plus_year(anniversary)
    return {
        "sections": ["3.22", "3.23", "3.24", "3.25"],
        "next_annual_validation_message_utc": _iso(anniversary),
        "validation_authority": "Authorized Recipient only",
        "recipient_validation_reported": data["recipient_has_validated"],
        "fbi_testing_reported_but_unverified": data["fbi_testing_and_approval_reported"],
        "real_subscription_or_applicant_identifiers_stored": False,
        "applicant_pii_accepted": False,
        "validation_performed": False,
        "rapback_messages_sent": False,
        "rapback_service_enabled": False,
        "fbi_approval_verified": False,
    }

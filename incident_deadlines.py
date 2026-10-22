"""Nonpersistent notification deadlines from two supplied primary policies.

This planner neither records incident details nor sends mandatory notifications.
The actual role, legal duties, discovery facts, and contact routes require human
confirmation. It accepts only categories and timestamps: never CJI or PII.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class DeadlineError(ValueError):
    pass


CATEGORIES = frozenset({"pii_breach", "security_violation", "agreement_termination"})
ROLES = frozenset({"authorized_recipient", "channeler"})


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str) or len(value) > 35:
        raise DeadlineError("UTC timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DeadlineError("UTC timestamp required") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DeadlineError("Timestamp must include UTC timezone")
    return parsed.astimezone(timezone.utc)


def incident_deadlines(request: dict) -> dict:
    """Compute notification deadlines without storing or sending a report."""
    if not isinstance(request, dict) or set(request) not in (
        {"role", "category", "discovered_at"},
        {"role", "category", "discovered_at", "initial_notice_at"},
    ):
        raise DeadlineError("Only the role, category and UTC times are permitted")
    role, category = request["role"], request["category"]
    if role not in ROLES or category not in CATEGORIES:
        raise DeadlineError("Select the applicable role and incident category")
    discovered = _timestamp(request["discovered_at"])
    initial_notice = None
    if "initial_notice_at" in request:
        initial_notice = _timestamp(request["initial_notice_at"])
        if initial_notice < discovered:
            raise DeadlineError("Initial notification cannot precede discovery")
    # PII breach: 1 hour. Other security violations and termination: 4 hours.
    external_hours = 1 if category == "pii_breach" else 4
    external_due = discovered + timedelta(hours=external_hours)
    # CJIS IR-6 requires organizational reporting immediately, <=1 hour
    # after discovery of a suspected incident (not contract termination alone).
    internal_due = None if category == "agreement_termination" else discovered + timedelta(hours=1)
    if role == "authorized_recipient":
        written_due = None if initial_notice is None else initial_notice + timedelta(days=5)
        written_basis = "Five calendar days from initial notification (Outsourcing 2.08)"
        recipients = "Compact Officer/Chief Administrator and FBI"
    else:
        written_due = discovered + timedelta(days=5)
        written_basis = "Five calendar days from discovery (Outsourcing 3.15)"
        recipients = "Authorized Recipient, Compact Officer/Chief Administrator, and FBI"
    return {
        "role": role,
        "category": category,
        "internal_incident_report_due_utc": internal_due.isoformat() if internal_due else None,
        "external_notification_due_utc": external_due.isoformat(),
        "written_report_due_utc": written_due.isoformat() if written_due else None,
        "written_report_basis": written_basis,
        "external_recipients": recipients,
        "security_policy_reference": "CJIS Security Policy v6.1 IR-6, printed page 171",
        "outsourcing_reference": "2.08, PDF page 9" if role == "authorized_recipient" else "3.15, PDF page 13",
        "automatically_notified": False,
        "incident_details_collected": False,
    }

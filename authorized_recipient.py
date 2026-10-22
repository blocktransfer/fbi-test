"""Authorized Recipient responsibilities, Compact Council Channeling Standard §2.

Source: Security and Management Control Outsourcing Standard for Channeling,
approved November 29, 2023, PDF pp. 8–10 (§§2.01–2.14).

This module records operator checklists and calculates deadlines. It neither
verifies FBI approvals nor collects applicant/CHRI/PII records or sends notices.
"""
from __future__ import annotations

from datetime import timedelta
from incident_deadlines import _timestamp, DeadlineError


class RecipientError(ValueError):
    """Unrecognized or unsafe Authorized Recipient workflow data."""


# Each checklist entry is an operator-declared activity, never independently
# verified legal compliance. The optional flag reflects whether the Standard
# describes the action as an option, not a waiver of applicable obligations.
CHECKS = (
    ("2.01", "permission", "Obtain written Compact Officer/Chief Administrator permission before using a Channeler", False),
    ("2.01", "authority", "Include specific legal authority for nationwide fingerprint-based checks in the written request", False),
    ("2.01", "populations", "Describe the specific populations to be submitted in the written request", False),
    ("2.01", "arpoc", "Include Authorized Recipient Point of Contact information in the written request", False),
    ("2.01", "correct_officer", "Route request to the State Compact Officer/Chief Administrator or FBI Compact Officer as §2.01(a)-(b) directs", False),
    ("2.02", "agreement", "Execute agreement before granting Channeler CHRI access", False),
    ("2.02", "incorporation", "Incorporate Outsourcing Standard and CJIS Security Policy into agreement by reference", False),
    ("2.02", "disclosure", "Be prepared to supply CHRI-related portions of current agreement to oversight officials on request", False),
    ("2.03", "current_versions", "Incorporate latest policy and standard at agreement/renewal or within update-notification period, whichever sooner", False),
    ("2.04", "access_terms", "Specify terms and conditions of any Channeler access to CHRI", False),
    ("2.04", "purpose_limit", "Limit CHRI use to the purposes for which provided", False),
    ("2.04", "no_unauthorized_dissemination", "Prohibit dissemination except as authorized by governing law and Compact rules", False),
    ("2.04", "confidentiality", "Require CHRI security and confidentiality", False),
    ("2.04", "audits_sanctions", "Include FBI audit rights and Compact Council sanctions", False),
    ("2.04", "termination", "Specify contract/agreement termination conditions", False),
    ("2.05", "dataflow", "Document understanding of how the Channeler processes and transmits CHRI", False),
    ("2.06", "arpoc_change_notice", "Notify Compact Officer/Chief Administrator and FBI within 30 calendar days of ARPOC change", False),
    ("2.07", "arso_appointment", "Appoint an Authorized Recipient Security Officer", False),
    ("2.07", "arso_initial_notice", "Notify Compact Officer/Chief Administrator and FBI of ARSO contact within 30 calendar days of initial approval", False),
    ("2.07", "arso_change_notice", "Notify Compact Officer/Chief Administrator and FBI within 30 calendar days of ARSO changes", False),
    ("2.08", "pii_notice", "Notify Compact Officer/Chief Administrator and FBI within one hour of a PII breach discovery", False),
    ("2.08", "violation_notice", "Notify Compact Officer/Chief Administrator and FBI within four hours of other security violation or termination discovery", False),
    ("2.08", "written_report", "Submit written report within five calendar days after initial notification of breach or violation", False),
    ("2.08", "written_contents", "Report corrective actions, Channeler name, OCA, summary, occurrence time, intent, and occurrence count", False),
    ("2.09", "termination_rights", "Document grounds for security-violation termination (violation, missing report, refusal/inability to correct)", True),
    ("2.10", "suspension", "Track possible suspension if security violation is not reported", False),
    ("2.10", "reinstatement", "Require satisfactory written assurances to Compact Council Chair or Attorney General before treating CHRI exchange as reinstated", False),
    ("2.11", "inspections", "Make facilities available for announced and unannounced state/FBI audits and inspections", False),
    ("2.12", "optional_audits", "Consider or conduct optional Authorized Recipient audits of Channeler", True),
    ("2.13", "stricter_requirements", "Consider more stringent site security requirements", True),
    ("2.14", "voluntary_termination_notice", "Provide written notice of early voluntary termination to Compact Officer/Chief Administrator and FBI", False),
)
SOURCE = {
    "title": "Security and Management Control Outsourcing Standard for Channeling",
    "authority": "National Crime Prevention and Privacy Compact Council",
    "approved": "2023-11-29",
    "section": "Section 2 — Responsibilities of the Authorized Recipient",
    "pdf_pages": "8–10",
}
SPEC = {section + "." + short: (section, short, label, optional)
        for section, short, label, optional in CHECKS}
EVENTS = frozenset((
    "initial_outsourcing_approval",
    "arpoc_change",
    "arso_change",
    "policy_update_notice",
    "pii_breach",
    "security_violation",
    "contract_termination",
    "early_voluntary_termination",
))


def catalog() -> dict:
    return {
        "source": dict(SOURCE), "sections": [f"2.{i:02d}" for i in range(1, 15)],
        "control_count": len(CHECKS),
        "operator_attestation_only": True,
        "independently_verified": False,
        "production_ready": False,
        "controls": [
            {"id": section + "." + short, "section": section, "description": description,
             "optional": optional, "pdf_page": "8" if int(section[2:]) <= 4
             else ("9" if int(section[2:]) <= 8 else "10")}
            for section, short, description, optional in CHECKS
        ],
    }


def deadlines(data: dict) -> dict:
    """Calendar-day and hour deadlines derived solely from §2 text."""
    if not isinstance(data, dict) or set(data) - {"event", "occurred_at", "initial_notice_at", "renewal_at"}:
        raise RecipientError("Only event type and UTC timestamps are allowed")
    if "event" not in data or "occurred_at" not in data:
        raise RecipientError("Event type and occurrence time required")
    event = data["event"]
    if type(event) is not str or event not in EVENTS:
        raise RecipientError("Unsupported Authorized Recipient event")
    if "initial_notice_at" in data and event not in ("pii_breach", "security_violation"):
        raise RecipientError("Initial notice timestamp only applies to breach or violation")
    if "renewal_at" in data and event != "policy_update_notice":
        raise RecipientError("Renewal timestamp only applies to policy updates")
    try:
        occurred = _timestamp(data["occurred_at"])
        notice = _timestamp(data["initial_notice_at"]) if "initial_notice_at" in data else None
        renewal = _timestamp(data["renewal_at"]) if "renewal_at" in data else None
    except (DeadlineError, TypeError) as exc:
        raise RecipientError("Use explicit UTC timestamps") from exc
    if notice is not None and notice < occurred:
        raise RecipientError("Initial notice cannot precede discovery")
    if renewal is not None and renewal < occurred:
        raise RecipientError("Renewal timestamp cannot precede notification")
    external = None
    written = None
    recipient = "Compact Officer/Chief Administrator and FBI"
    section = ""
    additional = ""
    if event == "initial_outsourcing_approval":
        section = "2.07"
        external = occurred + timedelta(days=30)
        additional = "Notify appointment and ARSO contact information; appointment itself remains an external personnel action."
    elif event == "arpoc_change":
        section = "2.06"
        external = occurred + timedelta(days=30)
        additional = "Update ARPOC designation and send required notification."
    elif event == "arso_change":
        section = "2.07"
        external = occurred + timedelta(days=30)
        additional = "Update ARSO designation and send required notification."
    elif event == "policy_update_notice":
        section = "2.03"
        external = min(occurred + timedelta(days=60), renewal) if renewal else occurred + timedelta(days=60)
        additional = "Policy references must be updated at contract/renewal or within 60-day notification window, whichever sooner."
        recipient = "Internal contract owner (document update, not notice dispatch)"
    elif event == "pii_breach":
        section = "2.08"
        external = occurred + timedelta(hours=1)
        written = notice + timedelta(days=5) if notice else None
        additional = "Written breach report due five calendar days after initial notification; report actual content and corrections."
    elif event == "security_violation":
        section = "2.08"
        external = occurred + timedelta(hours=4)
        written = notice + timedelta(days=5) if notice else None
        additional = "Possible suspension under §2.10 for failure to report; reinstatement needs written assurances."
    elif event == "contract_termination":
        section = "2.08"
        external = occurred + timedelta(hours=4)
        additional = "Separate §2.14 written notice applies to early voluntary termination; no numeric deadline stated there."
    else:
        section = "2.14"
        additional = "Written notice to both recipients is required; §2.14 sets no specific deadline."
    return {
        "event": event, "section": section, "pdf_page": "9" if int(section[2:]) <= 8 else "10",
        "external_due_utc": external.isoformat() if external else None,
        "written_report_due_utc": written.isoformat() if written else None,
        "requires_initial_notice_time": event in ("pii_breach", "security_violation") and notice is None,
        "recipients": recipient,
        "instruction": additional,
        "messages_sent": False,
        "automatically_verified": False,
        "legal_role_verified": False,
    }

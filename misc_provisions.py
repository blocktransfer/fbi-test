"""Compact Council 2023 Outsourcing Standard Section 5, Miscellaneous Provisions.

Source: uploaded November 29, 2023 Security and Management Control
Outsourcing Standard for Channeling, §§5.01–5.08, PDF pages 18–19
(printed pages 10–11). No local operator may modify official standards,
grant an exception or purport to act for a governmental authority.
"""
from __future__ import annotations

from copy import deepcopy

SOURCE = {
    "title": "Security and Management Control Outsourcing Standard for Channeling",
    "issuer": "National Crime Prevention and Privacy Compact Council",
    "last_updated": "2023-11-29",
    "section": "5",
    "heading": "Miscellaneous Provisions",
    "pdf_pages": "18–19",
    "printed_pages": "10–11",
}

CLAUSES = (
    ("5.01", "governance", "Only Compact Council may modify this Standard under 28 CFR Part 906; applies to all personnel, systems, networks and facilities supporting/on behalf of Authorized Recipient.", "18"),
    ("5.02", "scope", "Standard confers no rights, privileges or obligations on persons outside Channeler, Authorized Recipient, FBI and, when applicable, Compact Officer/Chief Administrator.", "18"),
    ("5.03", "incorporation", "Current CJIS Security Policy (CJISSECPOL) is incorporated by reference as part of this Standard.", "18"),
    ("5.04", "higher_controls", "Standard is a minimum security basis; Recipient–Channeler contract may impose stricter controls (e.g. extra audits, fees or security).", "18"),
    ("5.05", "non_waiver", "Only Compact Council modifies this Standard; CJISSECPOL minimum changes require CJIS APB process; reductions below Standard require Compact Council consent after consultation with U.S. Attorney General.", "18"),
    ("5.06", "audit_rights", "Compact Officer/Chief Administrator, Compact Council and U.S. Attorney General may conduct scheduled or unscheduled audits; Council, Attorney General and applicable state may final-audit Channeler after termination.", "19"),
    ("5.07", "investigation_rights", "Compact Officer/Chief Administrator, Compact Council and U.S. Attorney General may investigate OR decline to investigate unauthorized-CHRI-access reports.", "19"),
    ("5.08", "postal_delivery", "Required correspondence to FBI, Compact Council, FBI Compact Officer and U.S. Attorney General is directed by First Class Mail to specified FBI Compact Officer address.", "19"),
)

CHECKS = (
    ("5.01", "council_exclusive_change", "Official Compact Council-only modification process respected"),
    ("5.01", "all_supporting_assets", "All recipient-supporting personnel, systems, networks and facilities in scope"),
    ("5.02", "authorized_roles_only", "No rights claimed for entities beyond listed §5.02 parties"),
    ("5.03", "cjis_policy_incorporated", "Applicable CJIS Security Policy incorporated by reference"),
    ("5.04", "contract_minima_preserved", "Contract preserves minimum security controls"),
    ("5.04", "stricter_terms_tracked", "Stricter contract audits, fees or security conditions tracked separately"),
    ("5.05", "apb_control_process", "CJIS Security Policy changes reserved to CJIS APB process"),
    ("5.05", "compact_council_consultation", "Proposed less-stringent minimum requires Compact Council consent in consultation with U.S. Attorney General"),
    ("5.05", "no_local_waivers", "Local sender must not accept claimed regulatory waivers"),
    ("5.06", "scheduled_audit_readiness", "Scheduled audits by authorized authorities supported"),
    ("5.06", "unscheduled_audit_readiness", "Unscheduled audits by authorized authorities supported"),
    ("5.06", "post_termination_final_audit", "Post-termination final audit rights preserved"),
    ("5.07", "reports_triaged", "Unauthorized-access report can be routed to competent authority"),
    ("5.07", "authority_decision_reserved", "Decision to investigate/decline reserved to permitted authority"),
    ("5.08", "first_class_mail_process", "First Class Mail instructions incorporated in external correspondence workflow"),
    ("5.08", "address_control", "Correct FBI Compact Officer mailing address controlled as document version"),
    ("5.08", "dispatch_proof", "Actual mail dispatch and delivery evidence tracked externally"),
)

CHECK_IDS = frozenset(section + "." + key for section, key, _ in CHECKS)
PARTIES = frozenset((
    "channeler", "authorized_recipient", "fbi", "compact_officer_chief_administrator",
))
AUDITORS = frozenset((
    "compact_officer_chief_administrator", "compact_council", "us_attorney_general",
))
FINAL_AUDITORS = frozenset(("compact_council", "us_attorney_general", "applicable_state"))
INVESTIGATION_AUTHORITIES = AUDITORS

FIRST_CLASS_MAIL = {
    "method": "First Class Mail",
    "recipient": "FBI Compact Officer",
    "routing": "BTC4",
    "organization": "FBI CJIS Division",
    "street": "1000 Custer Hollow Road",
    "city_state_zip": "Clarksburg, WV 26306",
    "source_section": "5.08",
    "as_published_2023": True,
    "current_address_verified": False,
}


def catalog() -> dict:
    return {
        "source": deepcopy(SOURCE),
        "sections": [f"5.{i:02d}" for i in range(1, 9)],
        "clauses": [
            {"section": section, "topic": topic, "description": description,
             "pdf_page": page}
            for section, topic, description, page in CLAUSES
        ],
        "checks": [
            {"id": section + "." + key, "section": section, "description": description}
            for section, key, description in CHECKS
        ],
        "mailing": deepcopy(FIRST_CLASS_MAIL),
        "check_count": len(CHECKS),
        "regulatory_change_authorized": False,
        "government_decision_performed": False,
        "current_postal_address_verified": False,
        "production_ready": False,
    }

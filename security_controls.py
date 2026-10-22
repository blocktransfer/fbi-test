"""Source-referenced security register for the synthetic-only sender.

These are control observations, NOT evidence of compliance or agency approval.
The legal role (Authorized Recipient / Channeler) is not established by this app.
"""

from __future__ import annotations

from copy import deepcopy

DOCUMENTS = {
    "CJIS": {
        "title": "FBI CJIS Security Policy",
        "version": "6.1",
        "date": "2026-06-25",
    },
    "OUTSOURCING": {
        "title": "Compact Council Security and Management Control Outsourcing Standard for Channeling",
        "version": "2023-11-29",
        "date": "2023-11-29",
    },
}

# Printed page numbers for CJIS; document PDF page numbers for Outsourcing.
# "prototype_only" means a useful test implementation exists, NOT that the
# control is fully satisfied. "unverified" is the default for external duties.
CONTROLS = (
    ("CJIS", "AC-7", "26", "Technical", "Five failed logons within 15 minutes; administrator release of lockout", "prototype_only"),
    ("CJIS", "AC-8", "27", "Technical", "Restricted-system notice with explicit acknowledgment before access", "prototype_only"),
    ("CJIS", "AC-12", "28", "Technical", "Termination of logical user sessions", "prototype_only"),
    ("CJIS", "IA-2 / IA-2(1)", "93-94", "Technical", "Unique organizational identities and MFA for privileged accounts", "unverified"),
    ("CJIS", "AC-2 / AC-6", "17-26", "Technical", "Individual account management and least-privilege authorization", "unverified"),
    ("CJIS", "AU-2 / AU-3", "46-49", "Technical", "Event selection and identity, time, source, outcome in audit records", "unverified"),
    ("CJIS", "AU-9 / AU-11", "52-54", "Technical", "Protect audit records and retain records for at least one year as required", "unverified"),
    ("CJIS", "SC-8(1)", "240-241", "Technical", "Cryptographic protection of transmissions", "prototype_only"),
    ("CJIS", "SC-28", "246-247", "Technical", "Protection of CJI at rest and permitted hosting boundaries", "unverified"),
    ("CJIS", "IR-6", "171", "Organization", "Report suspected incidents immediately, no later than one hour after discovery", "unverified"),
    ("CJIS", "CP-9", "89-90", "Organization", "Protect and test backups for required data", "unverified"),
    ("CJIS", "5.1.1 / CA-3", "15 / 58", "Agency", "Formal exchange agreement with roles, permitted uses and security controls", "unverified"),
    ("OUTSOURCING", "2.01-2.02", "8", "Authorized Recipient", "Written Compact Officer/Chief Administrator permission and outsourcing agreement", "unverified"),
    ("OUTSOURCING", "2.06-2.07", "9", "Authorized Recipient", "Maintain ARPOC and notify ARSO appointment/changes within specified 30-day periods", "unverified"),
    ("OUTSOURCING", "2.08", "9", "Authorized Recipient", "PII breach notice within one hour, violations or termination within four hours, written report within five calendar days", "unverified"),
    ("OUTSOURCING", "3.05", "11", "Channeler", "Document security program and obtain FBI written approval", "unverified"),
    ("OUTSOURCING", "3.08-3.09", "12", "Channeler", "Obtain FBI approval for network diagrams, changes and contingency plan", "unverified"),
    ("OUTSOURCING", "3.12", "12", "Channeler", "Destroy CHRI on confirmed receipt or within 30 calendar days, whichever is sooner", "unverified"),
    ("OUTSOURCING", "3.13", "13", "Channeler", "Retain CHRI dissemination log for at least one year with required identifiers and authority", "unverified"),
    ("OUTSOURCING", "3.15", "13", "Channeler", "Notify Authorized Recipient, Compact Officer and FBI within breach/violation time limits; written report within five days", "unverified"),
    ("OUTSOURCING", "3.18-3.19", "14", "Channeler", "Update access records and notify FBI within 24 hours; initial and annual refresher training", "unverified"),
    ("OUTSOURCING", "3.22-3.25", "14-15", "Channeler", "Maintain EBTS and Rap Back transaction requirements, subject to approval", "unverified"),
    ("OUTSOURCING", "4.03-4.10", "16-17", "FBI", "FBI audit and approval responsibilities; cannot be satisfied by sender code", "unverified"),
)


def readiness_register() -> dict:
    controls = [
        {
            "framework": framework,
            "section": section,
            "pages": pages,
            "responsible_party": party,
            "requirement": requirement,
            "state": state,
            "is_fully_verified": False,
        }
        for framework, section, pages, party, requirement, state in CONTROLS
    ]
    return {
        "production_ready": False,
        "legal_role_verified": False,
        "FBI_approval_verified": False,
        "assessment": "Source-derived readiness inventory, not a compliance certification",
        "sources": deepcopy(DOCUMENTS),
        "control_count": len(controls),
        "controls": controls,
    }

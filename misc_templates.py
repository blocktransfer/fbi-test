"""Blank Section 5 governance and First Class Mail reference templates.

No documents are mailed or signed and no legal policy waiver is granted.
Never enter actual CJI, PII, confidential case details or agency identifiers.
"""
from __future__ import annotations

from misc_provisions import SOURCE, FIRST_CLASS_MAIL

TEMPLATES = (
    (
        "first_class_cover",
        "First Class Mail cover for required notices / assurances",
        ["5.08"],
        """EXTERNAL MAIL DRAFT ONLY — VERIFY CURRENT OFFICIAL ADDRESS

Delivery method: FIRST CLASS MAIL (as specified by §5.08, 2023 Standard).
FBI Compact Officer
BTC4
FBI CJIS Division
1000 Custer Hollow Road
Clarksburg, WV 26306

Date: [DATE]
Original addressee / legal purpose: [FBI / COMPACT COUNCIL /
FBI COMPACT OFFICER / U.S. ATTORNEY GENERAL, AS REQUIRED]
Official notice, assurance or correspondence category: [TYPE]
Authorized sender: [PREPARE OUTSIDE THIS TEST CONSOLE]
Required documents enclosed: [DOCUMENT IDENTIFIERS — PRIVATE]
Proof of posting / delivery: [OFFICIAL EXTERNAL RECORD]

This is a blank outline, not proof of sending, official receipt or approval.
Verify updated agency routing before using in any actual correspondence.""",
    ),
    (
        "cjis_incorporation",
        "Policy incorporation and covered-system inventory outline",
        ["5.01", "5.03"],
        """POLICY INTEGRATION / COVERAGE WORKSHEET
Outsourcing Standard version: [COMPATIBLE OFFICIAL VERSION]
CJIS Security Policy incorporated by reference: [APPLICABLE VERSION]
Authorized Recipient agreement: [CONTROLLED EXTERNAL DOCUMENT]
Included Recipient-supporting personnel: [SECURE ORGANIZATIONAL INVENTORY]
Included Recipient-supporting systems: [SECURE ORGANIZATIONAL INVENTORY]
Included Recipient-supporting networks: [SECURE ORGANIZATIONAL INVENTORY]
Included Recipient-supporting facilities: [SECURE ORGANIZATIONAL INVENTORY]
Validation by responsible organizational officials: [OFFLINE EVIDENCE]
No assets become exempt merely because the Channeler is using this software.""",
    ),
    (
        "contract_stricter_controls",
        "Contract terms exceeding Compact Council minima",
        ["5.04", "5.05"],
        """RECIPIENT–CHANNELER CONTRACT SUPPLEMENT — LEGAL REVIEW REQUIRED
Controlling minimums: [OFFICIAL OUTSOURCING STANDARD AND CJISSECPOL]
Stricter contract provisions, if applicable:
- Additional security requirements: [PROPOSED TEXT]
- Additional audits and access: [PROPOSED TEXT]
- Additional fees or service obligations: [PROPOSED TEXT]
Security comparison / no relaxation of mandatory minimums: [REVIEW]
Written agreement and governing legal authority: [EXTERNAL EVIDENCE]
Compact Council approval cannot be presumed from a contract provision.
The CJIS APB process, not a local contract toggle, governs
modification of CJIS Security Policy minimum measures.""",
    ),
    (
        "minimums_change_request",
        "Proposed lower-minimum change referral (not a waiver)",
        ["5.01", "5.05"],
        """EXTERNAL REGULATORY CONSULTATION DRAFT — NOT A WAIVER
Standard or minimum security measure proposed for change: [PROVISION]
Current governing rule/policy: [OFFICIAL VERSION]
Impact and proposed variation: [LEGAL AND SECURITY ANALYSIS]
Compact Council modification authority under 28 CFR Part 906: [EXTERNAL]
Consultation with U.S. Attorney General: [AUTHENTIC RECORD]
For CJISSECPOL minimum changes: [CJIS APB GOVERNANCE PROCESS RECORD]
Written competent authority decision: [AUTHENTIC OFFICIAL DOCUMENT]
No relaxation is implemented or authorized in this prototype.
DO NOT USE AN INTERNAL APPROVAL OR EVIDENCE REFERENCE AS CONSENT.""",
    ),
    (
        "audit_and_final_audit",
        "Scheduled, unannounced and post-termination audit coordination",
        ["5.06"],
        """GOVERNMENT AUDIT-READINESS OUTLINE
Requesting authority: [COMPACT OFFICER/CHIEF ADMINISTRATOR /
COMPACT COUNCIL / U.S. ATTORNEY GENERAL]
Scheduled or unscheduled inspection: [AUTHORIZED NOTICE OR ARRANGEMENTS]
Authorized Recipient and Channeler procedures: [SECURE EXTERNAL EVIDENCE]
Facilities/systems/accounts made available under law: [CONTROLLED PLAN]
If agreement terminated — final Channeler systems audit:
[COMPACT COUNCIL / U.S. ATTORNEY GENERAL / APPLICABLE STATE]
Official audit results, preservation and follow-up: [PROTECTED RECORD]
Only competent authorities may conduct these audits.
The dashboard schedules none and cannot act as a government auditor.""",
    ),
    (
        "unauthorized_access_reporting",
        "Unauthorized CHRI access report routing",
        ["5.07", "5.08"],
        """RESTRICTED OUTSIDE-APP INCIDENT CORRESPONDENCE OUTLINE
Potential unauthorized CHRI access: [PREPARE IN APPROVED SECURE SYSTEM]
Applicable immediate notice duties in Sections 2 or 3: [CROSS-REFERENCE]
Recipient / Compact Officer / FBI notifications: [OFFICIAL DELIVERY]
Competent authority for §5.07 discretion: [COMPACT OFFICER/CHIEF
ADMINISTRATOR / COMPACT COUNCIL / U.S. ATTORNEY GENERAL]
Authority may INVESTIGATE or DECLINE TO INVESTIGATE; this decision
must be made by the competent authority, not the Channeler or software.
Where §5.08 applies, prepare correspondence by First Class Mail
to the published FBI Compact Officer routing address, subject to
verification of current instructions.
No report is stored, transmitted, accepted or adjudicated in this console.""",
    ),
)


def template_catalog() -> dict:
    return {
        "source": dict(SOURCE),
        "mailing": dict(FIRST_CLASS_MAIL),
        "templates": [
            {
                "id": identifier, "title": title, "sections": list(sections),
                "body": text, "blank_only": True, "sent": False,
                "government_decision": False,
            }
            for identifier, title, sections, text in TEMPLATES
        ],
        "postal_address_current_verified": False,
        "contains_real_legal_documents": False,
        "production_ready": False,
    }

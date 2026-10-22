"""Unpopulated document templates for Authorized Recipient duties (§2).

Copies remain editable outside this test system. No notifications are sent,
and the UI never requests or stores names, addresses, incident details, or CJI.
"""
from __future__ import annotations

from authorized_recipient import SOURCE

TEMPLATES = (
    {
        "id": "permission_request",
        "title": "Prior written permission request",
        "sections": ["2.01"],
        "required_review": "Select the proper State or FBI Compact Officer for the recipient's actual authority and routing.",
        "body": """Subject: Request for written permission to use a fingerprint Channeler

To: [State Compact Officer/Chief Administrator OR FBI Compact Officer, as §2.01(a)-(b) directs]
From: [Authorized Recipient / designated official]
Date: [DATE]

Authorized Recipient: [ENTITY]
ARPOC: [RECIPIENT EMPLOYEE NAME AND CONTACT INFORMATION]
Specific legal authority for national fingerprint-based criminal history checks: [CITE]
Specific populations to be submitted: [AUTHORIZED POPULATIONS]
Proposed Channeler: [ENTITY; DO NOT ASSERT FBI SELECTION WITHOUT DOCUMENTARY EVIDENCE]
Proposed fingerprint submission / CHRI return path: [REVIEWED PROCESS DESCRIPTION]

We request written permission before using the Channeler.
Please provide the decision and any conditions in writing.

[AUTHORIZED RECIPIENT SIGNATURE]""",
    },
    {
        "id": "outsourcing_agreement",
        "title": "CHRI outsourcing agreement clauses",
        "sections": ["2.02", "2.03", "2.04", "2.05", "2.09"],
        "required_review": "Contract must be negotiated, signed, and independently reviewed; this is an outline, not an executed agreement.",
        "body": """AUTHORIZED RECIPIENT — CHANNELER OUTSOURCING AGREEMENT OUTLINE
Parties: [AUTHORIZED RECIPIENT] and [CHANNELER].
Effective date, purpose, and populations: [DATE, AUTHORITY, POPULATIONS].
Incorporated by reference: current Compact Council Security and Management Control Outsourcing Standard for Channeling and current FBI CJIS Security Policy. Update references on contract, renewal, or within the specified notification period, whichever is sooner.

1. Scope and access: Specify exactly when and how the Channeler accesses CHRI.
2. Purpose limitation: CHRI may be used only for the purposes for which provided.
3. Authorized dissemination: Prohibit any other disclosure under federal/state law and Compact rules.
4. Security: Maintain security and confidentiality of CHRI and associated systems.
5. Audits and sanctions: Provide for FBI audits and Compact Council sanctions.
6. Termination: Specify contractual conditions, CHRI disposition, required notices, and termination rights.
7. Processing transparency: Document the Channeler's processing, storage, transmission and delivery path.
8. Security-violation termination grounds: CHRI violation; missing notice or report; refusal/inability to complete correction (§2.09).
9. Availability: Supply applicable CHRI-related portions of the current agreement to Compact Officer/Chief Administrator or FBI upon request.

[LEGAL REVIEW, SIGNATURES, EFFECTIVE VERSION AND APPROVALS]""",
    },
    {
        "id": "policy_update",
        "title": "Policy and contract version update",
        "sections": ["2.03"],
        "required_review": "Confirm the operative versions and any FBI/Compact Council notification period.",
        "body": """DOCUMENT CONTROL RECORD — §2.03

Authorized Recipient agreement: [REFERENCE]
Prior policy versions incorporated: [VERSIONS]
Updated Outsourcing Standard: [VERSION/DATE]
Updated CJIS Security Policy: [VERSION/DATE]
Policy update notification date: [UTC TIME]
Next contract date / renewal: [UTC TIME]
Earliest required update deadline: [DATE, BASED ON CONTRACT/RENEWAL OR NOTIFIED 60-DAY PERIOD]
Amendment completion and signature: [EVIDENCE]
Notices and relevant review: [EVIDENCE]""",
    },
    {
        "id": "arpoc_change",
        "title": "ARPOC change notice",
        "sections": ["2.06", "1.03"],
        "required_review": "Send notice to both Compact Officer/Chief Administrator and FBI within 30 calendar days of a change.",
        "body": """To: [COMPACT OFFICER/CHIEF ADMINISTRATOR] and [FBI]
Subject: Notice of ARPOC change — §2.06

Authorized Recipient: [ENTITY]
Effective change date: [DATE/TIME]
New ARPOC: [NAME, CONTACT AND RECIPIENT EMPLOYEE STATUS]
Prior ARPOC: [IF APPROPRIATE]
Submitted on: [DATE/TIME]

Please update the approved points of contact.
[AUTHORIZED SIGNATURE AND DELIVERY RECEIPTS]""",
    },
    {
        "id": "arso_notice",
        "title": "ARSO appointment or change notice",
        "sections": ["2.07", "1.04"],
        "required_review": "Appointment must be tracked from initial outsourcing approval; changed ARSO contact also requires notice within 30 days.",
        "body": """To: [COMPACT OFFICER/CHIEF ADMINISTRATOR] and [FBI]
Subject: Authorized Recipient Security Officer appointment/change — §2.07

Authorized Recipient: [ENTITY]
Initial outsourcing approval date, if applicable: [DATE]
New or changed ARSO: [NAME AND CONTACT INFORMATION]
Appointment / effective change date: [DATE]
Oversight responsibility: Ensure Channeler follows CJISSECPOL and Outsourcing Standard, confirm annual security training, and communicate with FBI CJIS on security matters.
Submitted on: [DATE/TIME]

[AUTHORIZED SIGNATURE AND DELIVERY RECEIPTS]""",
    },
    {
        "id": "incident_notice_and_report",
        "title": "Breach/violation notice and written report",
        "sections": ["2.08", "2.10"],
        "required_review": "Time-sensitive: PII breach one hour, other security violation or termination four hours; written breach/violation report five calendar days from initial notification.",
        "body": """RESTRICTED — INCIDENT COMMUNICATION TEMPLATE
NOT for submission through this test application.

Recipients: Compact Officer/Chief Administrator and FBI
Authorized Recipient: [ENTITY]
Channeler: [NAME]
FBI-assigned Originating Agency Case number (OCA): [OCA]
Event: [PII BREACH / SECURITY VIOLATION / CONTRACT TERMINATION]
Discovery time (UTC): [TIME]
Occurrence time (UTC): [TIME]
Initial notification sent (UTC): [TIME]
Initial notice deadline: [1 HOUR FOR PII BREACH; 4 HOURS FOR OTHER VIOLATION/TERMINATION]

Written breach/violation report:
- Summary of the violation: [DETAILS — HANDLE SECURELY]
- Corrective actions taken by Authorized Recipient and Channeler, as appropriate: [DETAILS]
- Whether intentional: [YES/NO/UNKNOWN]
- Number of times occurred: [COUNT]
- Date and time of violation: [TIME]
- Applicable Channeler name and Authorized Recipient OCA: [IDENTIFIERS]
- Written report deadline: [5 CALENDAR DAYS FROM INITIAL NOTICE]
- Evidence of delivery to both recipients: [RECEIPTS]

Failure to notify may cause CHRI suspension under §2.10.
[AUTHORIZED SIGNATURE AND SECURITY REVIEW]""",
    },
    {
        "id": "reinstatement_assurances",
        "title": "Suspension and reinstatement assurances",
        "sections": ["2.10"],
        "required_review": "A workflow record never restores CHRI access. The Compact Council Chair or Attorney General must receive satisfactory written assurances through the required parties.",
        "body": """SUSPENSION / REINSTATEMENT REVIEW — §2.10

Security violation and reporting status: [DOCUMENTED FACTS]
CHRI exchange suspended by competent authority? [YES/NO/UNKNOWN]
Satisfactory written assurances from:
- Compact Officer/Chief Administrator: [EVIDENCE]
- Authorized Recipient: [EVIDENCE]
- Channeler: [EVIDENCE]
Recipient of assurances: [COMPACT COUNCIL CHAIR OR ATTORNEY GENERAL]
Official determination of resolution and reinstatement: [DOCUMENTED WRITTEN DECISION]

Do NOT restore CHRI exchange based solely on internal checklists or this template.""",
    },
    {
        "id": "audit_and_site_controls",
        "title": "Audit access and stricter-site requirements",
        "sections": ["2.11", "2.12", "2.13"],
        "required_review": "Mandatory access for state/FBI inspections; recipient audits and stricter site conditions are optional.",
        "body": """AUTHORIZED RECIPIENT AUDIT AND SITE SECURITY WORKSHEET

§2.11: Facilities available to state/FBI for announced and unannounced audits and security inspections.
Facility access arrangements and inspection contacts: [RESTRICTED OFFLINE PROCEDURES]
Audit readiness records and corrective actions: [EVIDENCE]

§2.12: Authorized Recipient may conduct audits of its Channeler(s).
Optional audit decision, scope, report, findings, and response: [EVIDENCE]

§2.13: Authorized Recipient may impose Channeler site controls more stringent than CJIS APB baseline.
Document any agreed additional site requirements: [CONTRACT AND CONTROL REFERENCES]""",
    },
    {
        "id": "voluntary_termination",
        "title": "Early voluntary termination notice",
        "sections": ["2.14", "2.04", "2.09"],
        "required_review": "Provide written early voluntary termination notice to Compact Officer/Chief Administrator and FBI; preserve agreement-specific terms.",
        "body": """To: [COMPACT OFFICER/CHIEF ADMINISTRATOR] and [FBI]
Subject: Written notice of early voluntary termination of Channeler agreement — §2.14

Authorized Recipient: [ENTITY]
Channeler: [ENTITY]
Contract/agreement reference: [REFERENCE]
Effective termination date: [DATE]
Reason, where appropriate: [AUTHORIZED DOCUMENTATION]
CHRI access shutoff and disposition per law/agreement: [EVIDENCE]
Coordination of pending responses and security responsibilities: [EVIDENCE]
Date notice submitted: [DATE/TIME]
Delivery receipts: [EVIDENCE]

[AUTHORIZED SIGNATURE]""",
    },
)


def template_catalog() -> dict:
    return {
        "source": dict(SOURCE),
        "templates": [
            {
                **template,
                "generated_only": True,
                "notice_sent": False,
                "FBI_approval_verified": False,
            }
            for template in TEMPLATES
        ],
        "contains_actual_personal_data": False,
        "production_ready": False,
    }

"""Section 4, FBI responsibilities, Compact Council Channeling Standard (2023).

Source: Security and Management Control Outsourcing Standard for Channeling,
approved November 29, 2023, Section 4 §§4.01–4.10, printed pages 8–9.
These are duties of the FBI and/or Compact Officer/Chief Administrator,
NOT permissions or approvals which local software can grant.
"""
from __future__ import annotations
from copy import deepcopy

SOURCE = {
    "title": "Security and Management Control Outsourcing Standard for Channeling",
    "issuer": "National Crime Prevention and Privacy Compact Council",
    "approved": "2023-11-29",
    "section": "4",
    "printed_pages": "8–9",
}
# Section, responsible actor, source-grounded summary, printed page.
CLAUSES = (
    ("4.01", "Compact Officer/Chief Administrator and FBI",
     "Officer/Administrator reviews legal authority and responds in writing to Recipient outsourcing request; FBI coordinates in drafting the response.", "8"),
    ("4.01(a)", "Compact Officer/Chief Administrator",
     "Before permission: combined state/federal audit program covering representative sample of Channelers and Recipients at least triennially; first such audit within one year of first approved CHRI receipt; generally accepted statistical sampling.", "8"),
    ("4.02", "FBI",
     "Notify Channelers of updates to Outsourcing Standard and CJISSECPOL; provide most current copies within 60 calendar days after notice unless otherwise directed.", "8"),
    ("4.03", "FBI",
     "Conduct 90-day, one-year, and triennial Channeler audits after agreement; within 90 calendar days of first CHRI receipt certify an audit was conducted to the FBI Compact Officer and provide the results.", "8"),
    ("4.04", "FBI",
     "Perform criminal history checks for Channeler personnel with CHRI access; maintain access roster and list of persons who passed checks; update access records within 24 hours after changes.", "8"),
    ("4.05", "FBI",
     "Assign an Originating Agency Case (OCA) to each Authorized Recipient and an Originating Agency Identifier (ORI) to each Channeler.", "8"),
    ("4.06", "FBI",
     "Ensure Channeler physical site security against unauthorized CHRI access.", "9"),
    ("4.07", "FBI",
     "Ensure current physical, personnel and IT Security Program exists and is administered; provide written FBI approval.", "9"),
    ("4.08", "FBI",
     "Review Channeler Security Awareness Training Program and provide written approval.", "9"),
    ("4.09", "FBI",
     "Review Channeler system contingency plan and provide written approval.", "9"),
    ("4.10", "FBI",
     "Review and give written approval of Channeler network diagram, retain up-to-date copy, review and approve proposed changes.", "9"),
)
# Safe document-reference checklist claims; never actual FBI verification.
CHECKS = (
    ("4.01", "recipient_authority_review", "Officer/Administrator legal authority review documented"),
    ("4.01", "written_response", "Written response to Authorized Recipient request documented"),
    ("4.01", "fbi_coordination", "FBI coordination on drafted response documented"),
    ("4.01(a)", "combined_audit_program", "Combined state/federal audit program established before permission"),
    ("4.01(a)", "representative_sampling", "Generally accepted statistical sampling method documented"),
    ("4.01(a)", "first_year_sample_audit", "First combined representative-sample audit within one year of initial CHRI receipt"),
    ("4.01(a)", "triennial_sampling", "Representative-sample audit at least triennially"),
    ("4.02", "notice_to_channeler", "Update notification to Channeler documented"),
    ("4.02", "current_versions", "Current Standard/CJISSECPOL provided within 60 days unless otherwise directed"),
    ("4.03", "agreement_execution", "Channeler agreement execution date recorded externally"),
    ("4.03", "ninety_day_audit", "Initial 90-day Channeler audit performed"),
    ("4.03", "compact_officer_certification", "Initial audit certification AND results sent to FBI Compact Officer within 90 days"),
    ("4.03", "one_year_audit", "One-year Channeler audit performed"),
    ("4.03", "triennial_audits", "Recurring triennial Channeler audits performed"),
    ("4.04", "background_checks", "Criminal history checks performed for CHRI-access personnel"),
    ("4.04", "access_roster", "FBI CHRI-access roster maintained"),
    ("4.04", "roster_updates_24_hours", "Personnel access-change records updated within 24 hours"),
    ("4.04", "successful_checks_list", "List of successful personnel checks maintained"),
    ("4.05", "recipient_oca", "FBI-assigned OCA for Authorized Recipient documented in approved records"),
    ("4.05", "channeler_ori", "FBI-assigned ORI for Channeler documented in approved records"),
    ("4.06", "secure_site", "FBI physical security evaluation completed"),
    ("4.07", "security_program_current", "Physical, personnel and IT Security Program assessed against current policies"),
    ("4.07", "written_security_approval", "FBI written Security Program approval recorded externally"),
    ("4.08", "written_training_approval", "FBI written Security Awareness Training Program approval recorded externally"),
    ("4.09", "written_contingency_approval", "FBI written contingency plan approval recorded externally"),
    ("4.10", "written_network_approval", "FBI written network diagram approval recorded externally"),
    ("4.10", "network_diagram_copy", "FBI up-to-date network diagram copy maintained"),
    ("4.10", "network_change_approval", "FBI approval before changes to diagram/configuration documented"),
)

CHECK_IDS = frozenset(section + "." + key for section, key, _ in CHECKS)


def catalog() -> dict:
    return {
        "source": deepcopy(SOURCE),
        "responsibility": "FBI / Compact Officer/Chief Administrator; external duties",
        "sections": ["4.%02d" % n for n in range(1, 11)],
        "clauses": [
            {"section": section, "responsible_party": actor,
             "description": description, "printed_page": page}
            for section, actor, description, page in CLAUSES
        ],
        "checks": [
            {"id": section + "." + key, "section": section, "description": description,
             "actor": "Compact Officer/Chief Administrator" if section == "4.01(a)" else
                      "Compact Officer/Chief Administrator and FBI" if section == "4.01" else "FBI"}
            for section, key, description in CHECKS
        ],
        "clause_count": len(CLAUSES),
        "check_count": len(CHECKS),
        "externally_verified": False,
        "agency_action_performed": False,
        "FBI_approval_verified": False,
        "production_ready": False,
    }

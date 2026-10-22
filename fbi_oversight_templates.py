"""Blank Section 4 oversight templates. Never produce an FBI determination.

The forms are generic outlines for authorized external reviewers, with no
personal records, OCA/ORI values, actual audit files or agency signatures.
"""
from fbi_oversight import SOURCE

TEMPLATES = (
    ("recipient_permission_response", "Written outsourcing permission response",
     ["4.01"],
     """DRAFT / OFFICIAL REVIEW REQUIRED — NOT AN FBI OR COMPACT OFFICER DECISION
Requesting Authorized Recipient: [LEGAL ENTITY / CONTROLLED EXTERNAL FILE]
Specific noncriminal justice statutory authority: [DOCUMENTED LEGAL REVIEW]
Proposed Channeler: [ENTITY AND FBI-SELECTION DOCUMENT]
Compact Officer/Chief Administrator legal authority review: [OFFICIAL RECORD]
Combined state/federal audit program established before grant? [OFFICIAL EVIDENCE]
FBI coordination in drafting response: [REVIEW EVIDENCE]
Actual written decision and conditions: [SIGNATURE / OFFICIAL CORRESPONDENCE]
This local template cannot grant permission or certify an agency decision."""),
    ("combined_audit_program", "Combined state/federal sampling program",
     ["4.01(a)"],
     """COMBINED STATE/FEDERAL AUDIT PROGRAM — EXTERNAL OFFICIAL ACTION
Compact Officer/Chief Administrator program authorization: [SIGNED PLAN]
Population: Authorized Recipients and Channelers in outsourcing arrangements
Sampling methodology: [GENERALLY ACCEPTED STATISTICAL METHOD AND RATIONALE]
Representative sample selection and exclusion method: [DOCUMENTED METHOD]
First Channeler receipt of CHRI under approved agreement: [RESTRICTED SOURCE TIME]
First sample-audit deadline: WITHIN ONE YEAR OF FIRST RECEIPT
Further representative-sample audits: AT LEAST TRIENNIALLY
Auditors, independence, results handling and corrective action: [CONTROLLED FILES]
Actual agency permission cannot be granted until required program is implemented."""),
    ("fbi_channeler_audit", "FBI 90-day, one-year and triennial audit",
     ["4.03"],
     """FBI CHANNELER AUDIT PLAN — NOT AN AUDIT CERTIFICATION
Agreement execution: [OFFICIAL DATE AND REFERENCE]
First CHRI receipt under approved agreement: [OFFICIAL EVIDENCE]
Initial 90-day audit: [AUDIT DATE, SCOPE, FINAL SIGNED FINDINGS]
Within 90 calendar days of first CHRI receipt: provide FBI Compact Officer
CERTIFICATION that Channeler audit occurred AND A COPY OF AUDIT RESULTS.
One-year audit: [AUDIT PLAN / APPROVED SCHEDULE]
Recurring triennial audits: [AUDIT PLAN / APPROVED SCHEDULE]
Remediation and closeout: [AUTHENTIC AGENCY RECORDS]
Actual certification must be sent by the FBI, not by this software."""),
    ("policy_distribution", "FBI channeler policy-update notification",
     ["4.02"],
     """POLICY-UPDATE DISTRIBUTION — EXTERNAL FBI ACT
Current Outsourcing Standard version: [OFFICIAL VERSION]
Current CJIS Security Policy version: [OFFICIAL VERSION]
Channelers notified of updates: [OFFICIAL NOTICE EVIDENCE]
Notification date: [OFFICIAL UTC TIME]
Current documents made available no later than 60 calendar days thereafter,
unless otherwise directed: [PROTECTED DELIVERY EVIDENCE]
Sender's local worksheet does not distribute documents or notify Channelers."""),
    ("personnel_screening", "Channeler CHRI-access personnel screening",
     ["4.04"],
     """RESTRICTED PERSONNEL SECURITY PROCESS — NO EMPLOYEE DATA HERE
FBI criminal-history check of CHRI-access personnel: [APPROVED WORKFLOW]
Successful personnel-screening list: [FBI CONTROLLED SYSTEM]
Current CHRI-access roster: [FBI CONTROLLED SYSTEM]
Changed access: [OFFICIAL UTC TIME AND AUTHORIZED DECISION]
Roster updated within 24 hours of access change: [FBI RECORD]
Do not enter employee identity, background-check results or CHRI in the test app."""),
    ("agency_identifiers", "FBI OCA / ORI assignment evidence",
     ["4.05"],
     """IDENTIFIER ASSIGNMENT — FBI AUTHORITY ONLY
For EACH Authorized Recipient: FBI-assigned Originating Agency Case (OCA)
For EACH Channeler: FBI-assigned Originating Agency Identifier (ORI)
Evidence of issuance, ownership and correct routing: [OFFICIAL RECORD]
Never derive, create, infer or assign actual OCA/ORI from this interface.
Do not place real OCA/ORI values into local test evidence fields."""),
    ("site_security", "FBI physically secure site assessment",
     ["4.06"],
     """CHANNELER SITE PHYSICAL SECURITY — INSPECTION WORKSHEET
Premises/access controls: [SECURE FACILITY REVIEW]
Unauthorized CHRI access prevention: [TESTING / INSPECTION EVIDENCE]
FBI physical security determination: [OFFICIAL RECORD]
Relevant corrections and reinspection: [SIGNED EVIDENCE]
No facility was assessed by use of this blank document."""),
    ("program_and_training_approval", "FBI Security Program and training approval",
     ["4.07", "4.08"],
     """WRITTEN FBI PROGRAM APPROVAL REVIEW — NOT AN APPROVAL
Current Security Program: PHYSICAL / PERSONNEL / INFORMATION TECHNOLOGY
Review against CURRENT Outsourcing Standard and CJISSECPOL: [MATRIX]
FBI written Security Program approval: [AUTHENTIC SIGNED DECISION]
Security Awareness Training Program: [CURRENT VERSION]
FBI training-program review and written approval: [AUTHENTIC SIGNED DECISION]
Program deficiencies and remediation: [CONTROLLED EVIDENCE]
No checkbox or draft constitutes the FBI's written approval."""),
    ("contingency_and_network", "FBI contingency and network approval/change control",
     ["4.09", "4.10"],
     """FBI WRITTEN APPROVAL RECORD — NOT AN APPROVAL
System contingency plan: [VERSION, REVIEW EVIDENCE]
FBI written contingency plan approval: [ACTUAL WRITTEN DECISION]
Current Channeler network diagram/configuration: [PROTECTED VERSION]
FBI written initial diagram approval: [ACTUAL WRITTEN DECISION]
FBI-maintained up-to-date network diagram copy: [OFFICIAL RECORD]
Proposed diagram/configuration modification: [CHANGE REFERENCE]
FBI REVIEW AND APPROVAL OF MODIFICATION: [ACTUAL WRITTEN DECISION]
No production changes until applicable external approval is established."""),
)


def template_catalog() -> dict:
    return {
        "source": dict(SOURCE),
        "templates": [
            {"id": key, "title": title, "sections": list(sections),
             "body": body, "blank_template": True,
             "agency_action_performed": False,
             "FBI_approval_verified": False}
            for key, title, sections, body in TEMPLATES
        ],
        "contains_real_personal_data": False,
        "production_ready": False,
    }

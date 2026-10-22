"""Blank Channeler §3 policy and notice templates (synthetic-only prototype).

These are templates, NOT approved plans, correspondence, operational records,
or proof that the FBI has reviewed/accepted any system or service.
"""
from __future__ import annotations

from channeler_policy import SOURCE

TEMPLATES = (
    ("legal_and_contract", "Applicable law and CHRI agreement review", ["3.01","3.02"],
     """Applicable federal/state authority and policy references: [DOCUMENT VERSIONS]
Authorized Recipient and Channeler current approved agreement: [REFERENCE]
CHRI-related portions available for Compact Officer/Chief Administrator request: [ACCESS PROCEDURE]
FBI/security review: [AUTHORITY, REVIEW DATE AND OFFICIAL DOCUMENT REFERENCE]
Status: [PENDING / DOCUMENTED]"""),
    ("termination_and_updates", "Early termination and policy update notices", ["3.03","3.04"],
     """To: [COMPACT OFFICER/CHIEF ADMINISTRATOR] and [FBI]
Subject: [EARLY VOLUNTARY TERMINATION NOTICE / POLICY UPDATE]
Agreement and Authorized Recipient: [REFERENCE]
Termination date, if any: [DATE]
For changes to CJISSECPOL or Outsourcing Standard: [VERSION, RECIPIENT NOTICE DATE]
Current versions supplied to Authorized Recipient by: [DATE, ≤60 CALENDAR DAYS unless directed otherwise]
Evidence of actual delivery: [SIGNED RECEIPTS]"""),
    ("security_program", "FBI-approved physical, personnel and IT Security Program outline", ["3.05","3.06","3.07"],
     """CHANNELER SECURITY PROGRAM — AWAITING WRITTEN FBI APPROVAL
Physical security: [CONTROLS, PHYSICAL ACCESS, FACILITY INSPECTION]
Personnel security: [SELECTION, BACKGROUND REVIEW, SUPERVISION, ACCESS REVOCATION, SEPARATION]
Information technology: [CJISSECPOL CONTROLS, ASSETS, ENCRYPTION BOUNDARIES, MONITORING]
Current CJISSECPOL and successor versions: [VERSIONS, MAPPING, CHANGE TRACKING]
Agreement-specific requirements: [REFERENCES]
Review by Recipient/Compact Officer/FBI: [DATES, FINDINGS]
Remediation and change log: [REFERENCES]
FBI WRITTEN APPROVAL: [REQUIRED OFFICIAL APPROVAL, NOT A CHECKBOX]"""),
    ("network_change", "Network configuration, diagram and pre-change FBI approval", ["3.08"],
     """NETWORK CONFIGURATION CONTROL — §§3.08
Current inventory/network diagram version: [VERSION, PROTECTED DOCUMENT REFERENCE]
Proposed change and affected systems: [CHANGE ID, DESCRIPTION]
Security impact and validation plan: [DOCUMENT]
Authorized Recipient coordination: [REVIEW]
FBI diagram approval: [WRITTEN DECISION REFERENCE]
FBI configuration change approval PRIOR TO IMPLEMENTATION: [WRITTEN DECISION REFERENCE]
Approved effective date / release checklist: [DATE]
DO NOT IMPLEMENT UNSANCTIONED PRODUCTION CHANGES."""),
    ("contingency_and_audit", "FBI-approved contingency plan and inspection readiness", ["3.09","3.10","3.11"],
     """IT CONTINGENCY & ACCESS AUDIT PLAN
Continuity, disruption response and recovery controls: [CURRENT DOCUMENT]
FBI contingency approval: [WRITTEN APPROVAL REFERENCE]
All access attempts logged and routine FBI review enabled: [AUDIT DESIGN AND ACCESS PROCEDURE]
Announced and unannounced Recipient/FBI facility audit support: [CONTROLLED ARRANGEMENTS]
Authorized configuration review access: [PROCEDURE]
Findings, owners, remediation, validation: [TRACKED EVIDENCE]"""),
    ("retention_and_disposition", "CHRI custody and secure destruction/return procedure", ["3.12","3.17"],
     """CHRI CUSTODY POLICY — COMPLETE ONLY IN AN APPROVED SECURE SYSTEM
Contract-prescribed CHRI dissemination method/time: [AGREEMENT SECTION]
CHRI received: [SECURE RECORD ID / TIME]
Recipient successful receipt confirmed: [SECURE CONFIRMATION TIME]
Mandatory destruction: IMMEDIATELY ON CONFIRMATION OR NO LATER THAN 30 CALENDAR DAYS FROM RECEIPT, WHICHEVER EARLIER.
Media sanitization under CJISSECPOL: [APPROVED TECHNIQUE, ATTESTATION]
Upon termination of Recipient CHRI exchange, return/delete CHRI records/media as agreement and CJISSECPOL require.
Evidence of actual destruction/return: [CONTROLLED SECURITY RECORD]
This test console never stores CHRI or performs destruction."""),
    ("dissemination_log", "CHRI dissemination log required fields", ["3.13","3.14"],
     """§3.13 CONFIDENTIAL DISSEMINATION LOG — DO NOT ENTER ACTUAL RECORDS HERE
Authorized Recipient unique identifier: [OCA/ORI]
Transaction Control Number (TCN): [TCN]
Date of dissemination: [UTC TIME]
Statutory authority for CHRI access: [CITATION]
Means of dissemination: [AUTHORIZED METHOD]
Retention: AT LEAST ONE YEAR; protect confidential identifiers and access auditability.
Official-purpose limitation and unauthorized-disclosure controls: [ENFORCEMENT EVIDENCE]
Use the protected agency production records system; no CHRI logs are stored in this console."""),
    ("incident_report", "Channeler incident notice and five-day report", ["3.15"],
     """RESTRICTED INCIDENT NOTICE AND REPORT
To: Authorized Recipient; Compact Officer/Chief Administrator; FBI
Event: [PII BREACH / OTHER SECURITY VIOLATION / TERMINATION]
Discovery UTC: [TIME] — PII breach notice ≤1 HOUR; other violation/termination notice ≤4 HOURS.
Initial notices and delivery receipts: [CONTROLLED REFERENCES]
For security violations, WRITTEN REPORT ≤5 CALENDAR DAYS FROM DISCOVERY.
Written contents: [CORRECTIVE ACTIONS TAKEN]; [SUMMARY]; [OCCURRENCE DATE/TIME];
[INTENTIONAL?]; [NUMBER OF OCCURRENCES].
Security follow-up, responsible officer and protected supporting evidence: [REFERENCES]
NOTE: Section 3 clock is FROM DISCOVERY, not initial notification (Section 2)."""),
    ("fingerprint_privacy_notice", "Individual right to report PII breach directly to FBI", ["3.16"],
     """INDIVIDUAL NOTICE — IF FINGERPRINTS ARE TAKEN BY CHANNELER
Your biometric and personal information must be protected during processing.
If you believe your personal information was mishandled or compromised,
you have the right to report a PII breach directly to the FBI.
Use the official current contact path in §5.08 / authoritative FBI guidance.
[REQUIRED ORGANIZATION CONTACT INFORMATION AND ACCESSIBLE DELIVERY METHOD]
[DELIVERY RECORD AND LEGAL/POLICY REVIEW]"""),
    ("personnel_access", "Employee CHRI access, suspension and discipline worksheet", ["3.18","3.20","3.21"],
     """PROTECTED EMPLOYEE ACCESS TRACKING — NOT IN THIS CONSOLE
Employee CHRI access grant/change/revocation: [EMPLOYEE, UTC TIME, AUTHORIZED DECISION]
Update employee access records ≤24 HOURS OF ACCESS CHANGE.
Notify FBI ≤24 HOURS OF ACCESS CHANGE, with delivery evidence.
Written discipline policy: [CURRENT APPROVED POLICY REFERENCE]
Security violation discovery: [TIME / OFFICER]
Suspend affected employee from all CHRI-access assignments UPON DETECTION/AWARENESS.
Personnel security, separation, supervisory and escalation controls: [PLAN]"""),
    ("training_certification", "Security awareness training and yearly FBI certification", ["3.19"],
     """SECURITY AWARENESS / PERSONNEL TRAINING CERTIFICATION
Does the agreement retain the security training duty with Authorized Recipient? [SIGNED CLAUSE]
If not, complete training BEFORE CHRI-access assignment.
Annual refresher curriculum and completion evidence: [PROTECTED TRAINING RECORD]
Agreement anniversary: [DATE]
Written annual certification to FBI no later than anniversary: [DUE DATE]
Actual written certification, responsible signer and evidence of delivery: [REFERENCE]
This blank template is NOT training completion or FBI certification."""),
    ("rapback_messaging", "EBTS/Rap Back controlled messaging and one-year validation", ["3.22","3.23","3.24","3.25"],
     """RAP BACK OPERATIONS — NO PRODUCTION SERVICE ENABLED HERE
Relevant EBTS version and message types: [APPROVED SPECIFICATION]
Privacy risk mitigation implementation guide version: [CURRENT REQUIRED GUIDE]
Annual one-year subscription validation messages: [ROUTING AND TIMELINE]
ONLY Authorized Recipient performs substantive validation; Channeler relays messaging.
Channeler must NOT store applicant PII for Rap Back; ONLY TCN and Rap Back Subscription Identifier may be referenced to store/link individual notifications.
Actual Rap Back testing passed: [FBI WRITTEN DECISION]
FBI implementation approval: [WRITTEN DECISION, PRIOR TO IMPLEMENTATION]
Recipient notification/relay speed and subscription removal tracking: [CONTROLLED PROCESS]"""),
)

def template_catalog() -> dict:
    return {
        "source": dict(SOURCE),
        "templates": [
            {"id": tid, "title": title, "sections": list(sections), "body": body,
             "generated_only": True, "message_sent": False,
             "fbi_approval_verified": False}
            for tid, title, sections, body in TEMPLATES
        ],
        "live_data_allowed": False,
        "production_ready": False,
    }

"""Channeler duties from Compact Council Outsourcing Standard §3.01–§3.25.

Source: Security and Management Control Outsourcing Standard for Channeling,
November 29, 2023, SECTION 3, printed pages 3–7. These are organizational
duties, not evidence of approval, authority, or permission to process CHRI.
"""
from __future__ import annotations
from copy import deepcopy

SOURCE = {
    "title": "Security and Management Control Outsourcing Standard for Channeling",
    "issuer": "National Crime Prevention and Privacy Compact Council",
    "version_date": "2023-11-29", "section": "3", "printed_pages": "3–7",
}
# Section, category, plain-language duty, page, type.
CLAUSES = (
    ("3.01","governance","Comply with applicable federal/state law, CJISSECPOL, Compact Council and Attorney General rules.","3","required"),
    ("3.02","agreements","On request give Compact Officer/Chief Administrator current approved agreement portions that concern CHRI.","3","required_on_request"),
    ("3.03","termination","Give written early voluntary termination notice to Compact Officer/Chief Administrator and FBI.","3","conditional"),
    ("3.04","policy_updates","Notify Authorized Recipient of policy updates and provide current versions within 60 calendar days unless otherwise directed.","3","required_on_event"),
    ("3.05","security_program","Develop/maintain physical, personnel, IT Security Program including selection, supervision and separation; obtain FBI written approval.","3","required"),
    ("3.06","security_program","Maintain program against policy incorporated in the agreement and successor CJISSECPOL versions.","3–4","required"),
    ("3.07","security_program","Permit program review by Recipient, Compact Officer/Chief Administrator, FBI; correct findings and incorporate law/policy changes.","4","required_on_review"),
    ("3.08","network","Maintain current network diagram; obtain FBI approval of diagram and proposed network/configuration changes before implementation.","4","required"),
    ("3.09","contingency","Maintain documented IT contingency plan approved by FBI.","4","required"),
    ("3.10","audit","Record all system access attempts for routine FBI review.","4","required"),
    ("3.11","audit","Allow announced/unannounced audits and inspections and network reviews by Authorized Recipient and FBI.","4","required_on_request"),
    ("3.12","retention","Destroy CHRI immediately upon confirmed successful Recipient receipt or after 30 calendar days, whichever first; contract specifies dissemination methods/time.","4","required"),
    ("3.13","dissemination","Keep CHRI dissemination log at least one year with Recipient FBI-assigned OCA/ORI, TCN, date, legal authority and means.","5","required"),
    ("3.14","access","Protect CHRI and equipment against unauthorized access; restrict NGI checks and CHRI use/dissemination to official permitted purposes.","5","required"),
    ("3.15","incidents","Notify Recipient, Compact Officer/Chief Administrator and FBI within 1 hour of PII breach or 4 hours of other violation/termination; written security-violation report within 5 calendar days of discovery.","5","required_on_event"),
    ("3.16","fingerprinting","If Channeler takes fingerprints, notify individual of right to report PII breaches directly to FBI; safeguard PII throughout processing.","5","conditional"),
    ("3.17","termination","If Recipient CHRI exchange terminates, delete or return CHRI records/media as CJISSECPOL and contract specify.","5","conditional"),
    ("3.18","personnel","Update CHRI-access employee records and notify FBI within 24 hours of access changes.","6","required_on_event"),
    ("3.19","training","Train before assignment; annual refresher and annual written certification to FBI by agreement anniversary, unless Recipient retains training duty by contract.","6","conditional"),
    ("3.20","personnel","Maintain written discipline policy covering employee security violations of incorporated agreement.","6","required"),
    ("3.21","personnel","Immediately suspend violating employee from assignments permitting CHRI access.","6","required_on_event"),
    ("3.22","biometrics","Conform to applicable EBTS; relay required Rap Back messages/results expeditiously and maintain subscription messaging information.","6","conditional"),
    ("3.23","rap_back","Relay mandatory annual Rap Back subscription validation messaging; only Authorized Recipient performs substantive validation.","6","conditional"),
    ("3.24","rap_back","Store no applicant PII for Rap Back; references limited to TCN and Rap Back Subscription Identifier.","7","conditional"),
    ("3.25","rap_back","Before any Rap Back implementation, pass FBI testing and obtain approval; use designated risk mitigation and validation strategy.","7","conditional"),
)
# Source duties decomposed into separately observable evidence/checklist checkpoints.
CHECKS = (
    ("3.01","legal_compliance","Legal/policy compliance review"),
    ("3.02","agreement_available","Current approved CHRI agreement available on authorized request"),
    ("3.03","termination_notice","Written early voluntary termination notice prepared/delivered when applicable"),
    ("3.04","recipient_update_notice","Policy updates relayed to Authorized Recipient"),
    ("3.04","current_versions","Most recent policies made available within required 60 days"),
    ("3.05","physical_program","Documented physical security program"),
    ("3.05","personnel_program","Documented selection, supervision and separation controls"),
    ("3.05","it_program","Documented IT security program"),
    ("3.05","fbi_written_program_approval","Written FBI approval of Security Program"),
    ("3.06","version_tracking","Current/successor CJISSECPOL version mapping"),
    ("3.07","review_remediation","Program review and corrective action tracking"),
    ("3.08","diagram_current","Current network diagram"),
    ("3.08","fbi_diagram_approval","Written FBI diagram approval"),
    ("3.08","pre_change_approval","FBI approval before each configuration change"),
    ("3.09","contingency_plan","Documented and FBI-approved IT contingency plan"),
    ("3.10","access_audit","All access attempts recorded for FBI review"),
    ("3.11","inspections","Facilities and configuration available for audits/inspection"),
    ("3.12","maximum_retention","CHRI retained no longer than earliest successful receipt confirmation or day 30"),
    ("3.12","contract_dissemination","CHRI dissemination method and timing specified in agreement"),
    ("3.13","one_year_dissemination_log","Protected one-year dissemination log with mandatory OCA/ORI, TCN, date, authority, means"),
    ("3.14","restricted_access","CHRI access, use, dissemination and NGI check purpose restrictions"),
    ("3.15","initial_incident_notices","Required one-hour/four-hour notices to all three parties"),
    ("3.15","written_incident_report","Five-calendar-day written security violation report"),
    ("3.16","individual_right_notice","Direct FBI PII breach reporting rights notice when taking fingerprints"),
    ("3.16","pii_protection","PII protected while processing"),
    ("3.17","terminated_data_disposition","CHRI return/deletion on Recipient exchange termination"),
    ("3.18","access_roster_updated","Employee CHRI access record updated within 24 hours"),
    ("3.18","fbi_access_notice","FBI notified of employee CHRI access changes within 24 hours"),
    ("3.19","preassignment_training","Security awareness training before CHRI-access assignment"),
    ("3.19","annual_training","Annual security refresher (unless contract retains duty with Recipient)"),
    ("3.19","annual_fbi_certification","FBI annual written refresher certification by contract anniversary (when duty applies)"),
    ("3.20","discipline_policy","Written discipline policy for security violations"),
    ("3.21","immediate_suspension","Violation-triggered employee removal from CHRI access assignments"),
    ("3.22","ebts_compliance","EBTS conformity and controlled message receipt/relay"),
    ("3.22","rapback_processing","Approved Rap Back message transmission/subscription support"),
    ("3.23","recipient_validation","Annual Rap Back validation messaging, Recipient makes validation decision"),
    ("3.24","minimal_rapback_refs","Rap Back references limited to TCN and subscription ID; no applicant PII"),
    ("3.25","fbi_rapback_testing","Successful FBI Rap Back testing and approval before deployment"),
    ("3.25","risk_mitigation","Approved Rap Back risk mitigation/validation strategy"),
)

def catalog() -> dict:
    return {
        "source": deepcopy(SOURCE),
        "scope": "Channeler obligations, not Authorized Recipient duties",
        "sections": [f"3.{i:02d}" for i in range(1, 26)],
        "clause_count": len(CLAUSES),
        "check_count": len(CHECKS),
        "clauses": [
            {"section": s, "category": c, "description": d,
             "printed_page": p, "kind": k}
            for s, c, d, p, k in CLAUSES
        ],
        "checks": [
            {"id": s + "." + k, "section": s, "label": d}
            for s, k, d in CHECKS
        ],
        "operator_attestation_only": True,
        "externally_approved": False,
        "actual_chri_processing_enabled": False,
        "production_ready": False,
    }

CHECK_IDS = frozenset(f"{s}.{k}" for s, k, _ in CHECKS)

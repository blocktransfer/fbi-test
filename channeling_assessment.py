"""Synthetic-only Section 1 interpretation checks; no personal data accepted.

Inputs are nonidentifying factual *claims*, not verified documentation.
Output never authorizes NGI/III access, CHRI receipt/dissemination, or positive ID.
"""

from __future__ import annotations

from channeling_definitions import definition_catalog


class ContextError(ValueError):
    """Reject unknown keys, unexpected types or raw data before processing."""


PURPOSES = frozenset((
    "unspecified", "employment_suitability", "licensing", "immigration_naturalization",
    "national_security_clearance", "other_legal_noncriminal",
))
ROLES = frozenset(("authorized_recipient", "channeler"))
RECIPIENT_KINDS = frozenset(("government", "nongovernmental", "unspecified"))
AUTHORITY = frozenset((
    "unverified", "federal_statute", "federal_executive_order",
    "state_statute_attorney_general_approved",
))
METHODS = frozenset(("none", "name_only", "ten_rolled", "ten_flat", "other_biometric"))
FIELDS = frozenset((
    "role", "recipient_kind", "purpose", "authority_basis",
    "agreement_reported", "fbi_channeler_selection_reported",
    "direct_ngi_approval_reported", "same_entity_for_purpose",
    "arpoc_recipient_employee", "chief_admin_role_applies",
    "chief_admin_repository_employee", "has_criminal_history",
    "has_biometric_identifiers", "has_other_personal_identifiers",
    "identification_method",
))
BOOL_FIELDS = FIELDS - {
    "role", "recipient_kind", "purpose", "authority_basis", "identification_method",
}


def assess_definitions(request: dict) -> dict:
    """Interpret Section 1 vocabulary without accessing/storing CHRI or PII."""
    if not isinstance(request, dict) or set(request) != FIELDS:
        raise ContextError("Only the defined, nonidentifying Section 1 fields are accepted")
    for field in BOOL_FIELDS:
        if type(request[field]) is not bool:
            raise ContextError("Section 1 switches must be booleans")
    for field, accepted in (
        ("role", ROLES), ("recipient_kind", RECIPIENT_KINDS),
        ("purpose", PURPOSES), ("authority_basis", AUTHORITY),
        ("identification_method", METHODS),
    ):
        if type(request[field]) is not str or request[field] not in accepted:
            raise ContextError("Invalid Section 1 option: " + field)

    notes = []
    def finding(section: str, ok: bool, explanation: str) -> None:
        notes.append({
            "section": section,
            "state": "self_reported_only" if ok else "blocked_by_reported_facts",
            "explanation": explanation,
        })

    kind = request["recipient_kind"]
    basis = request["authority_basis"]
    authority_plausible = (
        basis in ("federal_statute", "federal_executive_order") or
        (kind == "government" and basis == "state_statute_attorney_general_approved")
    )
    finding(
        "1.02", authority_plausible and kind != "unspecified",
        "Recipient legal basis appears structurally plausible but cannot be legally verified by this software."
        if authority_plausible and kind != "unspecified" else
        "Missing or incompatible recipient legal authority; governmental state authority needs Attorney General approval."
    )
    finding(
        "1.16", request["purpose"] != "unspecified",
        "Noncriminal justice purpose category identified; specific statutory authorization still requires verification."
        if request["purpose"] != "unspecified" else
        "Noncriminal justice purpose and governing law have not been identified."
    )
    finding(
        "1.03", request["arpoc_recipient_employee"],
        "ARPOC is reported to be the recipient's employee; not independently verified."
        if request["arpoc_recipient_employee"] else
        "ARPOC cannot be outsourced and must be an employee of the Authorized Recipient."
    )
    if request["chief_admin_role_applies"]:
        finding(
            "1.07 / 1.11", request["chief_admin_repository_employee"],
            "Repository employment is reported for the chief/designee; a state Compact Officer designee must also be a regular full-time repository employee, and both facts remain unverified."
            if request["chief_admin_repository_employee"] else
            "Chief Administrator/eligible state Compact Officer designee must be a repository employee."
        )
    if request["role"] == "channeler":
        finding(
            "1.05", request["fbi_channeler_selection_reported"] and request["direct_ngi_approval_reported"]
            and not request["same_entity_for_purpose"],
            "FBI selection and direct NGI authorization are reported, but require independent confirmation."
            if (request["fbi_channeler_selection_reported"] and request["direct_ngi_approval_reported"]
                and not request["same_entity_for_purpose"]) else
            "Channeler is distinct from the Authorized Recipient for this purpose and needs FBI selection and an authorized NGI connection."
        )
        finding(
            "1.17", request["agreement_reported"],
            "Outsourcing agreement reported; authenticity, scope and legal sufficiency remain unverified."
            if request["agreement_reported"] else
            "An outsourcing agreement between Channeler and Authorized Recipient is needed."
        )
    else:
        finding(
            "1.17", request["agreement_reported"],
            "Outsourcing agreement reported; authenticity, scope and legal sufficiency remain unverified."
            if request["agreement_reported"] else
            "An Authorized Recipient's use of a Channeler requires an outsourcing agreement."
        )
    # 1.08: stand-alone fingerprints without criminal-history involvement are
    # not CHRI; nevertheless 1.19 explicitly treats biometric records as PII.
    is_chri = request["has_criminal_history"]
    is_pii = (
        is_chri or request["has_biometric_identifiers"]
        or request["has_other_personal_identifiers"]
    )
    method = request["identification_method"]
    # 1.22's footnote supports ten-rolled/ten-flat collection; no method alone
    # proves a successful comparison or permits calling the subject positively ID'd.
    qualifying_capture = method in ("ten_rolled", "ten_flat")
    if method == "name_only":
        identification_note = "Name-only or non-unique identifier comparisons do not establish positive identification."
    elif qualifying_capture:
        identification_note = "Qualifying capture format reported; a reliable comparison result is still required."
    else:
        identification_note = "This simulation cannot establish an authorized positive identification."
    return {
        "source": definition_catalog()["source"],
        "input_persisted": False,
        "raw_identifiers_accepted": False,
        "role": request["role"],
        "classification": {
            "chri_indicated": is_chri,
            "pii_indicated": is_pii,
            "standalone_biometrics_are_not_automatically_chri": True,
            "classification_is_based_on_flags_only": True,
        },
        "identity": {
            "qualifying_fingerprint_capture_reported": qualifying_capture,
            "positive_identification_established": False,
            "note": identification_note,
        },
        "access": {
            "direct_iii_terminal_access_granted": False,
            "real_ngi_submission_enabled": False,
            "chri_dissemination_enabled": False,
            "rap_back_enabled": False,
            "media_sanitization_proven": False,
        },
        "findings": notes,
        "externally_verified": False,
        "production_ready": False,
        "summary": "Definition-based dry run only. Agency legal authority and actual security approvals remain unverified.",
    }

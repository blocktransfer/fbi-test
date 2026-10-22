"""Section 5 nonidentifying governance and agency-powers guardrails.

Dry-run interpretations only: no approvals, government decisions,
inquiries, post-termination inspections or mail are performed.
"""
from __future__ import annotations
from misc_provisions import (
    PARTIES, AUDITORS, FINAL_AUDITORS, INVESTIGATION_AUTHORITIES,
    FIRST_CLASS_MAIL,
)

class MiscInputError(ValueError):
    pass

def _required(data: dict, keys: set[str]) -> None:
    if type(data) is not dict or set(data) != keys:
        raise MiscInputError("Only the exact, nonidentifying Section 5 fields are accepted")

def _enum(value, options, field: str) -> None:
    if type(value) is not str or value not in options:
        raise MiscInputError("Invalid category for " + field)

def _flag(value, field: str) -> None:
    if type(value) is not bool:
        raise MiscInputError("Boolean required for " + field)

ASSETS = frozenset(("personnel", "systems", "networks", "facilities"))
RULES = frozenset(("outsourcing_standard", "cjis_security_policy", "recipient_channeler_contract"))
DIRECTIONS = frozenset(("stricter", "unchanged", "weaker"))
ACTORS = frozenset((
    "compact_council", "cjis_apb", "authorized_recipient", "channeler",
    "fbi", "compact_officer_chief_administrator", "us_attorney_general",
    "other",
))
MAIL_RECIPIENTS = frozenset((
    "fbi", "compact_council", "fbi_compact_officer", "us_attorney_general",
))

def scope_check(data: dict) -> dict:
    """§§5.01–5.03: covered supporting assets and no rights to outsiders."""
    _required(data, {"party", "asset", "supports_authorized_recipient", "rights_claimed"})
    _enum(data["party"], PARTIES | {"other"}, "party")
    _enum(data["asset"], ASSETS, "asset")
    _flag(data["supports_authorized_recipient"], "supports_authorized_recipient")
    _flag(data["rights_claimed"], "rights_claimed")
    covered = data["supports_authorized_recipient"]
    return {
        "sections": ["5.01", "5.02", "5.03"],
        "covered_by_section_5_01": covered,
        "asset_type": data["asset"],
        "party_named_by_section_5_02": data["party"] in PARTIES,
        "no_third_party_rights": True,
        "attempt_to_grant_rights_denied": True,
        "cjis_security_policy_incorporated_by_reference": True,
        "recipient_supporting_asset_may_be_excluded": False if covered else None,
        "actor_authority_verified": False,
        "new_rights_granted": False,
        "production_ready": False,
    }

def changes_check(data: dict) -> dict:
    """§§5.01, 5.04–5.05: never treat local declaration as legal waiver."""
    _required(data, {"instrument", "direction", "actor",
                     "compact_council_consent_reported", "us_ag_consultation_reported"})
    _enum(data["instrument"], RULES, "instrument")
    _enum(data["direction"], DIRECTIONS, "direction")
    _enum(data["actor"], ACTORS, "actor")
    for flag in ("compact_council_consent_reported", "us_ag_consultation_reported"):
        _flag(data[flag], flag)
    instrument, direction, actor = data["instrument"], data["direction"], data["actor"]
    if direction == "weaker":
        status = "blocked_pending_external_authority"
        basis = ("§5.05: reduced minimum security cannot be self-authorized. "
                 "Compact Council consent after consultation with U.S. Attorney General "
                 "requires authentic external documentation; no waiver can be issued here.")
    elif instrument == "outsourcing_standard":
        status = "requires_official_compact_council_process"
        basis = "§§5.01/5.05: only Compact Council may modify the Outsourcing Standard under 28 CFR part 906."
    elif instrument == "cjis_security_policy":
        status = "requires_official_cjis_apb_process"
        basis = "§5.05: CJIS Security Policy minimum changes require the CJIS APB process."
    else:
        status = "contract_review_only"
        basis = ("§§5.04–5.05: an Authorized Recipient–Channeler agreement may impose "
                 "stronger requirements. Contract and legal review remain external.")
    expected_actor = (
        "compact_council" if instrument == "outsourcing_standard" else
        "cjis_apb" if instrument == "cjis_security_policy" else
        "authorized_recipient_and_channeler"
    )
    return {
        "sections": ["5.01", "5.04", "5.05"],
        "status": status,
        "reason": basis,
        "reported_actor": actor,
        "formal_change_authority": expected_actor,
        "claimed_authority_sufficient": False,
        "consultation_or_consent_independently_verified": False,
        "lower_standard_automatically_accepted": False,
        "minimum_control_bypassed": False,
        "policy_or_contract_amended": False,
        "production_ready": False,
    }

AUDIT_PHASES = frozenset(("scheduled", "unscheduled", "post_termination_final"))
DECISIONS = frozenset(("investigate", "decline"))

def government_power_check(data: dict) -> dict:
    """§§5.06–5.07, actor check only, never authorizes actual inspection."""
    _required(data, {"kind", "actor", "action"})
    _enum(data["kind"], {"audit", "unauthorized_access_report"}, "kind")
    _enum(data["actor"], AUDITORS | FINAL_AUDITORS | {"other"}, "actor")
    _enum(data["action"], AUDIT_PHASES | DECISIONS, "action")
    kind, actor, action = data["kind"], data["actor"], data["action"]
    if kind == "audit":
        if action not in AUDIT_PHASES:
            raise MiscInputError("Audit action must be scheduled, unscheduled or post-termination final")
        allowed = actor in (FINAL_AUDITORS if action == "post_termination_final" else AUDITORS)
        section = "5.06"
    else:
        if action not in DECISIONS:
            raise MiscInputError("Report decision must be investigate or decline")
        allowed = actor in INVESTIGATION_AUTHORITIES
        section = "5.07"
    return {
        "section": section, "kind": kind, "action": action,
        "named_authority_for_action": allowed,
        "official_identity_verified": False,
        "authority_exercised": False,
        "audit_conducted": False,
        "investigation_started_or_declined": False,
        "decision_authorized_by_software": False,
        "official_coordination_required": True,
    }

def postage_instructions(data: dict) -> dict:
    """§5.08 First Class Mail to 2023-published routing address."""
    _required(data, {"addressee", "mail_method", "purpose"})
    _enum(data["addressee"], MAIL_RECIPIENTS, "addressee")
    _enum(data["mail_method"], {"first_class_mail"}, "mail_method")
    _enum(data["purpose"], {"notice", "assurance", "correspondence"}, "purpose")
    return {
        "section": "5.08",
        "requested_addressee": data["addressee"],
        "purpose": data["purpose"],
        "published_2023_routing": dict(FIRST_CLASS_MAIL),
        "verify_current_postal_instructions_with_responsible_authority": True,
        "letter_created": False,
        "mail_dispatched": False,
        "delivery_confirmed": False,
        "agency_acknowledgment_received": False,
        "legal_sufficiency_verified": False,
    }

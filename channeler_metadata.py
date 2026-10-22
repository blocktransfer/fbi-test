"""Synthetic-only format checks for §3.13 dissemination and §3.24 Rap Back.

No real CHRI or identifier values accepted; no records saved, sent or deleted.
An approved production system must retain authentic dissemination logs for
at least one year and protect the actual OCA/ORI, TCN, authority and means.
"""
from __future__ import annotations

from datetime import datetime
import re

from channeler_operations import utc, plus_year, ChannelerInputError

TEST_OCA = re.compile(r"^TEST-(?:OCA|ORI)-[A-Z0-9]{6,20}$")
TEST_TCN = re.compile(r"^TEST-TCN-[A-Z0-9]{6,24}$")
TEST_SUBSCRIPTION = re.compile(r"^TEST-RBS-[A-Z0-9]{6,24}$")
TEST_AUTHORITY = re.compile(r"^TEST-AUTH-[A-Z0-9]{6,24}$")
MEANS = frozenset({"test_secure_electronic", "test_offline_secure_transfer"})

def _fields(data: dict, keys: set) -> None:
    if type(data) is not dict or set(data) != keys:
        raise ChannelerInputError("Only the exact required synthetic metadata fields are permitted")

def _matching(key: str, value: object, pattern) -> None:
    if type(value) is not str or not pattern.fullmatch(value):
        raise ChannelerInputError(key + " must use a synthetic TEST- reference, not real identifiers")

def dissemination_dry_run(data: dict) -> dict:
    """§3.13 required dissemination fields, annual retention baseline."""
    _fields(data, {
        "recipient_oca_or_ori", "transaction_control_number",
        "disseminated_at", "statutory_authority_test_ref",
        "means", "as_of",
    })
    _matching("OCA/ORI", data["recipient_oca_or_ori"], TEST_OCA)
    _matching("TCN", data["transaction_control_number"], TEST_TCN)
    _matching("authority", data["statutory_authority_test_ref"], TEST_AUTHORITY)
    if type(data["means"]) is not str or data["means"] not in MEANS:
        raise ChannelerInputError("Unsupported synthetic dissemination method")
    when, now = utc(data["disseminated_at"]), utc(data["as_of"])
    if now < when:
        raise ChannelerInputError("Inspection time precedes dissemination")
    return {
        "section": "3.13",
        "minimum_retention_until_utc": plus_year(when).isoformat(),
        "all_five_required_log_elements_present": True,
        "statutory_authority_independently_verified": False,
        "log_record_saved": False, "real_identifiers_accepted": False,
        "real_chri_disclosed": False, "fbi_audit_performed": False,
        "production_ready": False,
    }

def rapback_link_dry_run(data: dict) -> dict:
    """§3.24: only synthetic TCN + Rap Back subscription reference."""
    _fields(data, {"transaction_control_number", "subscription_identifier"})
    _matching("TCN", data["transaction_control_number"], TEST_TCN)
    _matching("subscription", data["subscription_identifier"], TEST_SUBSCRIPTION)
    return {
        "section": "3.24", "expected_reference_fields": [
            "TCN", "Rap Back Subscription Identifier"
        ],
        "applicant_pii_accepted": False, "applicant_pii_stored": False,
        "reference_persisted": False, "real_rapback_subscription_created": False,
        "production_ready": False,
    }

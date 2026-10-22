"""Tests for all Miscellaneous Provisions, §§5.01–5.08."""
import unittest

from misc_provisions import catalog, CHECK_IDS, FIRST_CLASS_MAIL
from misc_guardrails import (
    MiscInputError, changes_check, government_power_check,
    postage_instructions, scope_check,
)


class SectionFiveTests(unittest.TestCase):
    def test_catalog_has_eight_sections_and_source_pages(self):
        c = catalog()
        self.assertEqual(c["sections"], [f"5.{n:02d}" for n in range(1, 9)])
        self.assertEqual(len(c["clauses"]), 8)
        self.assertEqual(c["check_count"], 17)
        self.assertEqual(len(CHECK_IDS), 17)
        self.assertEqual({e["pdf_page"] for e in c["clauses"]}, {"18", "19"})
        self.assertFalse(c["production_ready"])
        self.assertFalse(c["regulatory_change_authorized"])

    def test_mailing_address_from_section_5_08_not_verified_current(self):
        self.assertEqual(FIRST_CLASS_MAIL["recipient"], "FBI Compact Officer")
        self.assertEqual(FIRST_CLASS_MAIL["routing"], "BTC4")
        self.assertEqual(FIRST_CLASS_MAIL["organization"], "FBI CJIS Division")
        self.assertEqual(FIRST_CLASS_MAIL["street"], "1000 Custer Hollow Road")
        self.assertEqual(FIRST_CLASS_MAIL["city_state_zip"], "Clarksburg, WV 26306")
        self.assertFalse(FIRST_CLASS_MAIL["current_address_verified"])
        c = catalog()
        c["mailing"]["street"] = "tampered"
        self.assertEqual(catalog()["mailing"]["street"], "1000 Custer Hollow Road")

    def test_scope_includes_all_supporting_asset_classes(self):
        for asset in ("personnel", "systems", "networks", "facilities"):
            with self.subTest(asset=asset):
                r = scope_check({"party": "authorized_recipient", "asset": asset,
                                 "supports_authorized_recipient": True,
                                 "rights_claimed": False})
                self.assertTrue(r["covered_by_section_5_01"])
                self.assertFalse(r["recipient_supporting_asset_may_be_excluded"])
                self.assertTrue(r["cjis_security_policy_incorporated_by_reference"])

    def test_no_third_party_rights_even_when_requested(self):
        r = scope_check({"party": "other", "asset": "networks",
                         "supports_authorized_recipient": True,
                         "rights_claimed": True})
        self.assertFalse(r["party_named_by_section_5_02"])
        self.assertTrue(r["attempt_to_grant_rights_denied"])
        self.assertFalse(r["new_rights_granted"])

    def example_change(self, **overrides):
        data = {"instrument": "recipient_channeler_contract",
                "direction": "stricter",
                "actor": "authorized_recipient",
                "compact_council_consent_reported": False,
                "us_ag_consultation_reported": False}
        data.update(overrides)
        return data

    def test_stricter_contract_requirements_review_only(self):
        r = changes_check(self.example_change())
        self.assertEqual(r["status"], "contract_review_only")
        self.assertFalse(r["policy_or_contract_amended"])
        self.assertFalse(r["minimum_control_bypassed"])

    def test_weakening_minimum_blocks_even_with_self_reported_consent(self):
        for rule in ("outsourcing_standard", "cjis_security_policy",
                     "recipient_channeler_contract"):
            for actor in ("compact_council", "cjis_apb", "authorized_recipient"):
                r = changes_check(self.example_change(
                    instrument=rule, direction="weaker", actor=actor,
                    compact_council_consent_reported=True,
                    us_ag_consultation_reported=True))
                self.assertEqual(r["status"], "blocked_pending_external_authority")
                self.assertFalse(r["lower_standard_automatically_accepted"])
                self.assertFalse(r["consultation_or_consent_independently_verified"])

    def test_only_council_or_cjis_apb_procedure_for_rule_changes(self):
        council = changes_check(self.example_change(
            instrument="outsourcing_standard", actor="compact_council"))
        apb = changes_check(self.example_change(
            instrument="cjis_security_policy", actor="cjis_apb"))
        self.assertEqual(council["status"], "requires_official_compact_council_process")
        self.assertEqual(apb["status"], "requires_official_cjis_apb_process")
        self.assertFalse(council["claimed_authority_sufficient"])
        self.assertFalse(apb["claimed_authority_sufficient"])

    def test_government_audits_scheduled_and_unscheduled_by_named_actors(self):
        for actor in ("compact_officer_chief_administrator",
                      "compact_council", "us_attorney_general"):
            for action in ("scheduled", "unscheduled"):
                r = government_power_check({
                    "kind": "audit", "actor": actor, "action": action
                })
                self.assertTrue(r["named_authority_for_action"])
                self.assertFalse(r["audit_conducted"])

    def test_final_audit_rights_are_separately_scoped(self):
        for actor in ("compact_council", "us_attorney_general", "applicable_state"):
            r = government_power_check({"kind": "audit", "actor": actor,
                                        "action": "post_termination_final"})
            self.assertTrue(r["named_authority_for_action"])
        r = government_power_check({"kind": "audit",
                                   "actor": "compact_officer_chief_administrator",
                                   "action": "post_termination_final"})
        self.assertFalse(r["named_authority_for_action"])
        self.assertFalse(r["authority_exercised"])

    def test_authorities_can_investigate_or_decline(self):
        for action in ("investigate", "decline"):
            for actor in ("compact_officer_chief_administrator",
                          "compact_council", "us_attorney_general"):
                r = government_power_check({
                    "kind": "unauthorized_access_report", "actor": actor,
                    "action": action
                })
                self.assertTrue(r["named_authority_for_action"])
                self.assertFalse(r["investigation_started_or_declined"])

    def test_notices_assurances_correspondence_all_route_first_class(self):
        for purpose in ("notice", "assurance", "correspondence"):
            for party in ("fbi", "compact_council", "fbi_compact_officer",
                          "us_attorney_general"):
                r = postage_instructions({"purpose": purpose,
                                           "addressee": party,
                                           "mail_method": "first_class_mail"})
                self.assertEqual(r["published_2023_routing"]["method"], "First Class Mail")
                self.assertFalse(r["mail_dispatched"])
                self.assertFalse(r["delivery_confirmed"])
                self.assertTrue(r["verify_current_postal_instructions_with_responsible_authority"])

    def test_rejects_unapproved_postage_methods_and_mail_contents(self):
        data = {"purpose": "notice", "addressee": "fbi",
                "mail_method": "first_class_mail"}
        for bad in ({**data, "mail_method": "email"},
                    {**data, "applicant": "sensitive"},
                    {**data, "address": "private"},
                    {**data, "addressee": "other"}):
            with self.subTest(bad=bad), self.assertRaises(MiscInputError):
                postage_instructions(bad)

    def test_rejects_free_text_rights_and_personnel_identifiers(self):
        src = {"party": "channeler", "asset": "systems",
               "supports_authorized_recipient": True,
               "rights_claimed": False}
        for bad in ({**src, "name": "private"},
                    {**src, "asset": "unsupported"},
                    {**src, "rights_claimed": 1},
                    {**src, "supports_authorized_recipient": "yes"}):
            with self.subTest(bad=bad), self.assertRaises(MiscInputError):
                scope_check(bad)

    def test_rejects_invalid_policy_change_actor_or_extra_data(self):
        for bad in (
            self.example_change(actor="admin"),
            self.example_change(compact_council_consent_reported="yes"),
            self.example_change(person_name="private"),
            self.example_change(direction="unenforced"),
        ):
            with self.subTest(bad=bad), self.assertRaises(MiscInputError):
                changes_check(bad)

    def test_conflicting_audit_and_investigation_actions_rejected(self):
        for data in (
            {"kind": "audit", "actor": "compact_council", "action": "decline"},
            {"kind": "unauthorized_access_report", "actor": "compact_council", "action": "scheduled"},
            {"kind": "audit", "actor": "fbi", "action": "scheduled"},
            {"kind": "audit", "actor": "compact_council", "action": "scheduled", "person": "private"},
        ):
            with self.subTest(data=data), self.assertRaises(MiscInputError):
                government_power_check(data)

    def test_no_government_power_check_performs_action(self):
        r = government_power_check({"kind": "audit",
                                   "actor": "compact_council",
                                   "action": "post_termination_final"})
        self.assertFalse(r["official_identity_verified"])
        self.assertFalse(r["authority_exercised"])
        self.assertFalse(r["decision_authorized_by_software"])


if __name__ == "__main__":
    unittest.main()

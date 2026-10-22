"""Offline tests for all Section 2 controls and deadline calculations."""
from datetime import datetime, timedelta, timezone
import unittest

from authorized_recipient import catalog, deadlines, RecipientError, SPEC


class RecipientPolicyTests(unittest.TestCase):
    def test_all_fourteen_sections_and_source_pages(self):
        result = catalog()
        self.assertEqual(result["sections"], [f"2.{n:02d}" for n in range(1,15)])
        self.assertEqual(result["control_count"], 31)
        self.assertEqual(len(SPEC), 31)
        self.assertEqual(len({x["id"] for x in result["controls"]}), 31)
        self.assertEqual({x["pdf_page"] for x in result["controls"]}, {"8","9","10"})
        self.assertFalse(result["independently_verified"])
        self.assertFalse(result["production_ready"])

    def test_important_agreement_requirements_present(self):
        keys = {c["id"] for c in catalog()["controls"]}
        for key in ("2.01.permission", "2.02.incorporation", "2.04.audits_sanctions",
                    "2.08.written_contents", "2.10.reinstatement",
                    "2.11.inspections", "2.14.voluntary_termination_notice"):
            self.assertIn(key, keys)

    def test_optional_rights_not_misidentified_as_mandatory(self):
        optional = {c["id"] for c in catalog()["controls"] if c["optional"]}
        self.assertEqual(optional, {
            "2.09.termination_rights", "2.12.optional_audits", "2.13.stricter_requirements"
        })

    def plan(self, event, occurred="2026-10-22T12:00:00Z", **args):
        return deadlines({"event":event,"occurred_at":occurred,**args})

    def test_template_catalog_covers_all_section_two_subsections(self):
        from recipient_templates import template_catalog
        result = template_catalog()
        templates = result["templates"]
        self.assertEqual(len(templates), 9)
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["contains_actual_personal_data"])
        self.assertTrue(all(not t["notice_sent"] for t in templates))
        covered = {section for t in templates for section in t["sections"]}
        for n in range(1, 15):
            self.assertIn(f"2.{n:02d}", covered)

    def test_initial_approval_requires_arso_notice_within_30_days(self):
        plan=self.plan("initial_outsourcing_approval")
        self.assertEqual(plan["section"],"2.07")
        self.assertEqual(plan["external_due_utc"],"2026-11-21T12:00:00+00:00")
        self.assertFalse(plan["messages_sent"])

    def test_arpoc_and_arso_changes_30_calendar_days(self):
        for event,section in (("arpoc_change","2.06"),("arso_change","2.07")):
            p=self.plan(event)
            self.assertEqual(p["section"], section)
            self.assertEqual(p["external_due_utc"],"2026-11-21T12:00:00+00:00")

    def test_policy_update_60_days_or_earlier_renewal(self):
        plan=self.plan("policy_update_notice")
        self.assertEqual(plan["external_due_utc"],"2026-12-21T12:00:00+00:00")
        earlier=self.plan("policy_update_notice", renewal_at="2026-10-25T00:00:00Z")
        self.assertEqual(earlier["external_due_utc"],"2026-10-25T00:00:00+00:00")

    def test_pii_breach_hour_and_report_five_days_after_notice(self):
        p=self.plan("pii_breach",initial_notice_at="2026-10-22T12:30:00Z")
        self.assertEqual(p["external_due_utc"],"2026-10-22T13:00:00+00:00")
        self.assertEqual(p["written_report_due_utc"],"2026-10-27T12:30:00+00:00")
        self.assertFalse(p["requires_initial_notice_time"])

    def test_violation_four_hours_report_after_notice(self):
        p=self.plan("security_violation",initial_notice_at="2026-10-22T15:00:00Z")
        self.assertEqual(p["external_due_utc"],"2026-10-22T16:00:00+00:00")
        self.assertEqual(p["written_report_due_utc"],"2026-10-27T15:00:00+00:00")

    def test_written_report_due_remains_unknown_until_notice_time(self):
        for kind in ("security_violation","pii_breach"):
            p=self.plan(kind)
            self.assertTrue(p["requires_initial_notice_time"])
            self.assertIsNone(p["written_report_due_utc"])

    def test_termination_discovery_four_hours_and_voluntary_has_no_numeric_deadline(self):
        self.assertEqual(self.plan("contract_termination")["external_due_utc"],
                         "2026-10-22T16:00:00+00:00")
        voluntary=self.plan("early_voluntary_termination")
        self.assertEqual(voluntary["section"],"2.14")
        self.assertIsNone(voluntary["external_due_utc"])
        self.assertIn("Written notice",voluntary["instruction"])

    def test_all_result_types_refuse_external_verification(self):
        from authorized_recipient import EVENTS
        for event in EVENTS:
            p=self.plan(event)
            self.assertFalse(p["messages_sent"])
            self.assertFalse(p["automatically_verified"])
            self.assertFalse(p["legal_role_verified"])

    def test_invalid_or_extra_fields_rejected(self):
        for bad in [
            {"event":"pii_breach","occurred_at":"2026-10-22T12:00:00Z","name":"PII"},
            {"event":"imaginary","occurred_at":"2026-10-22T12:00:00Z"},
            {"event":"pii_breach","occurred_at":"2026-10-22T12:00:00"},
            {"event":"arpoc_change","occurred_at":"2026-10-22T12:00:00Z",
             "initial_notice_at":"2026-10-22T12:00:00Z"},
            {"event":"pii_breach","occurred_at":"2026-10-22T12:00:00Z",
             "renewal_at":"2026-10-22T13:00:00Z"},
            {"event":"pii_breach","occurred_at":"2026-10-22T12:00:00Z",
             "initial_notice_at":"2026-10-22T11:00:00Z"},
        ]:
            with self.subTest(case=bad), self.assertRaises(RecipientError):
                deadlines(bad)

    def test_require_utc_timestamp(self):
        with self.assertRaises(RecipientError):
            self.plan("arpoc_change", occurred="2026-10-22T12:00:00-04:00")

    def test_calendar_days_account_for_month_lengths(self):
        p=self.plan("arpoc_change","2026-02-01T00:00:00Z")
        self.assertEqual(p["external_due_utc"],"2026-03-03T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()

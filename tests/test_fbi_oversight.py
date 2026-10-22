"""Offline regression tests for Compact Council §4 FBI responsibilities."""
import unittest

from fbi_oversight import catalog, CHECK_IDS
from fbi_oversight_schedule import deadlines, OversightInputError


class OversightPolicyTests(unittest.TestCase):
    def test_complete_source_catalog_and_distinct_responsible_parties(self):
        result = catalog()
        self.assertEqual(result["sections"], ["4.%02d" % n for n in range(1, 11)])
        self.assertEqual(result["clause_count"], 11)  # includes §4.01(a)
        self.assertEqual(result["check_count"], 28)
        self.assertEqual(len(CHECK_IDS), 28)
        self.assertFalse(result["FBI_approval_verified"])
        self.assertFalse(result["agency_action_performed"])
        self.assertFalse(result["production_ready"])
        self.assertEqual({c["printed_page"] for c in result["clauses"]}, {"8", "9"})
        actors = {c["section"]: c["responsible_party"] for c in result["clauses"]}
        self.assertEqual(actors["4.01(a)"], "Compact Officer/Chief Administrator")
        self.assertEqual(actors["4.03"], "FBI")

    def test_important_written_approval_and_sampling_gates(self):
        for key in ("4.01.written_response", "4.01(a).combined_audit_program",
                    "4.01(a).representative_sampling",
                    "4.03.compact_officer_certification",
                    "4.04.successful_checks_list",
                    "4.05.recipient_oca", "4.05.channeler_ori",
                    "4.07.written_security_approval",
                    "4.08.written_training_approval",
                    "4.09.written_contingency_approval",
                    "4.10.network_change_approval"):
            self.assertIn(key, CHECK_IDS)

    def test_catalog_return_is_fresh(self):
        c = catalog()
        c["source"]["approved"] = "changed"
        c["checks"][0]["description"] = "changed"
        self.assertEqual(catalog()["source"]["approved"], "2023-11-29")
        self.assertNotEqual(catalog()["checks"][0]["description"], "changed")

    def test_60_calendar_day_policy_delivery(self):
        r = deadlines({"event": "policy_update_notification",
                       "occurred_at": "2026-10-22T12:00:00Z",
                       "as_of": "2026-10-23T00:00:00Z"})
        self.assertEqual(r["policy_versions_available_by_utc"], "2026-12-21T12:00:00+00:00")
        self.assertFalse(r["recipients_notified"])
        self.assertFalse(r["deadline_elapsed"])

    def test_24_hour_fbi_roster_update_not_an_access_grant(self):
        r = deadlines({"event": "personnel_access_change",
                       "occurred_at": "2026-10-22T12:00:00Z",
                       "as_of": "2026-10-24T00:00:00Z"})
        self.assertEqual(r["access_roster_updated_by_utc"], "2026-10-23T12:00:00+00:00")
        self.assertTrue(r["deadline_elapsed"])
        self.assertFalse(r["background_checks_completed"])

    def test_audit_90_day_certification_and_combined_first_year(self):
        r = deadlines({"event": "first_approved_chri_receipt",
                       "occurred_at": "2026-10-22T12:00:00Z",
                       "as_of": "2026-11-01T12:00:00Z"})
        self.assertEqual(r["fbi_initial_audit_and_certification_due_utc"],
                         "2027-01-20T12:00:00+00:00")
        self.assertEqual(r["combined_state_federal_first_sample_audit_due_utc"],
                         "2027-10-22T12:00:00+00:00")
        self.assertEqual(r["fbi_first_triennial_audit_reference_utc"],
                         "2029-10-22T12:00:00+00:00")
        self.assertTrue(r["fbi_certification_requires_copy_of_audit_results"])
        self.assertTrue(r["representative_sampling_required"])
        self.assertFalse(r["audits_conducted"])
        self.assertFalse(r["certification_delivered"])
        self.assertIn("planning anchor", r["scheduling_assumption"])

    def test_triennial_after_three_years(self):
        r = deadlines({"event": "first_approved_chri_receipt",
                       "occurred_at": "2023-10-22T12:00:00Z",
                       "as_of": "2026-10-22T12:00:00Z"})
        self.assertEqual(r["combined_state_federal_next_triennial_reference_utc"],
                         "2029-10-22T12:00:00+00:00")

    def test_one_year_uses_calendar_anniversary(self):
        r = deadlines({"event": "first_approved_chri_receipt",
                       "occurred_at": "2024-02-29T10:00:00Z",
                       "as_of": "2024-03-01T10:00:00Z"})
        self.assertEqual(r["fbi_one_year_audit_reference_utc"],
                         "2025-02-28T10:00:00+00:00")

    def test_fail_closed_without_identifiers_or_actual_chri(self):
        good = {"event": "first_approved_chri_receipt",
                "occurred_at": "2026-10-22T12:00:00Z",
                "as_of": "2026-10-22T12:00:00Z"}
        for extra in ("employee_name", "fingerprint", "OCA", "ORI", "CHRI",
                      "report_content", "sample_population", "approver"):
            with self.subTest(field=extra), self.assertRaises(OversightInputError):
                deadlines({**good, extra: "sensitive"})
        for bad in (
            {**good, "event": "fbi_approval"},
            {**good, "occurred_at": "2026-10-22T12:00:00"},
            {**good, "as_of": "2026-10-21T12:00:00Z"},
            {**good, "as_of": "2026-10-22T08:00:00-04:00"},
            {"event": "policy_update_notification", "occurred_at": good["occurred_at"]},
        ):
            with self.subTest(case=bad), self.assertRaises(OversightInputError):
                deadlines(bad)

    def test_no_calendar_event_claims_federal_action(self):
        for event in ("first_approved_chri_receipt", "personnel_access_change",
                      "policy_update_notification"):
            result = deadlines({"event": event, "occurred_at": "2026-10-22T12:00:00Z",
                                "as_of": "2026-10-22T12:00:00Z"})
            for flag in ("agency_approval_verified", "production_ready",
                         "audits_conducted", "recipients_notified",
                         "certification_delivered", "real_chri_processed"):
                self.assertFalse(result[flag])


if __name__ == "__main__":
    unittest.main()

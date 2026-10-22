"""Regression tests for each Section 3 Channeler planning boundary."""
import unittest

from channeler_policy import CHECK_IDS, CLAUSES, catalog
from channeler_operations import (
    ChannelerInputError, deadlines, retention_dry_run, training_dry_run,
    rapback_dry_run,
)


class ChannelerPolicyTests(unittest.TestCase):
    def test_all_25_clauses_and_every_check_unique(self):
        result = catalog()
        self.assertEqual(result["clause_count"], 25)
        self.assertEqual(result["sections"], [f"3.{i:02d}" for i in range(1, 26)])
        self.assertEqual(len(CHECK_IDS), result["check_count"])
        self.assertEqual(len(result["checks"]), result["check_count"])
        self.assertTrue(all(c["printed_page"] in ("3", "3–4", "4", "5", "6", "7")
                            for c in result["clauses"]))
        self.assertFalse(result["externally_approved"])
        self.assertFalse(result["actual_chri_processing_enabled"])

    def test_all_important_security_requirements_have_checklists(self):
        for required in ("3.05.fbi_written_program_approval", "3.08.pre_change_approval",
                         "3.09.contingency_plan", "3.10.access_audit",
                         "3.12.maximum_retention", "3.13.one_year_dissemination_log",
                         "3.18.fbi_access_notice", "3.19.annual_fbi_certification",
                         "3.23.recipient_validation", "3.24.minimal_rapback_refs",
                         "3.25.fbi_rapback_testing"):
            self.assertIn(required, CHECK_IDS)

    def test_catalog_copy_is_isolated(self):
        result = catalog()
        result["source"]["title"] = "tampered"
        result["checks"].clear()
        self.assertEqual(catalog()["clause_count"], 25)
        self.assertTrue(catalog()["checks"])

    def test_pii_breach_has_one_hour_and_report_five_days_from_discovery(self):
        result = deadlines({"event": "pii_breach_discovered", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertEqual(result["initial_due_utc"], "2026-10-22T13:00:00+00:00")
        self.assertEqual(result["written_report_due_utc"], "2026-10-27T12:00:00+00:00")
        self.assertEqual(result["report_deadline_basis"], "discovery")
        self.assertIn("FBI", result["recipients"])
        self.assertFalse(result["messages_sent"])

    def test_other_violation_four_hours_and_written_report(self):
        result = deadlines({"event": "security_violation_discovered", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertEqual(result["initial_due_utc"], "2026-10-22T16:00:00+00:00")
        self.assertEqual(result["written_report_due_utc"], "2026-10-27T12:00:00+00:00")

    def test_termination_has_four_hours_but_not_automatic_written_incident_report(self):
        result = deadlines({"event": "contract_termination_discovered", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertEqual(result["initial_due_utc"], "2026-10-22T16:00:00+00:00")
        self.assertIsNone(result["written_report_due_utc"])

    def test_policy_updates_sixty_calendar_days(self):
        result = deadlines({"event": "policy_update_received", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertEqual(result["initial_due_utc"], "2026-12-21T12:00:00+00:00")

    def test_access_roster_and_fbi_notice_24_hours(self):
        result = deadlines({"event": "employee_access_changed", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertEqual(result["initial_due_utc"], "2026-10-23T12:00:00+00:00")
        self.assertIn("24 hours", result["instruction"])

    def test_early_termination_no_invented_deadline(self):
        result = deadlines({"event": "early_voluntary_termination", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertIsNone(result["initial_due_utc"])
        self.assertIn("Written notice", result["instruction"])

    def test_recipient_exchange_termination_requires_secure_disposition(self):
        result = deadlines({"event": "recipient_exchange_terminated", "occurred_at": "2026-10-22T12:00:00Z"})
        self.assertIsNone(result["initial_due_utc"])
        self.assertIn("CHRI", result["instruction"])
        self.assertFalse(result["messages_sent"])

    def test_retention_max_30_calendar_days(self):
        result = retention_dry_run({
            "received_at": "2026-10-22T12:00:00Z", "as_of": "2026-10-25T12:00:00Z"})
        self.assertEqual(result["destroy_by_utc"], "2026-11-21T12:00:00+00:00")
        self.assertFalse(result["destruction_performed"])
        self.assertFalse(result["actual_chri_present"])

    def test_acknowledged_receipt_accelerates_destruction(self):
        result = retention_dry_run({
            "received_at": "2026-10-22T12:00:00Z",
            "acknowledged_at": "2026-10-22T14:00:00Z",
            "as_of": "2026-10-22T14:30:00Z",
        })
        self.assertEqual(result["destroy_by_utc"], "2026-10-22T14:00:00+00:00")
        self.assertTrue(result["overdue"])
        self.assertTrue(result["requires_immediate_destruction_after_confirmed_receipt"])

    def test_very_late_ack_cannot_extend_retention(self):
        result = retention_dry_run({
            "received_at": "2026-10-22T12:00:00Z",
            "acknowledged_at": "2026-12-22T12:00:00Z",
            "as_of": "2026-11-25T12:00:00Z",
        })
        self.assertEqual(result["destroy_by_utc"], "2026-11-21T12:00:00+00:00")
        self.assertTrue(result["overdue"])

    def test_training_before_assignment_and_annual_refresher(self):
        result = training_dry_run({
            "agreement_anniversary": "2026-01-01T00:00:00Z",
            "assignment_at": "2026-02-01T00:00:00Z",
            "last_training_at": "2026-01-20T00:00:00Z",
            "recipient_retains_training_by_contract": False,
            "as_of": "2026-10-22T12:00:00Z",
        })
        self.assertTrue(result["preassignment_training_reported"])
        self.assertEqual(result["next_training_due_utc"], "2027-01-20T00:00:00+00:00")
        self.assertEqual(result["next_fbi_certification_anniversary_utc"], "2027-01-01T00:00:00+00:00")
        self.assertFalse(result["fbi_certification_sent"])

    def test_recipient_retained_training_not_conflated_with_channeler_duty(self):
        result = training_dry_run({
            "agreement_anniversary": "2026-01-01T00:00:00Z",
            "assignment_at": "2026-02-01T00:00:00Z",
            "recipient_retains_training_by_contract": True,
            "as_of": "2026-10-22T12:00:00Z",
        })
        self.assertFalse(result["channeler_training_duty_applies"])
        self.assertIsNone(result["next_fbi_certification_anniversary_utc"])
        self.assertFalse(result["staff_access_enabled"])

    def test_rapback_annual_messaging_but_recipient_controls_validation(self):
        result = rapback_dry_run({
            "subscription_started_at": "2026-05-01T10:00:00Z",
            "as_of": "2026-10-22T12:00:00Z",
            "recipient_has_validated": True,
            "fbi_testing_and_approval_reported": True,
            "purpose": "synthetic_only",
        })
        self.assertEqual(result["next_annual_validation_message_utc"], "2027-05-01T10:00:00+00:00")
        self.assertEqual(result["validation_authority"], "Authorized Recipient only")
        self.assertFalse(result["validation_performed"])
        self.assertFalse(result["rapback_service_enabled"])
        self.assertFalse(result["fbi_approval_verified"])

    def test_annual_anniversary_not_fixed_365_days_on_leap_year(self):
        result = rapback_dry_run({
            "subscription_started_at": "2024-02-29T10:00:00Z",
            "as_of": "2024-03-01T10:00:00Z",
            "recipient_has_validated": False,
            "fbi_testing_and_approval_reported": False,
            "purpose": "synthetic_only",
        })
        self.assertEqual(result["next_annual_validation_message_utc"], "2025-02-28T10:00:00+00:00")

    def test_strict_input_schemas_block_personal_info_and_invalid_time(self):
        valid = {"event": "pii_breach_discovered", "occurred_at": "2026-10-22T12:00:00Z"}
        for bad in ({**valid, "name": "PRIVATE"}, {**valid, "fingerprint": "PII"},
                    {**valid, "event": "unknown"},
                    {**valid, "occurred_at": "2026-10-22T12:00:00-04:00"}):
            with self.subTest(case=bad), self.assertRaises(ChannelerInputError):
                deadlines(bad)
        with self.assertRaises(ChannelerInputError):
            retention_dry_run({"received_at": "2026-10-22T12:00:00Z",
                               "as_of": "2026-10-22T14:00:00Z", "tcn": "PRIVATE"})
        with self.assertRaises(ChannelerInputError):
            rapback_dry_run({"subscription_started_at": "2026-05-01T10:00:00Z",
                             "as_of": "2026-10-22T12:00:00Z", "recipient_has_validated": False,
                             "fbi_testing_and_approval_reported": False, "purpose": "synthetic_only",
                             "subscription_id": "PRIVATE"})

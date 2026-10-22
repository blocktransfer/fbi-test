"""Synthetic-only Section 3 dissemination and Rap Back record schema tests."""
import unittest
from channeler_metadata import dissemination_dry_run, rapback_link_dry_run
from channeler_operations import ChannelerInputError


class MetadataTests(unittest.TestCase):
    def example(self, **extra):
        request = {
            "recipient_oca_or_ori": "TEST-OCA-ABC123",
            "transaction_control_number": "TEST-TCN-ABC123",
            "disseminated_at": "2026-10-22T10:00:00Z",
            "statutory_authority_test_ref": "TEST-AUTH-ABC123",
            "means": "test_secure_electronic",
            "as_of": "2026-10-22T10:00:00Z",
        }
        request.update(extra)
        return request

    def test_all_five_fields_one_year_retention_and_no_storage(self):
        result = dissemination_dry_run(self.example())
        self.assertEqual(result["minimum_retention_until_utc"], "2027-10-22T10:00:00+00:00")
        self.assertTrue(result["all_five_required_log_elements_present"])
        for key in ("log_record_saved", "real_identifiers_accepted",
                    "real_chri_disclosed", "production_ready"):
            self.assertFalse(result[key])

    def test_february_anniversary_uses_calendar_year(self):
        result = dissemination_dry_run(self.example(
            disseminated_at="2024-02-29T00:00:00Z",
            as_of="2024-03-01T00:00:00Z"))
        self.assertEqual(result["minimum_retention_until_utc"], "2025-02-28T00:00:00+00:00")

    def test_any_real_or_free_text_identifier_is_rejected(self):
        for field,value in (
            ("recipient_oca_or_ori","123456789"),
            ("transaction_control_number","actual transaction"),
            ("statutory_authority_test_ref","18 USC 922"),
            ("means","email"),
        ):
            with self.subTest(field=field), self.assertRaises(ChannelerInputError):
                dissemination_dry_run(self.example(**{field:value}))

    def test_additional_chri_or_personal_fields_are_rejected(self):
        for key in ("person_name","chri","fingerprint","applicant_email"):
            with self.subTest(field=key), self.assertRaises(ChannelerInputError):
                dissemination_dry_run(self.example(**{key:"not allowed"}))

    def test_real_rapback_identifiers_never_accepted(self):
        result = rapback_link_dry_run({
            "transaction_control_number": "TEST-TCN-ABC123",
            "subscription_identifier": "TEST-RBS-ABC123",
        })
        self.assertFalse(result["applicant_pii_stored"])
        self.assertFalse(result["reference_persisted"])
        self.assertFalse(result["real_rapback_subscription_created"])

    def test_rapback_rejects_additional_identifiers(self):
        good = {"transaction_control_number":"TEST-TCN-ABC123",
                "subscription_identifier":"TEST-RBS-ABC123"}
        for bad in (
            {**good, "name":"Private"},
            {**good, "dob":"2000-01-01"},
            {**good, "subscription_identifier":"REAL-ABC123"},
            {**good, "transaction_control_number":"tcn-realdigits"},
        ):
            with self.subTest(fields=bad), self.assertRaises(ChannelerInputError):
                rapback_link_dry_run(bad)

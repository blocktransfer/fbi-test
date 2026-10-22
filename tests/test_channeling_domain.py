"""No real CHRI, fingerprints, names, or personal identifiers in fixtures."""
import unittest
from channeling_definitions import DEFINITIONS, definition_catalog
from channeling_assessment import ContextError, FIELDS, assess_definitions


def example(**overrides):
    data = {
        "role": "channeler",
        "recipient_kind": "government",
        "purpose": "licensing",
        "authority_basis": "federal_statute",
        "agreement_reported": True,
        "fbi_channeler_selection_reported": True,
        "direct_ngi_approval_reported": True,
        "same_entity_for_purpose": False,
        "arpoc_recipient_employee": True,
        "chief_admin_role_applies": False,
        "chief_admin_repository_employee": False,
        "has_criminal_history": False,
        "has_biometric_identifiers": True,
        "has_other_personal_identifiers": False,
        "identification_method": "ten_flat",
    }
    data.update(overrides)
    return data


class CatalogTests(unittest.TestCase):
    def test_section_one_has_exactly_25_numbered_definitions(self):
        catalog = definition_catalog()
        self.assertEqual(catalog["total"], 25)
        self.assertEqual(len(DEFINITIONS), 25)
        self.assertEqual(
            [x["section"] for x in catalog["entries"]],
            ["1.%02d" % n for n in range(1, 26)],
        )

    def test_all_definitions_have_pdf_page_provenance(self):
        for entry in definition_catalog()["entries"]:
            self.assertTrue(entry["term"])
            self.assertTrue(entry["summary"])
            self.assertTrue(entry["pdf_pages"])
            self.assertFalse(entry["external_approval_verified"])

    def test_catalog_return_cannot_mutate_source(self):
        first = definition_catalog()
        first["source"]["approved"] = "tampered"
        first["entries"][0]["term"] = "tampered"
        other = definition_catalog()
        self.assertEqual(other["source"]["approved"], "2023-11-29")
        self.assertNotEqual(other["entries"][0]["term"], "tampered")


class AssessmentTests(unittest.TestCase):
    def test_strict_nonidentifying_schema(self):
        self.assertEqual(set(example()), FIELDS)
        for invalid in (
            {**example(), "name": "unsafe"},
            {**example(), "fingerprint": "unsafe"},
            {**example(), "chri": "unsafe"},
            {k:v for k,v in example().items() if k != "role"},
        ):
            with self.assertRaises(ContextError):
                assess_definitions(invalid)

    def test_reject_nonboolean_values(self):
        for value in (1, 0, "yes", None, [], {}):
            with self.assertRaises(ContextError):
                assess_definitions(example(arpoc_recipient_employee=value))

    def test_fingerprints_alone_are_pii_not_chri(self):
        result = assess_definitions(example())
        self.assertFalse(result["classification"]["chri_indicated"])
        self.assertTrue(result["classification"]["pii_indicated"])
        self.assertFalse(result["identity"]["positive_identification_established"])

    def test_chri_flag_independent_of_biometrics(self):
        result = assess_definitions(example(
            has_criminal_history=True, has_biometric_identifiers=False
        ))
        self.assertTrue(result["classification"]["chri_indicated"])
        self.assertTrue(result["classification"]["pii_indicated"])

    def test_nonidentifiable_empty_flags_are_not_marked_pii(self):
        result = assess_definitions(example(
            has_criminal_history=False, has_biometric_identifiers=False,
            has_other_personal_identifiers=False
        ))
        self.assertFalse(result["classification"]["pii_indicated"])

    def test_name_only_cannot_establish_positive_identification(self):
        result = assess_definitions(example(identification_method="name_only"))
        self.assertFalse(result["identity"]["positive_identification_established"])
        self.assertFalse(result["identity"]["qualifying_fingerprint_capture_reported"])
        self.assertIn("Name-only", result["identity"]["note"])

    def test_ten_rolled_and_flat_never_claim_successful_identification(self):
        for method in ("ten_rolled", "ten_flat"):
            result = assess_definitions(example(identification_method=method))
            self.assertTrue(result["identity"]["qualifying_fingerprint_capture_reported"])
            self.assertFalse(result["identity"]["positive_identification_established"])

    def test_channeler_cannot_claim_same_purpose_recipient_role(self):
        result = assess_definitions(example(same_entity_for_purpose=True))
        check = next(item for item in result["findings"] if item["section"] == "1.05")
        self.assertEqual(check["state"], "blocked_by_reported_facts")

    def test_ar_poc_employee_and_chief_admin_employee_guardrails(self):
        result = assess_definitions(example(
            arpoc_recipient_employee=False, chief_admin_role_applies=True,
            chief_admin_repository_employee=False,
        ))
        bad = [item["section"] for item in result["findings"]
               if item["state"] == "blocked_by_reported_facts"]
        self.assertIn("1.03", bad)
        self.assertIn("1.07 / 1.11", bad)

    def test_nongovernment_cannot_rely_only_on_state_authority(self):
        result = assess_definitions(example(
            recipient_kind="nongovernmental",
            authority_basis="state_statute_attorney_general_approved"
        ))
        self.assertEqual(result["findings"][0]["state"], "blocked_by_reported_facts")

    def test_no_source_self_reporting_unlocks_real_features(self):
        result = assess_definitions(example())
        self.assertFalse(result["externally_verified"])
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["input_persisted"] is True)
        self.assertFalse(any(result["access"].values()))
        self.assertEqual(result["role"], "channeler")

    def test_invalid_enums_are_rejected(self):
        for key in ("role", "recipient_kind", "authority_basis", "purpose", "identification_method"):
            with self.assertRaises(ContextError):
                assess_definitions(example(**{key: "not_valid"}))

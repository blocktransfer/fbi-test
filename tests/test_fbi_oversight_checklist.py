"""Section 4 protected evidence tracking is only operator self-reporting."""
import os
from pathlib import Path
import tempfile
import unittest

from audit_journal import AuditJournal
from fbi_oversight import CHECK_IDS
from fbi_oversight_checklist import OversightChecklist, ChecklistError
from channeler_checklist import ChannelerChecklist
from recipient_checklist import RecipientChecklist


class OversightChecklistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.path = self.root / "fbi-oversight.json"
        self.audit = AuditJournal(self.root / "audit.jsonl")
        self.addCleanup(self.audit.close)
        self.checklist = OversightChecklist(self.path)

    def record(self, key="4.07.written_security_approval", reported=True, ref="REPORTED-ONLY-2026"):
        return self.checklist.update({
            "id": key, "reported": reported,
            "evidence_ref": ref if reported else None,
        }, self.audit)

    def test_initial_state_does_not_claim_fbi_approval(self):
        state = self.checklist.summary()
        self.assertEqual(state["reported_count"], 0)
        self.assertFalse(state["FBI_approval_verified"])
        self.assertFalse(state["production_ready"])
        self.assertFalse(self.path.exists())

    def test_all_28_items_can_be_reported_without_being_verified(self):
        self.assertEqual(len(CHECK_IDS), 28)
        for key in CHECK_IDS:
            self.assertFalse(self.record(key)["independently_verified"])
        reloaded = OversightChecklist(self.path).summary()
        self.assertEqual(reloaded["reported_count"], 28)
        self.assertFalse(reloaded["FBI_approval_verified"])
        self.assertFalse(reloaded["independently_verified"])
        self.assertFalse(reloaded["production_ready"])

    def test_file_permissions_and_sanitized_audit(self):
        self.record()
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        journal = (self.root / "audit.jsonl").read_text()
        self.assertIn("fbi_oversight_check_requested", journal)
        self.assertIn("fbi_oversight_check_saved", journal)
        self.assertNotIn("REPORTED-ONLY-2026", journal)

    def test_section_four_keys_are_isolated_from_other_roles(self):
        for klass in (RecipientChecklist, ChannelerChecklist):
            other = klass(self.root / (klass.__name__ + ".json"))
            with self.assertRaises(ChecklistError):
                other.update({
                    "id": "4.10.written_network_approval",
                    "reported": True, "evidence_ref": "REPORTED-ONLY-2026",
                }, self.audit)
        for key in ("2.01.permission", "3.08.fbi_diagram_approval"):
            with self.assertRaises(ChecklistError):
                self.record(key)

    def test_revoking_claim_deletes_reference(self):
        self.record()
        self.record(reported=False)
        state = self.checklist.summary()
        self.assertEqual(state["reported_count"], 0)
        self.assertIsNone(state["checks"]["4.07.written_security_approval"]["evidence_ref"])

    def test_rejects_free_text_and_identifiers(self):
        for value in ("Real Applicant", "foo@example.net", "/private/path",
                      "https://fbi.gov/record", "ABCDE", ""):
            with self.subTest(value=value), self.assertRaises(ChecklistError):
                self.record(ref=value)
        self.assertFalse(self.path.exists())

    def test_symlink_hardlink_and_world_readable_files_are_rejected(self):
        target = self.root / "target"
        target.write_text('{"schema":1,"checks":{}}')
        target.chmod(0o600)
        self.path.symlink_to(target)
        with self.assertRaises(ChecklistError):
            OversightChecklist(self.path)
        self.path.unlink()
        self.record()
        os.link(self.path, self.root / "hard-link")
        with self.assertRaises(ChecklistError):
            OversightChecklist(self.path)
        (self.root / "hard-link").unlink()
        self.path.chmod(0o644)
        with self.assertRaises(ChecklistError):
            OversightChecklist(self.path)

    def test_unreadable_or_corrupted_metadata_never_implies_completion(self):
        self.record()
        self.path.write_text('{"broken": true}')
        with self.assertRaises(ChecklistError):
            self.checklist.summary()


if __name__ == "__main__":
    unittest.main()

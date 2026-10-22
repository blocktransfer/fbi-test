"""Owner-only Section 5 evidence references are never regulatory approvals."""
from pathlib import Path
import os
import tempfile
import unittest

from audit_journal import AuditJournal
from misc_provisions import CHECK_IDS
from misc_checklist import MiscChecklist, ChecklistError
from recipient_checklist import RecipientChecklist
from channeler_checklist import ChannelerChecklist
from fbi_oversight_checklist import OversightChecklist


class MiscChecklistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)
        self.path = self.root / "section-five.json"
        self.journal = AuditJournal(self.root / "audit.jsonl")
        self.addCleanup(self.journal.close)
        self.checklist = MiscChecklist(self.path)

    def mark(self, key="5.05.no_local_waivers", enabled=True, reference="CONTROL-2026-001"):
        return self.checklist.update({
            "id": key, "reported": enabled,
            "evidence_ref": reference if enabled else None,
        }, self.journal)

    def test_empty_defaults_to_unverified_and_no_file(self):
        state = self.checklist.summary()
        self.assertEqual(state["reported_count"], 0)
        self.assertFalse(state["production_ready"])
        self.assertFalse(state["independently_verified"])
        self.assertFalse(self.path.exists())

    def test_all_seventeen_checks_remain_unverified(self):
        self.assertEqual(len(CHECK_IDS), 17)
        for key in CHECK_IDS:
            response = self.mark(key)
            self.assertFalse(response["independently_verified"])
            self.assertFalse(response["production_ready"])
        reopened = MiscChecklist(self.path)
        state = reopened.summary()
        self.assertEqual(state["reported_count"], 17)
        self.assertFalse(state["FBI_approval_verified"])

    def test_revocation_clears_claim_and_reference(self):
        self.mark()
        self.mark(enabled=False)
        state = self.checklist.summary()
        self.assertEqual(state["reported_count"], 0)
        self.assertIsNone(state["checks"]["5.05.no_local_waivers"]["evidence_ref"])

    def test_separate_from_all_other_sections(self):
        classes = (RecipientChecklist, ChannelerChecklist, OversightChecklist)
        for klass in classes:
            other = klass(self.root / (klass.__name__ + ".json"))
            with self.assertRaises(ChecklistError):
                other.update({
                    "id": "5.05.no_local_waivers",
                    "reported": True,
                    "evidence_ref": "CONTROL-2026-001",
                }, self.journal)
        for forbidden in ("2.01.permission", "3.05.it_program", "4.07.written_security_approval"):
            with self.assertRaises(ChecklistError):
                self.mark(key=forbidden)

    def test_owner_only_file_and_sanitized_audit(self):
        self.mark()
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        audit = (self.root / "audit.jsonl").read_text()
        self.assertIn("misc_check_requested", audit)
        self.assertIn("misc_check_saved", audit)
        self.assertNotIn("CONTROL-2026-001", audit)

    def test_no_arbitrary_personal_data_or_paths(self):
        for text in ("Someone Private", "someone@example.net", "/private/system",
                     "http://host.test/document", "", "SMALL"):
            with self.subTest(reference=text), self.assertRaises(ChecklistError):
                self.mark(reference=text)
        self.assertFalse(self.path.exists())

    def test_symlink_hardlink_and_loose_permissions_rejected(self):
        target = self.root / "other.json"
        target.write_text('{"schema":1,"checks":{}}')
        target.chmod(0o600)
        self.path.symlink_to(target)
        with self.assertRaises(ChecklistError):
            MiscChecklist(self.path)
        self.path.unlink()
        self.mark()
        os.link(self.path, self.root / "linked.json")
        with self.assertRaises(ChecklistError):
            MiscChecklist(self.path)
        (self.root / "linked.json").unlink()
        self.path.chmod(0o644)
        with self.assertRaises(ChecklistError):
            MiscChecklist(self.path)

    def test_corruption_fails_closed(self):
        self.mark()
        self.path.write_text('{not valid')
        with self.assertRaises(ChecklistError):
            self.checklist.summary()


if __name__ == "__main__":
    unittest.main()

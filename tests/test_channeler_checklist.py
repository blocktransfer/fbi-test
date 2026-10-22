"""Channeler checklist isolation and strict evidence metadata regression tests."""
import os
from pathlib import Path
import tempfile
import unittest

from audit_journal import AuditJournal
from channeler_checklist import ChannelerChecklist, ChecklistError
from channeler_policy import CHECK_IDS
from recipient_checklist import RecipientChecklist


class ChannelerChecklistTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        folder = Path(self.temporary.name)
        folder.chmod(0o700)
        self.channeler_path = folder / "channeler.json"
        self.recipient_path = folder / "recipient.json"
        self.log = AuditJournal(folder / "audit.jsonl")
        self.addCleanup(self.log.close)
        self.channeler = ChannelerChecklist(self.channeler_path)

    def mark(self, key="3.05.fbi_written_program_approval", reported=True, reference="UNVERIFIED-DOC-2026"):
        return self.channeler.update({
            "id": key, "reported": reported,
            "evidence_ref": reference if reported else None,
        }, self.log)

    def test_no_state_means_no_assumed_approval(self):
        state = self.channeler.summary()
        self.assertFalse(state["FBI_approval_verified"])
        self.assertFalse(state["production_ready"])
        self.assertFalse(state["independently_verified"])
        self.assertFalse(self.channeler_path.exists())

    def test_all_39_controls_are_allowed_but_unverified(self):
        for key in CHECK_IDS:
            result = self.mark(key)
            self.assertFalse(result["independently_verified"])
        state = ChannelerChecklist(self.channeler_path).summary()
        self.assertEqual(state["reported_count"], len(CHECK_IDS))
        self.assertEqual(len(CHECK_IDS), 39)
        self.assertFalse(state["FBI_approval_verified"])

    def test_recipient_and_channeler_records_cannot_be_cross_assigned(self):
        with self.assertRaises(ChecklistError):
            self.mark("2.01.permission")
        recipient = RecipientChecklist(self.recipient_path)
        with self.assertRaises(ChecklistError):
            recipient.update({
                "id":"3.05.fbi_written_program_approval",
                "reported":True,"evidence_ref":"UNVERIFIED-DOC-2026"
            }, self.log)
        self.assertFalse(self.recipient_path.exists())

    def test_owner_only_atomic_file_and_separate_audit_event_names(self):
        self.mark()
        self.assertEqual(self.channeler_path.stat().st_mode & 0o777, 0o600)
        record = self.channeler_path.read_text()
        self.assertIn("UNVERIFIED-DOC-2026", record)
        audit = (self.channeler_path.parent / "audit.jsonl").read_text()
        self.assertIn("channeler_check_requested", audit)
        self.assertIn("channeler_check_saved", audit)
        self.assertNotIn("UNVERIFIED-DOC-2026", audit)

    def test_revocation_clears_reference_and_count(self):
        self.mark()
        self.mark(reported=False)
        state = self.channeler.summary()
        self.assertEqual(state["reported_count"], 0)
        self.assertIsNone(state["checks"]["3.05.fbi_written_program_approval"]["evidence_ref"])

    def test_pii_and_file_paths_rejected_as_evidence(self):
        for value in ("my name", "private@example.com", "/secret/path",
                      "http://example.test/file", "", "1"):
            with self.subTest(value=value), self.assertRaises(ChecklistError):
                self.mark(reference=value)
        self.assertFalse(self.channeler_path.exists())

    def test_symlink_and_unsafe_permissions_fail_closed(self):
        target = self.channeler_path.parent / "other.json"
        target.write_text('{"schema":1,"checks":{}}')
        target.chmod(0o600)
        self.channeler_path.symlink_to(target)
        with self.assertRaises(ChecklistError):
            ChannelerChecklist(self.channeler_path)
        self.channeler_path.unlink()
        self.mark()
        self.channeler_path.chmod(0o644)
        with self.assertRaises(ChecklistError):
            ChannelerChecklist(self.channeler_path)

    def test_hardlink_is_rejected(self):
        self.mark()
        os.link(self.channeler_path, self.channeler_path.parent / "linked")
        with self.assertRaises(ChecklistError):
            ChannelerChecklist(self.channeler_path)


if __name__ == "__main__":
    unittest.main()

"""Security and persistence tests for synthetic-only Authorized Recipient checklist."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from recipient_checklist import ChecklistError, RecipientChecklist


class AuditStub:
    def __init__(self, fail=False):
        self.fail = fail
        self.events = []

    def append(self, event, outcome):
        if self.fail:
            raise RuntimeError("audit journal unavailable")
        self.events.append((event, outcome))


class RecipientChecklistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.base.chmod(0o700)
        self.path = self.base / "recipient-state.json"
        self.store = RecipientChecklist(self.path)
        self.audit = AuditStub()

    def update(self, **changes):
        data = {
            "id": "2.02.agreement",
            "reported": True,
            "evidence_ref": "DOCUMENT-2026-001",
        }
        data.update(changes)
        return self.store.update(data, self.audit)

    def test_empty_initial_state_is_unverified_and_not_created(self):
        self.assertFalse(self.path.exists())
        result = self.store.summary()
        self.assertEqual(result["reported_count"], 0)
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["FBI_approval_verified"])

    def test_update_is_private_and_persistent(self):
        result = self.update()
        self.assertTrue(result["reported"])
        self.assertFalse(result["independently_verified"])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.base.stat().st_mode & 0o777, 0o700)
        self.assertEqual(
            self.audit.events,
            [("recipient_check_requested", "started"),
             ("recipient_check_saved", "recorded")],
        )
        reloaded = RecipientChecklist(self.path).summary()
        self.assertEqual(reloaded["reported_count"], 1)
        self.assertEqual(reloaded["checks"]["2.02.agreement"]["evidence_ref"], "DOCUMENT-2026-001")
        self.assertFalse(reloaded["independently_verified"])

    def test_revocation_clears_previous_evidence(self):
        self.update()
        self.update(reported=False, evidence_ref=None)
        entry = self.store.summary()["checks"]["2.02.agreement"]
        self.assertFalse(entry["reported"])
        self.assertIsNone(entry["evidence_ref"])
        self.assertEqual(self.store.summary()["reported_count"], 0)

    def test_private_data_and_free_text_rejected(self):
        for unsafe in (
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"name: Citizen"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"personal@example.com"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"https://files.example/test.pdf"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"abc 123"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"ABC"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"DOC-2026","person":"Nobody"},
            {"id":"2.02.agreement","reported":1,"evidence_ref":"DOC-2026"},
            {"id":"2.02.agreement","reported":False,"evidence_ref":"DOC-2026"},
            {"id":"2.99.fictional","reported":True,"evidence_ref":"DOC-2026"},
        ):
            with self.subTest(case=unsafe), self.assertRaises(ChecklistError):
                self.store.update(unsafe, self.audit)
        self.assertFalse(self.path.exists())
        self.assertEqual(self.audit.events, [])

    def test_audit_failure_prevents_state_change(self):
        with self.assertRaises(RuntimeError):
            self.store.update({
                "id":"2.02.agreement","reported":True,"evidence_ref":"DOC-2026"
            }, AuditStub(fail=True))
        self.assertFalse(self.path.exists())

    def test_symlink_file_is_rejected(self):
        target = self.base / "other"
        target.write_text('{"schema":1,"checks":{}}')
        target.chmod(0o600)
        self.path.symlink_to(target)
        with self.assertRaises(ChecklistError):
            RecipientChecklist(self.path)

    def test_group_readable_file_is_rejected(self):
        self.path.write_text('{"schema":1,"checks":{}}')
        self.path.chmod(0o640)
        with self.assertRaises(ChecklistError):
            RecipientChecklist(self.path)

    def test_corrupted_document_is_fail_closed(self):
        self.path.write_bytes(b"{ broken json")
        self.path.chmod(0o600)
        with self.assertRaises(ChecklistError):
            self.store.summary()

    def test_unknown_control_key_is_rejected_on_load(self):
        self.path.write_text(json.dumps({
            "schema": 1,
            "checks": {"2.999.secret": {
                "reported": True, "evidence_ref": "DOC-2026",
                "recorded_at": "2026-10-22T12:00:00+00:00"
            }}
        }))
        self.path.chmod(0o600)
        with self.assertRaises(ChecklistError):
            self.store.summary()

    def test_hardlink_is_rejected(self):
        self.update()
        os.link(self.path, self.base / "linked-state")
        with self.assertRaises(ChecklistError):
            RecipientChecklist(self.path)

    def test_invalid_parent_permissions_fail(self):
        private = self.base / "subdir"
        private.mkdir(mode=0o700)
        private.chmod(0o755)
        with self.assertRaises(ChecklistError):
            RecipientChecklist(private / "unsafe.json")

    def test_boolean_flags_not_inferred_from_missing_evidence(self):
        with self.assertRaises(ChecklistError):
            self.update(evidence_ref=None)
        self.assertEqual(self.store.summary()["reported_count"], 0)

    def test_all_controls_can_be_recorded_as_claims_only(self):
        from authorized_recipient import SPEC
        for index, key in enumerate(SPEC, start=1):
            self.update(id=key, evidence_ref="DOCUMENT-%03d" % index)
        state = RecipientChecklist(self.path).summary()
        self.assertEqual(state["reported_count"], len(SPEC))
        self.assertFalse(state["production_ready"])
        self.assertFalse(state["independently_verified"])


if __name__ == "__main__":
    unittest.main()

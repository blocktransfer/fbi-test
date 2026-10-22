"""Offline HTTP integration tests for the loopback synthetic admin console."""

from http.client import HTTPConnection
from pathlib import Path
import tempfile
import json
import threading
import unittest
from unittest.mock import patch
import time
from uuid import uuid4

from audit_journal import AuditError, AuditJournal
from admin_ui import AdminServer, AdminState, synthetic_bytes
from fbi_sender import DeliveryUncertain, TEST_MAGIC


class AdminHttpTests(unittest.TestCase):
    def setUp(self):
        self.audit_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.audit_directory.cleanup)
        self.audit_path = str(Path(self.audit_directory.name) / "audit.jsonl")
        Path(self.audit_directory.name).chmod(0o700)
        self.recipient_path = str(Path(self.audit_directory.name) / "recipient.json")
        self.state = AdminState(
            env={"FBI_TEST_AUDIT_PATH": self.audit_path,
                 "FBI_TEST_RECIPIENT_PATH": self.recipient_path},
            token="test-" + "x" * 40
        )
        self.server = AdminServer(port=0, state=self.state)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)
        self.origin = self.server.origin
        self.assertEqual(self.request("POST", "/api/session", {"acknowledge": True})[0], 200)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.state.audit.close()

    def request(self, method, path, data=None, *, token=True, origin=True, host=None, content_type=True):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        self.addCleanup(connection.close)
        headers = {"Host": host or "127.0.0.1:" + str(self.server.server_port)}
        if token:
            headers["X-Admin-Token"] = self.state.token
        if origin:
            headers["Origin"] = self.origin
        if data is not None and content_type:
            headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode() if data is not None else None
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        if path in ("/", "/app.js", "/app.css"):
            return response.status, payload, dict(response.getheaders())
        try:
            return response.status, json.loads(payload), dict(response.getheaders())
        except ValueError:
            return response.status, payload, dict(response.getheaders())

    def test_audit_journal_persists_sanitized_events(self):
        self.assertEqual(self.request("POST", "/api/preview", {"padding": 0})[0], 200)
        audit_text = Path(self.audit_path).read_text()
        self.assertIn('"event":"session_acknowledged"', audit_text)
        self.assertIn('"event":"synthetic_preview"', audit_text)
        self.assertNotIn("agency-test-123", audit_text)
        self.assertNotIn("SYNTHETIC-NON-CJI", audit_text)
        self.assertEqual(Path(self.audit_path).stat().st_mode & 0o777, 0o600)
        # Restart verification of the journal's hash chain should succeed.
        second_reader = AuditJournal(self.audit_path)
        second_reader.close()

    def test_tampered_audit_journal_cannot_be_opened(self):
        self.state.audit.close()
        with open(self.audit_path, "ab") as handle:
            handle.write(b"corruption\n")
        with self.assertRaises(AuditError):
            AuditJournal(self.audit_path)

    def test_audit_changes_block_test_gateway_submission(self):
        self.set_ready()
        Path(self.audit_path).write_bytes(b"tampered")
        request = self.send_request()
        self.assertEqual(self.request("POST", "/api/send", request)[0], 503)
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_loopback_only(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_section_one_frontend_has_reference_and_dry_run_controls(self):
        status, page, _ = self.request("GET", "/", token=False)
        self.assertEqual(status, 200)
        self.assertIn(b'id="definition-list"', page)
        self.assertIn(b'id="section-one-form"', page)
        self.assertIn(b'name="has_biometric_identifiers"', page)
        status, script, _ = self.request("GET", "/app.js", token=False)
        self.assertEqual(status, 200)
        self.assertIn(b'"/api/section-one/assess"', script)
        self.assertIn(b"textContent", script)

    def test_assets_served_without_token(self):
        for asset in ("/", "/app.css", "/app.js"):
            status, content, headers = self.request("GET", asset, token=False)
            self.assertEqual(status, 200)
            self.assertGreater(len(content), 100)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_system_notice_blocks_api_until_acknowledgment(self):
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("GET", "/api/status")[0], 403)
        self.assertEqual(self.request("POST", "/api/preview", {"padding": 0})[0], 403)
        self.assertEqual(self.request("POST", "/api/session", {"acknowledge": False})[0], 400)
        self.assertEqual(self.request("POST", "/api/session", {"acknowledge": True})[0], 200)
        self.assertEqual(self.request("GET", "/api/status")[0], 200)

    def test_acknowledgment_needs_correct_admin_token(self):
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("POST", "/api/session", {"acknowledge": True}, token=False)[0], 401)
        self.assertFalse(self.state.notice_acknowledged)

    def test_logout_revokes_all_future_access(self):
        self.assertEqual(self.request("POST", "/api/logout", {})[0], 200)
        self.assertEqual(self.request("GET", "/api/status")[0], 401)
        self.assertEqual(self.request("POST", "/api/session", {"acknowledge": True})[0], 401)

    def test_incident_deadline_planner_never_sends_or_stores_details(self):
        status, result, _ = self.request("POST", "/api/incident-deadlines", {
            "role": "channeler",
            "category": "pii_breach",
            "discovered_at": "2026-10-22T10:00:00Z",
        })
        self.assertEqual(status, 200)
        self.assertEqual(result["external_notification_due_utc"], "2026-10-22T11:00:00+00:00")
        self.assertEqual(result["written_report_due_utc"], "2026-10-27T10:00:00+00:00")
        self.assertFalse(result["automatically_notified"])
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_incident_deadline_recipient_written_report_uses_initial_notice(self):
        status, result, _ = self.request("POST", "/api/incident-deadlines", {
            "role": "authorized_recipient",
            "category": "security_violation",
            "discovered_at": "2026-10-22T10:00:00Z",
            "initial_notice_at": "2026-10-22T13:00:00Z",
        })
        self.assertEqual(status, 200)
        self.assertEqual(result["internal_incident_report_due_utc"], "2026-10-22T11:00:00+00:00")
        self.assertEqual(result["external_notification_due_utc"], "2026-10-22T14:00:00+00:00")
        self.assertEqual(result["written_report_due_utc"], "2026-10-27T13:00:00+00:00")

    def test_incident_deadline_planner_rejects_personal_details(self):
        status, _, _ = self.request("POST", "/api/incident-deadlines", {
            "role": "channeler",
            "category": "pii_breach",
            "discovered_at": "2026-10-22T10:00:00Z",
            "name": "Do not include PII",
        })
        self.assertEqual(status, 400)

    def test_incident_deadline_planner_requires_auth_and_notice(self):
        data = {"role": "channeler", "category": "pii_breach", "discovered_at": "2026-10-22T10:00:00Z"}
        self.assertEqual(self.request("POST", "/api/incident-deadlines", data, token=False)[0], 401)
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("POST", "/api/incident-deadlines", data)[0], 403)

    def test_section_two_catalog_requires_auth_and_shows_all_sections(self):
        status, data, _ = self.request("GET", "/api/recipient")
        self.assertEqual(status, 200)
        self.assertEqual(data["catalog"]["sections"], [f"2.{i:02d}" for i in range(1,15)])
        self.assertFalse(data["progress"]["production_ready"])
        self.assertEqual(data["progress"]["reported_count"], 0)
        self.assertEqual(self.request("GET", "/api/recipient", token=False)[0], 401)

    def test_section_two_checklist_round_trip_and_private_file(self):
        item = {"id":"2.02.agreement", "reported":True, "evidence_ref":"AGREEMENT-2026"}
        status, result, _ = self.request("POST", "/api/recipient/check", item)
        self.assertEqual(status, 200)
        self.assertTrue(result["reported"])
        self.assertFalse(result["independently_verified"])
        self.assertEqual(self.request("GET", "/api/recipient")[1]["progress"]["reported_count"], 1)
        text = Path(self.recipient_path).read_text()
        self.assertIn("AGREEMENT-2026", text)
        self.assertEqual(Path(self.recipient_path).stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.request("POST", "/api/recipient/check", {
            "id":"2.02.agreement","reported":False,"evidence_ref":None})[0],200)
        self.assertEqual(self.request("GET", "/api/recipient")[1]["progress"]["reported_count"],0)

    def test_section_two_rejects_raw_personal_data_and_invalid_refs(self):
        for req in (
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"Person John Doe"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":"DOC-1234","email":"person@example.org"},
            {"id":"2.99.fake","reported":True,"evidence_ref":"DOC-1234"},
            {"id":"2.01.arpoc","reported":1,"evidence_ref":"DOC-1234"},
            {"id":"2.01.arpoc","reported":True,"evidence_ref":""},
        ):
            self.assertEqual(self.request("POST","/api/recipient/check",req)[0],400)

    def test_section_two_deadline_planner_nonpersistent(self):
        status, result, _ = self.request("POST","/api/recipient/deadlines",{
            "event":"pii_breach","occurred_at":"2026-10-22T12:00:00Z",
            "initial_notice_at":"2026-10-22T12:30:00Z"})
        self.assertEqual(status,200)
        self.assertEqual(result["external_due_utc"],"2026-10-22T13:00:00+00:00")
        self.assertEqual(result["written_report_due_utc"],"2026-10-27T12:30:00+00:00")
        self.assertFalse(result["messages_sent"])
        self.assertFalse(Path(self.recipient_path).exists())
        self.assertEqual(self.request("POST","/api/recipient/deadlines", {
            "event":"pii_breach","occurred_at":"2026-10-22T12:00:00Z","name":"unsafe"})[0],400)

    def test_all_section_one_definitions_available_only_to_authenticated_user(self):
        status, data, _ = self.request("GET", "/api/section-one")
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 25)
        self.assertEqual(data["entries"][0]["section"], "1.01")
        self.assertEqual(data["entries"][-1]["section"], "1.25")
        self.assertFalse(data["production_ready"])
        self.assertEqual(self.request("GET", "/api/section-one", token=False)[0], 401)
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("GET", "/api/section-one")[0], 403)

    def test_section_one_assessment_api_uses_strict_nonidentifying_schema(self):
        from channeling_assessment import FIELDS
        choices = {"role": "channeler", "recipient_kind": "government", "purpose": "licensing",
                   "authority_basis": "federal_statute", "identification_method": "ten_flat",
                   "has_biometric_identifiers": True}
        payload = {key: choices.get(key, False) for key in FIELDS}
        status, result, _ = self.request("POST", "/api/section-one/assess", payload)
        self.assertEqual(status, 200)
        self.assertFalse(result["production_ready"])
        self.assertTrue(result["classification"]["pii_indicated"])
        self.assertFalse(result["classification"]["chri_indicated"])
        self.assertEqual(self.state.status()["attempts"], 0)
        status, _, _ = self.request(
            "POST", "/api/section-one/assess", {**payload, "applicant_name": "not allowed"}
        )
        self.assertEqual(status, 400)
        self.assertIn('"event":"section_one_assessed"', Path(self.audit_path).read_text())
        self.assertNotIn("applicant_name", Path(self.audit_path).read_text())

    def test_section_one_assessment_requires_system_notice(self):
        from channeling_assessment import FIELDS
        choices = {"role": "channeler", "recipient_kind": "government", "purpose": "licensing",
                   "authority_basis": "federal_statute", "identification_method": "ten_flat",
                   "has_biometric_identifiers": True}
        payload = {key: choices.get(key, False) for key in FIELDS}
        self.assertEqual(
            self.request("POST", "/api/section-one/assess", payload, token=False)[0], 401
        )
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("POST", "/api/section-one/assess", payload)[0], 403)

    def test_security_readiness_catalog_is_never_certified(self):
        status, data, _ = self.request("GET", "/api/readiness")
        self.assertEqual(status, 200)
        self.assertFalse(data["production_ready"])
        self.assertFalse(data["FBI_approval_verified"])
        self.assertGreaterEqual(data["control_count"], 20)
        self.assertTrue(all(not row["is_fully_verified"] for row in data["controls"]))
        self.assertIn("AC-8", [row["section"] for row in data["controls"]])
        self.assertIn("3.12", [row["section"] for row in data["controls"]])
        self.assertIn("2.08", [row["section"] for row in data["controls"]])

    def test_readiness_requires_auth_and_system_notice(self):
        self.assertEqual(self.request("GET", "/api/readiness", token=False)[0], 401)
        self.state.notice_acknowledged = False
        self.assertEqual(self.request("GET", "/api/readiness")[0], 403)

    def test_authentication_on_status(self):
        self.assertEqual(self.request("GET", "/api/status", token=False)[0], 401)
        self.assertEqual(self.request("GET", "/api/status")[0], 200)

    def test_invalid_logons_lock_token_after_five_attempts(self):
        for _ in range(5):
            code, _, _ = self.request("GET", "/api/status", token=False)
            self.assertEqual(code, 401)
        self.assertTrue(self.state.session_locked)
        self.assertEqual(self.request("GET", "/api/status")[0], 401)

    def test_idle_session_expiration_is_enforced_by_server(self):
        self.state.last_authenticated = time.monotonic() - 901
        self.assertEqual(self.request("GET", "/api/status")[0], 401)
        self.assertTrue(self.state.session_expired)

    def test_absolute_session_expiration_is_enforced(self):
        self.state.session_started = time.monotonic() - (8 * 3600 + 1)
        self.assertEqual(self.request("GET", "/api/status")[0], 401)
        self.assertTrue(self.state.session_expired)

    def test_failure_window_prunes_prior_attempts(self):
        self.state.failed_logons.append(time.monotonic() - 901)
        self.assertEqual(self.request("GET", "/api/status", token=False)[0], 401)
        self.assertFalse(self.state.session_locked)
        self.assertEqual(len(self.state.failed_logons), 1)

    def test_successful_authentication_clears_failure_counter(self):
        for _ in range(4):
            self.assertEqual(self.request("GET", "/api/status", token=False)[0], 401)
        self.assertEqual(self.request("GET", "/api/status")[0], 200)
        self.assertFalse(self.state.failed_logons)
        self.assertEqual(self.request("GET", "/api/status", token=False)[0], 401)
        self.assertFalse(self.state.session_locked)

    def test_cross_origin_post_rejected(self):
        status, _, _ = self.request("POST", "/api/preview", {"padding": 0}, origin=False)
        self.assertEqual(status, 403)

    def test_rebinding_host_rejected(self):
        status, _, _ = self.request("GET", "/api/status", host="evil.example")
        self.assertEqual(status, 403)

    def test_private_preview_never_networks(self):
        status, data, _ = self.request("POST", "/api/preview", {"padding": 1024})
        self.assertEqual(status, 200)
        self.assertEqual(data["bytes"], len(TEST_MAGIC) + 2 + 1024)
        self.assertFalse(data["network_activity"])
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_preview_invalid_values_rejected(self):
        for value in (True, -1, 10, 100000, None, "1024"):
            self.assertEqual(self.request("POST", "/api/preview", {"padding": value})[0], 400)
        self.assertEqual(self.request("POST", "/api/preview", {"padding": 0, "biometrics": "private"})[0], 400)

    def test_get_unknown_and_query_routes_do_not_work(self):
        self.assertEqual(self.request("GET", "/api/fingerprint")[0], 404)
        self.assertEqual(self.request("GET", "/?token=secret")[0], 404)

    def test_send_is_disabled_without_configuration(self):
        status, _, _ = self.request("POST", "/api/send", self.send_request())
        self.assertEqual(status, 400)
        self.assertEqual(self.state.status()["attempts"], 0)

    def send_request(self, **changes):
        payload = {
            "padding": 256,
            "authorization_ref": "agency-test-123",
            "confirmed": True,
            "request_id": str(uuid4()),
        }
        payload.update(changes)
        return payload

    def set_ready(self):
        self.state.env.update({
            "FBI_TEST_ENDPOINT": "https://test.example/ingest",
            "FBI_TEST_APPROVED_HOST": "test.example",
            "FBI_TEST_CA_BUNDLE": "/missing/ca",
            "FBI_TEST_CLIENT_CERT": "/missing/cert",
            "FBI_TEST_CLIENT_KEY": "/missing/key",
            "FBI_TEST_AUTHORIZATION_REF": "agency-test-123",
            "FBI_TEST_ENABLE_GATEWAY": "synthetic-only",
        })

    def test_gateway_requires_explicit_synthetic_only_operator_enablement(self):
        self.set_ready()
        self.assertTrue(self.state.gateway_ready())
        self.state.env["FBI_TEST_ENABLE_GATEWAY"] = "production"
        self.assertFalse(self.state.gateway_ready())
        self.assertEqual(self.request("POST", "/api/send", self.send_request())[0], 400)

    def test_reference_must_match_configured_test_authorization(self):
        self.set_ready()
        self.assertEqual(
            self.request("POST", "/api/send", self.send_request(
                authorization_ref="different-approval-123"
            ))[0], 400
        )
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_confirmation_required_even_with_gateway(self):
        self.set_ready()
        self.assertEqual(self.request("POST", "/api/send", self.send_request(confirmed=False))[0], 400)
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_rejects_additional_fields_and_invalid_reference(self):
        self.set_ready()
        self.assertEqual(self.request("POST", "/api/send", self.send_request(authorization_ref="no"))[0], 400)
        self.assertEqual(self.request("POST", "/api/send", self.send_request(payload="real data"))[0], 400)
        self.assertEqual(self.state.status()["attempts"], 0)

    def test_test_gateway_send_only_once_and_deduplicates(self):
        self.set_ready()
        observed = []

        class Gateway:
            def send(self, data, submission_id):
                observed.append((data, submission_id))
                return 202

        with patch.object(AdminState, "gateway", return_value=Gateway()):
            request = self.send_request()
            status, result, _ = self.request("POST", "/api/send", request)
            self.assertEqual(status, 200)
            self.assertEqual(result["http_status"], 202)
            self.assertEqual(result["outcome"], "http_2xx_not_fbi_acceptance")
            self.assertEqual(len(observed), 1)
            self.assertEqual(observed[0][0], synthetic_bytes(256))
            self.assertEqual(self.request("POST", "/api/send", request)[0], 409)
            self.assertEqual(len(observed), 1)
        self.assertEqual(self.state.status()["attempts"], 1)
        self.assertEqual(self.state.status()["accepted_http"], 1)
        status, data, _ = self.request("GET", "/api/activity")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["events"]), 1)
        self.assertNotIn("agency-test-123", json.dumps(data))
        self.assertNotIn("SYNTHETIC", json.dumps(data))

    def test_network_uncertainty_returns_502_without_retry(self):
        self.set_ready()
        call_count = [0]

        class UncertainGateway:
            def send(self, data, submission_id):
                call_count[0] += 1
                raise DeliveryUncertain("Network timeout; uncertain")

        with patch.object(AdminState, "gateway", return_value=UncertainGateway()):
            req = self.send_request()
            status, message, _ = self.request("POST", "/api/send", req)
            self.assertEqual(status, 502)
            self.assertIn("do not retry", message["error"])
            self.assertEqual(self.request("POST", "/api/send", req)[0], 409)
            self.assertEqual(call_count[0], 1)
        status, data, _ = self.request("GET", "/api/activity")
        self.assertEqual(data["events"][0]["outcome"], "unknown_delivery_do_not_retry")

    def test_wrong_content_type_rejected(self):
        self.assertEqual(
            self.request("POST", "/api/preview", {"padding": 0}, content_type=False)[0], 415
        )

    def test_synthetic_bytes_are_deterministic(self):
        self.assertEqual(synthetic_bytes(0), TEST_MAGIC + b"\x00\x01")
        self.assertEqual(synthetic_bytes(256), TEST_MAGIC + b"\x00\x01" + bytes(256))


if __name__ == "__main__":
    unittest.main()

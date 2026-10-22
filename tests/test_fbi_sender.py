"""Security regression tests: synthetic fixtures only, never actual biometrics."""

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fbi_sender as sender


class MockGateway:
    def __init__(self, status=202):
        self.status = status
        self.calls = []

    def send(self, payload, submission_id):
        self.calls.append((payload, submission_id))
        return self.status


class SyntheticSenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "synthetic.bin"
        self.path.write_bytes(sender.TEST_MAGIC + b"\x00\x01")
        self.path.chmod(0o600)

    def test_valid_synthetic_payload(self):
        self.assertEqual(sender.read_synthetic_file(self.path), sender.TEST_MAGIC + b"\x00\x01")

    def test_empty_input_rejected(self):
        self.path.write_bytes(b"")
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    def test_real_or_unmarked_input_rejected(self):
        self.path.write_bytes(b"EBTS or biometric data is not allowed here")
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    def test_marker_cannot_smuggle_real_or_arbitrary_bytes(self):
        self.path.write_bytes(sender.TEST_MAGIC + b"\x00\x01" + b"private biometric record")
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    def test_deterministic_zero_padding_is_accepted(self):
        self.path.write_bytes(sender.TEST_MAGIC + b"\x00\x01" + b"\x00" * 1024)
        self.assertEqual(len(sender.read_synthetic_file(self.path)), len(sender.TEST_MAGIC) + 1026)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions required")
    def test_world_readable_file_rejected(self):
        self.path.chmod(0o644)
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    @unittest.skipUnless(os.name == "posix", "symlink protections tested on POSIX")
    def test_symlink_rejected(self):
        alias = Path(self.temp.name) / "alias"
        alias.symlink_to(self.path)
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(alias)

    @unittest.skipUnless(os.name == "posix", "hardlink protections tested on POSIX")
    def test_hardlink_rejected(self):
        alias = Path(self.temp.name) / "hardlink"
        os.link(self.path, alias)
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    def test_oversized_file_rejected_before_read(self):
        with self.path.open("r+b") as handle:
            handle.truncate(sender.MAX_TEST_BYTES + 1)
        with self.assertRaises(sender.SenderError):
            sender.read_synthetic_file(self.path)

    def test_bad_authorization_never_calls_gateway(self):
        gateway = MockGateway()
        with self.assertRaises(sender.SenderError):
            sender.submit_synthetic(self.path, gateway, "bad")
        self.assertFalse(gateway.calls)

    def test_success_receipt_contains_no_payload_or_file_path(self):
        gateway = MockGateway()
        receipt = sender.submit_synthetic(self.path, gateway, "agency-test-123")
        self.assertEqual(len(gateway.calls), 1)
        self.assertEqual(gateway.calls[0][0], sender.TEST_MAGIC + b"\x00\x01")
        audit = json.dumps(receipt.as_audit_event())
        self.assertIn("http_2xx_not_fbi_acceptance", audit)
        self.assertNotIn(self.temp.name, audit)
        self.assertNotIn("SYNTHETIC-NON-CJI", audit)
        self.assertNotIn("agency-test-123", audit)

    def test_inspection_is_local_and_payload_is_not_printed(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = sender.main(["inspect-test", str(self.path)])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["bytes"], len(sender.TEST_MAGIC) + 2)
        self.assertNotIn("SYNTHETIC-NON-CJI", output.getvalue())


class GatewayTests(unittest.TestCase):
    def test_http_url_rejected_before_certificate_loading(self):
        with self.assertRaises(sender.SenderError):
            sender.ApprovedTestGateway(
                "http://test.example/upload", "test.example", "ca", "cert", "key"
            )

    def test_wrong_host_rejected(self):
        with self.assertRaises(sender.SenderError):
            sender.ApprovedTestGateway(
                "https://other.example/upload", "test.example", "ca", "cert", "key"
            )

    def test_query_string_rejected(self):
        with self.assertRaises(sender.SenderError):
            sender.ApprovedTestGateway(
                "https://test.example/upload?secret=x", "test.example", "ca", "cert", "key"
            )

    def _gateway(self):
        class Context:
            def load_cert_chain(self, *args):
                pass
        context = Context()
        with patch.object(sender.ssl, "create_default_context", return_value=context):
            gateway = sender.ApprovedTestGateway(
                "https://test.example/upload", "test.example", "ca", "cert", "key"
            )
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, sender.ssl.CERT_REQUIRED)
        return gateway

    def test_posts_once_with_no_payload_logging(self):
        gateway = self._gateway()
        requests = []

        class Connection:
            def __init__(self, *args, **kwargs):
                self.closed = False

            def request(self, method, path, body, headers):
                requests.append((method, path, body, headers))

            def getresponse(self):
                return type("Response", (), {"status": 202})()

            def close(self):
                self.closed = True

        with patch.object(sender.http.client, "HTTPSConnection", Connection):
            status = gateway.send(sender.TEST_MAGIC, "one-submission")
        self.assertEqual(status, 202)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0][0:3], ("POST", "/upload", sender.TEST_MAGIC))
        self.assertEqual(requests[0][3]["X-Test-Submission-ID"], "one-submission")

    def test_redirect_is_not_followed(self):
        gateway = self._gateway()

        class Connection:
            def __init__(self, *args, **kwargs):
                pass

            def request(self, *args, **kwargs):
                pass

            def getresponse(self):
                return type("Response", (), {"status": 302})()

            def close(self):
                pass

        with patch.object(sender.http.client, "HTTPSConnection", Connection):
            with self.assertRaises(sender.SenderError):
                gateway.send(sender.TEST_MAGIC, "id")

    def test_network_timeout_reports_uncertain_delivery(self):
        gateway = self._gateway()

        class Connection:
            def __init__(self, *args, **kwargs):
                pass

            def request(self, *args, **kwargs):
                raise TimeoutError()

            def close(self):
                pass

        with patch.object(sender.http.client, "HTTPSConnection", Connection):
            with self.assertRaises(sender.DeliveryUncertain):
                gateway.send(sender.TEST_MAGIC, "id")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Loopback-only, token-protected admin UI for synthetic sender testing.

This is a local development console, not an FBI-connected or CJIS-certified UI.
Never enter CJI, fingerprints, actual biometric records, or PII.
"""

from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlsplit
from uuid import uuid4

from audit_journal import AuditError, AuditJournal
from security_controls import readiness_register

from fbi_sender import (
    AUTHORIZATION_PATTERN, ApprovedTestGateway, DeliveryUncertain, SenderError,
    TEST_MAGIC, TestReceipt,
)

ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
ROOT = Path(__file__).resolve().parent / "web"
PADDING_OPTIONS = frozenset((0, 256, 1024, 4096))
GATEWAY_ENV = (
    "FBI_TEST_ENDPOINT",
    "FBI_TEST_APPROVED_HOST",
    "FBI_TEST_CA_BUNDLE",
    "FBI_TEST_CLIENT_CERT",
    "FBI_TEST_CLIENT_KEY",
)
REQUEST_ID_PATTERN = re.compile(r"^[a-f0-9]{8}-[a-f0-9-]{27,40}$")
# Defense in depth for the local *synthetic-only* console; not an IA-2 MFA system.
FAILURE_WINDOW_SECONDS = 15 * 60
MAX_FAILED_LOGONS = 5
IDLE_TIMEOUT_SECONDS = 15 * 60
MAX_SESSION_SECONDS = 8 * 60 * 60


def synthetic_bytes(padding: int) -> bytes:
    """Fixed non-biometric bytes only. Caller cannot supply payload contents."""
    if type(padding) is not int or padding not in PADDING_OPTIONS:
        raise SenderError("Invalid synthetic padding size")
    return TEST_MAGIC + b"\x00\x01" + bytes(padding)


class AdminState:
    def __init__(self, env: dict[str, str] | None = None, token: str | None = None):
        self.env = dict(os.environ if env is None else env)
        default_audit = Path.home() / ".blocktransfer-fbi-test" / "audit.jsonl"
        self.audit = AuditJournal(self.env.get("FBI_TEST_AUDIT_PATH", str(default_audit)))
        self.token = secrets.token_urlsafe(32) if token is None else token
        self.events: deque[dict] = deque(maxlen=25)
        self.seen_requests: set[str] = set()
        self.sending = False
        self.lock = threading.Lock()
        self.session_started = time.monotonic()
        self.last_authenticated = self.session_started
        self.failed_logons: deque[float] = deque()
        self.session_locked = False
        self.session_expired = False
        self.notice_acknowledged = False

    def authenticate(self, candidate: str) -> bool:
        """AC-7-style lockout and local session timeout, enforced server-side.

        Restart is the only local unlock mechanism. No authentication failure
        ever re-enables a timed-out or locked token.
        """
        now = time.monotonic()
        with self.lock:
            if self.session_locked or self.session_expired:
                return False
            if (now - self.session_started >= MAX_SESSION_SECONDS
                    or now - self.last_authenticated >= IDLE_TIMEOUT_SECONDS):
                self.audit.append("session_expired", "expired")
                self.session_expired = True
                return False
            if candidate and secrets.compare_digest(candidate, self.token):
                self.last_authenticated = now
                self.failed_logons.clear()
                return True
            while self.failed_logons and now - self.failed_logons[0] >= FAILURE_WINDOW_SECONDS:
                self.failed_logons.popleft()
            self.audit.append("auth_failure", "denied")
            self.failed_logons.append(now)
            if len(self.failed_logons) >= MAX_FAILED_LOGONS:
                self.audit.append("auth_lockout", "locked")
                self.session_locked = True
            return False

    def acknowledge_use(self) -> None:
        with self.lock:
            self.audit.append("session_acknowledged", "acknowledged")
            self.notice_acknowledged = True

    def terminate_session(self) -> None:
        with self.lock:
            self.audit.append("logout", "terminated")
            self.session_expired = True
            self.notice_acknowledged = False

    def use_authorized(self) -> bool:
        with self.lock:
            return self.notice_acknowledged and not self.session_expired and not self.session_locked

    def gateway_ready(self) -> bool:
        return all(self.env.get(key) for key in GATEWAY_ENV)

    def status(self) -> dict:
        with self.lock:
            events = list(self.events)
            sending = self.sending
        return {
            "mode": "synthetic_only",
            "gateway_configured": self.gateway_ready(),
            "gateway_host": self.env.get("FBI_TEST_APPROVED_HOST", "") if self.gateway_ready() else None,
            "sending": sending,
            "attempts": len(events),
            "accepted_http": sum(e["outcome"] == "http_2xx_not_fbi_acceptance" for e in events),
            "history_volatile": True,
            "session_idle_timeout_seconds": IDLE_TIMEOUT_SECONDS,
            "session_absolute_timeout_seconds": MAX_SESSION_SECONDS,
            "mfa_configured": False,
            "audit_journal_local": True,
            "audit_integrity_external_anchor": False,
            "audit_records_retention_verified": False,
        }

    def gateway(self) -> ApprovedTestGateway:
        if not self.gateway_ready():
            raise SenderError("Test gateway is not configured")
        return ApprovedTestGateway(
            self.env["FBI_TEST_ENDPOINT"],
            self.env["FBI_TEST_APPROVED_HOST"],
            self.env["FBI_TEST_CA_BUNDLE"],
            self.env["FBI_TEST_CLIENT_CERT"],
            self.env["FBI_TEST_CLIENT_KEY"],
        )

    def send(self, request: dict) -> dict:
        if not self.gateway_ready():
            raise SenderError("Test gateway is not configured")
        if set(request) != {"padding", "authorization_ref", "request_id", "confirmed"}:
            raise SenderError("Unexpected test submission fields")
        payload = synthetic_bytes(request["padding"])
        auth = request["authorization_ref"]
        if not isinstance(auth, str) or not AUTHORIZATION_PATTERN.fullmatch(auth):
            raise SenderError("Valid agency test authorization reference required")
        if request["confirmed"] is not True:
            raise SenderError("Explicit synthetic-only confirmation required")
        request_id = request["request_id"]
        if not isinstance(request_id, str) or not REQUEST_ID_PATTERN.fullmatch(request_id):
            raise SenderError("Invalid single-use request identifier")
        with self.lock:
            if request_id in self.seen_requests:
                raise SenderError("Request already used; no automatic resubmission")
            if self.sending:
                raise SenderError("Another test is in progress")
            submission_id = str(uuid4())
            # The durable attempt record is mandatory before any network action.
            self.audit.append("gateway_started", "started", submission_id=submission_id)
            self.sending = True
            self.seen_requests.add(request_id)
        event = {
            "event": "synthetic_gateway_submission",
            "submission_id": submission_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "outcome": "unknown_delivery_do_not_retry",
            "http_status": None,
        }
        try:
            # No untrusted bytes, file paths, or certificates come from the browser.
            status = self.gateway().send(payload, submission_id)
            receipt = TestReceipt(
                submission_id=submission_id,
                gateway_http_status=status,
                timestamp_utc=event["timestamp_utc"],
            )
            event = receipt.as_audit_event()
            return event
        except DeliveryUncertain:
            raise
        except SenderError:
            event["outcome"] = "rejected_or_unconfirmed"
            raise
        except (OSError, ValueError):
            event["outcome"] = "gateway_configuration_error"
            raise SenderError("Gateway setup failed") from None
        finally:
            with self.lock:
                self.events.appendleft(event)
                self.sending = False
            try:
                self.audit.append(
                    "gateway_completed", event["outcome"],
                    submission_id=submission_id, http_status=event["http_status"],
                )
            except AuditError as exc:
                raise DeliveryUncertain("Audit persistence failed; do not retry") from exc


class AdminServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, port: int = 8765, state: AdminState | None = None):
        self.state = AdminState() if state is None else state
        # Deliberately no parameter for public/non-loopback binding.
        super().__init__(("127.0.0.1", port), AdminHandler)

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class AdminHandler(BaseHTTPRequestHandler):
    server: AdminServer
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        # Suppress default access logs and prevent request data from leaking.
        pass

    def _headers(self, status: int, mime: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self'; base-uri 'none'; "
            "form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()

    def _body(self, status: int, payload: bytes, mime: str) -> None:
        self._headers(status, mime, len(payload))
        self.wfile.write(payload)

    def _json(self, status: int, data: dict | list) -> None:
        self._body(status, json.dumps(data, separators=(",", ":")).encode(), "application/json")

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def _valid_host(self) -> bool:
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def _authorized(self) -> bool:
        value = self.headers.get("X-Admin-Token", "")
        return self.server.state.authenticate(value)

    def _path(self) -> str:
        parsed = urlsplit(self.path)
        return parsed.path if not parsed.query and not parsed.fragment else ""

    def do_GET(self) -> None:
        if not self._valid_host():
            self._error(403, "Unrecognized local host")
            return
        path = self._path()
        if path.startswith("/api/"):
            try:
                authenticated = self._authorized()
            except AuditError:
                self._error(503, "Security audit unavailable; operation blocked")
                return
            if not authenticated:
                self._error(401, "Session unavailable; restart the local server to unlock")
                return
            if not self.server.state.use_authorized():
                self._error(403, "Restricted system-use notice must be acknowledged")
            elif path == "/api/status":
                self._json(200, self.server.state.status())
            elif path == "/api/readiness":
                self._json(200, readiness_register())
            elif path == "/api/activity":
                with self.server.state.lock:
                    events = list(self.server.state.events)
                self._json(200, {"events": events})
            else:
                self._error(404, "Unknown API route")
            return
        if path not in ASSETS:
            self._error(404, "Not found")
            return
        name, mime = ASSETS[path]
        try:
            payload = (ROOT / name).read_bytes()
        except OSError:
            self._error(500, "Admin interface assets are unavailable")
            return
        self._body(200, payload, mime)

    def do_POST(self) -> None:
        if not self._valid_host() or self.headers.get("Origin") != self.server.origin:
            self._error(403, "Origin not allowed")
            return
        try:
            authenticated = self._authorized()
        except AuditError:
            self._error(503, "Security audit unavailable; operation blocked")
            return
        if not authenticated:
            self._error(401, "Session unavailable; restart the local server to unlock")
            return
        if self.headers.get("Content-Type") != "application/json":
            self._error(415, "JSON content required")
            return
        path = self._path()
        if path not in ("/api/preview", "/api/send", "/api/session", "/api/logout"):
            self._error(404, "Unknown API route")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if not 0 < length <= 1024:
            self._error(413, "Invalid request size")
            return
        try:
            request = json.loads(self.rfile.read(length))
            if not isinstance(request, dict):
                raise SenderError("JSON object required")
            if path == "/api/session":
                if request != {"acknowledge": True}:
                    raise SenderError("Explicit system-use acknowledgment required")
                self.server.state.acknowledge_use()
                self._json(200, {"session": "acknowledged", "production_access": False})
            elif path == "/api/logout":
                if request:
                    raise SenderError("Logout requires an empty request")
                self.server.state.terminate_session()
                self._json(200, {"session": "terminated"})
            elif not self.server.state.use_authorized():
                self._error(403, "Restricted system-use notice must be acknowledged")
            elif path == "/api/preview":
                if set(request) != {"padding"}:
                    raise SenderError("Unexpected preview fields")
                data = synthetic_bytes(request["padding"])
                self.server.state.audit.append("synthetic_preview", "validated")
                self._json(200, {
                    "kind": "deterministic_synthetic_non_cji",
                    "bytes": len(data), "padding": request["padding"],
                    "network_activity": False,
                })
            else:
                receipt = self.server.state.send(request)
                self._json(200, receipt)
        except DeliveryUncertain:
            self._error(502, "Delivery unknown; do not retry without agency reconciliation")
        except AuditError:
            self._error(503, "Security audit unavailable; operation blocked; do not retry")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._error(400, "Invalid JSON document")
        except SenderError as exc:
            self._error(409 if "already used" in str(exc) else 400, str(exc))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="loopback port (default 8765)")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0..65535")
    with AdminServer(port=args.port) as server:
        # URL fragment is not sent in HTTP requests, Referer headers, or access logs.
        print(f"Open local admin UI: {server.origin}/#token={server.state.token}", flush=True)
        print("Local synthetic-only console. Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

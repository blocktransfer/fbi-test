#!/usr/bin/env python3
"""Fail-closed synthetic sender for testing an agency-approved HTTPS gateway.

NOT an FBI NGI connection, EBTS validator, or CJIS compliance certification.
No real fingerprint records, CJI, or PII may be used with this test sender.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import stat
import sys
from urllib.parse import urlsplit
from uuid import uuid4


TEST_MAGIC = b"SYNTHETIC-NON-CJI-TEST-V1\n"
MAX_TEST_BYTES = 50 * 1024 * 1024
AUTHORIZATION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{5,63}$")


class SenderError(Exception):
    """An input, authorization, or gateway configuration was rejected."""


class DeliveryUncertain(SenderError):
    """A request may have reached the gateway; do not retry automatically."""


@dataclass(frozen=True)
class TestReceipt:
    submission_id: str
    gateway_http_status: int
    timestamp_utc: str

    def as_audit_event(self) -> dict[str, str | int]:
        # No payloads, identifiers of individuals, raw hashes, paths, or replies.
        return {
            "event": "synthetic_gateway_submission",
            "submission_id": self.submission_id,
            "outcome": "http_2xx_not_fbi_acceptance",
            "http_status": self.gateway_http_status,
            "timestamp_utc": self.timestamp_utc,
        }


def read_synthetic_file(path: str | Path) -> bytes:
    """Read a private, regular file without following a symlink."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(os.fspath(path), flags)
    except OSError as exc:
        raise SenderError("Cannot open synthetic input securely") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SenderError("Input must be a regular, non-hardlinked file")
        if info.st_mode & 0o077:
            raise SenderError("Input permissions must be owner-only (chmod 600)")
        if not 0 < info.st_size <= MAX_TEST_BYTES:
            raise SenderError("Synthetic input size is outside the permitted range")
        with os.fdopen(os.dup(fd), "rb") as source:
            data = source.read(MAX_TEST_BYTES + 1)
        if len(data) > MAX_TEST_BYTES or not data.startswith(TEST_MAGIC):
            raise SenderError("Input is not a supported synthetic test payload")
        return data
    finally:
        os.close(fd)


class ApprovedTestGateway:
    """An HTTPS test gateway supplied by an authorized integrating agency.

    This interface is NOT known to be supported by FBI NGI/CJIS WAN.
    """

    def __init__(
        self, endpoint: str, approved_host: str, ca_bundle: str,
        client_cert: str, client_key: str, timeout: float = 20,
    ) -> None:
        parts = urlsplit(endpoint)
        if (
            parts.scheme != "https" or not parts.hostname
            or parts.hostname.lower() != approved_host.lower()
            or parts.port not in (None, 443)
            or parts.username or parts.password or parts.query or parts.fragment
            or not approved_host or timeout <= 0 or timeout > 60
        ):
            raise SenderError("Gateway must be approved HTTPS host on port 443")
        if not (ca_bundle and client_cert and client_key):
            raise SenderError("Client certificate, key, and CA bundle are required")
        self.host = parts.hostname
        self.path = parts.path or "/"
        self.timeout = timeout
        self.context = ssl.create_default_context(cafile=ca_bundle)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.check_hostname = True
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_cert_chain(client_cert, client_key)

    def send(self, payload: bytes, submission_id: str) -> int:
        # http.client does not consult environment proxies or follow redirects.
        connection = http.client.HTTPSConnection(
            self.host, port=443, context=self.context, timeout=self.timeout
        )
        try:
            connection.request(
                "POST", self.path, body=payload,
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-Test-Submission-ID": submission_id,
                    "User-Agent": "blocktransfer-fbi-test/0.1",
                },
            )
            response = connection.getresponse()
            status = response.status
            # Never read or log a potentially sensitive response body.
            if not 200 <= status < 300:
                raise SenderError(f"Test gateway returned HTTP {status}; delivery unconfirmed")
            return status
        except (OSError, TimeoutError, http.client.HTTPException) as exc:
            raise DeliveryUncertain("Gateway outcome unknown; do not retry automatically") from exc
        finally:
            connection.close()


def submit_synthetic(
    path: str | Path, gateway: ApprovedTestGateway, authorization_ref: str,
) -> TestReceipt:
    """Send once. HTTP success does not mean FBI/NGI transaction acceptance."""
    if not AUTHORIZATION_PATTERN.fullmatch(authorization_ref):
        raise SenderError("An agency test authorization reference is required")
    payload = read_synthetic_file(path)
    submission_id = str(uuid4())
    http_status = gateway.send(payload, submission_id)
    return TestReceipt(
        submission_id=submission_id,
        gateway_http_status=http_status,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect-test", help="check synthetic-only input")
    inspect.add_argument("file")
    send = commands.add_parser("send-test", help="POST synthetic input to approved test gateway")
    send.add_argument("file")
    send.add_argument("--endpoint", required=True)
    send.add_argument("--approved-host", required=True)
    send.add_argument("--ca-bundle", required=True)
    send.add_argument("--client-cert", required=True)
    send.add_argument("--client-key", required=True)
    send.add_argument("--authorization-ref", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect-test":
            data = read_synthetic_file(args.file)
            print(json.dumps({"status": "synthetic_test_only", "bytes": len(data)}))
        else:
            gateway = ApprovedTestGateway(
                args.endpoint, args.approved_host, args.ca_bundle,
                args.client_cert, args.client_key,
            )
            receipt = submit_synthetic(args.file, gateway, args.authorization_ref)
            print(json.dumps(receipt.as_audit_event(), sort_keys=True))
    except DeliveryUncertain:
        print("ERROR: gateway outcome unknown; do not retry automatically", file=sys.stderr)
        return 2
    except (SenderError, OSError, ssl.SSLError, ValueError):
        print("ERROR: synthetic input, authorization, or gateway configuration rejected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

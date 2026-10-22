"""Minimal protected synthetic admin audit journal (not a CJIS audit substitute).

Append-only, owner-readable journal with a SHA-256 corruption-detection chain.
The chain is NOT tamper-proof against a privileged local adversary: it has no
independent signing key or external trusted anchor. No real CJI is permitted.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
import threading
from uuid import UUID


class AuditError(Exception):
    """Fail-closed local audit storage or integrity failure."""


EVENTS = frozenset({
    "auth_failure", "auth_lockout", "session_expired",
    "session_acknowledged", "logout", "synthetic_preview",
    "gateway_started", "gateway_completed", "section_one_assessed",
    "recipient_check_requested", "recipient_check_saved", "recipient_deadline_planned",
    "channeler_check_requested", "channeler_check_saved", "channeler_planned",
    "fbi_oversight_check_requested", "fbi_oversight_check_saved",
    "fbi_oversight_planned",
})
OUTCOMES = frozenset({
    "denied", "locked", "expired", "acknowledged", "terminated",
    "validated", "started", "recorded", "http_2xx_not_fbi_acceptance",
    "unknown_delivery_do_not_retry", "rejected_or_unconfirmed",
    "gateway_configuration_error",
})


def canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class AuditJournal:
    def __init__(self, filename: str | Path):
        path = Path(filename).expanduser().absolute()
        parent = path.parent
        self._lock = threading.Lock()
        self._fd = -1
        self._sequence = 0
        self._digest = "0" * 64
        self._bytes = 0
        try:
            parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            parent_stat = parent.lstat()
            if not stat.S_ISDIR(parent_stat.st_mode) or parent_stat.st_mode & 0o077:
                raise AuditError("Audit directory must be private (0700), without symlinks")
            flags = os.O_RDWR | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
            self._fd = os.open(path, flags, 0o600)
            current = os.fstat(self._fd)
            if (not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
                    or current.st_mode & 0o077):
                raise AuditError("Audit file must be owner-only regular file (0600)")
            if hasattr(os, "geteuid") and current.st_uid != os.geteuid():
                raise AuditError("Audit file must belong to the current user")
            self._verify()
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            self.close()
            raise AuditError("Audit journal cannot be safely opened or verified") from exc
        except AuditError:
            self.close()
            raise

    def _verify(self) -> None:
        os.lseek(self._fd, 0, os.SEEK_SET)
        with os.fdopen(os.dup(self._fd), "rb") as handle:
            for raw in handle:
                if len(raw) > 8192 or not raw.endswith(b"\n"):
                    raise AuditError("Audit journal contains an incomplete or oversized line")
                try:
                    record = json.loads(raw)
                except (ValueError, UnicodeError) as exc:
                    raise AuditError("Audit journal contains invalid JSON") from exc
                if not isinstance(record, dict):
                    raise AuditError("Invalid audit record")
                supplied_digest = record.pop("digest", None)
                if (record.get("sequence") != self._sequence + 1
                        or record.get("previous_digest") != self._digest):
                    raise AuditError("Audit sequence or hash chain mismatch")
                actual_digest = hashlib.sha256(canonical(record)).hexdigest()
                if not isinstance(supplied_digest, str) or not hmac.compare_digest(
                    supplied_digest, actual_digest
                ):
                    raise AuditError("Audit record digest mismatch")
                self._sequence += 1
                self._digest = supplied_digest
        self._bytes = os.fstat(self._fd).st_size

    def append(
        self, event: str, outcome: str, *, submission_id: str | None = None,
        http_status: int | None = None,
    ) -> None:
        if event not in EVENTS or outcome not in OUTCOMES:
            raise AuditError("Unexpected audit event type or outcome")
        if submission_id is not None:
            try:
                submission_id = str(UUID(submission_id))
            except (ValueError, TypeError) as exc:
                raise AuditError("Invalid synthetic submission identifier") from exc
        if http_status is not None and (type(http_status) is not int or not 100 <= http_status <= 599):
            raise AuditError("Invalid HTTP status for audit record")
        with self._lock:
            try:
                if os.fstat(self._fd).st_size != self._bytes:
                    raise AuditError("Audit journal changed outside application")
                record = {
                    "sequence": self._sequence + 1,
                    "previous_digest": self._digest,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event": event,
                    "outcome": outcome,
                    # Current shared-token design cannot uniquely identify human operators.
                    "actor": "local_shared_token",
                    "source": "loopback_admin",
                }
                if submission_id is not None:
                    record["submission_id"] = submission_id
                if http_status is not None:
                    record["http_status"] = http_status
                digest = hashlib.sha256(canonical(record)).hexdigest()
                line = canonical({**record, "digest": digest}) + b"\n"
                pos = 0
                while pos < len(line):
                    written = os.write(self._fd, line[pos:])
                    if written < 1:
                        raise AuditError("Audit journal write incomplete")
                    pos += written
                os.fsync(self._fd)
                self._bytes += len(line)
                self._sequence += 1
                self._digest = digest
            except OSError as exc:
                raise AuditError("Cannot durably write audit journal") from exc

    def close(self) -> None:
        if self._fd >= 0:
            os.close(self._fd)
            self._fd = -1

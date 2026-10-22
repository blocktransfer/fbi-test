"""Private local checklist metadata for Compact Council §2 (not approval evidence).

Only checklist IDs, booleans, generated timestamps and restricted document
reference codes are stored. No contacts, legal documents, incidents or CJI.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import stat
import threading

from authorized_recipient import SPEC


class ChecklistError(ValueError):
    pass


REFERENCE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{5,63}$")
MAX_SIZE = 65536


def _private_parent(path: Path) -> None:
    parent = path.parent
    parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    info = parent.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077
            or (hasattr(os, "geteuid") and info.st_uid != os.geteuid())):
        raise ChecklistError("Checklist directory must be private, owner-controlled (0700)")


class RecipientChecklist:
    """Single-process, atomic replacement of nonidentifying operator records."""

    def __init__(self, filename: str | Path):
        self.path = Path(filename).expanduser().absolute()
        self.lock = threading.Lock()
        _private_parent(self.path)
        self._load()

    def _load(self) -> dict:
        try:
            fd = os.open(self.path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        except FileNotFoundError:
            return {"schema": 1, "checks": {}}
        except OSError as exc:
            raise ChecklistError("Checklist file cannot be securely read") from exc
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                    or info.st_mode & 0o077 or info.st_size > MAX_SIZE
                    or (hasattr(os, "geteuid") and info.st_uid != os.geteuid())):
                raise ChecklistError("Checklist file must be a small owner-only regular file (0600)")
            with os.fdopen(os.dup(fd), "rb") as stream:
                blob = stream.read(MAX_SIZE + 1)
            doc = json.loads(blob)
            if type(doc) is not dict or set(doc) != {"schema", "checks"} or doc["schema"] != 1:
                raise ChecklistError("Unexpected checklist schema")
            if type(doc["checks"]) is not dict or set(doc["checks"]) - SPEC.keys():
                raise ChecklistError("Unknown checklist entries")
            for entry in doc["checks"].values():
                if (type(entry) is not dict or set(entry) != {"reported", "evidence_ref", "recorded_at"}
                        or type(entry["reported"]) is not bool
                        or (entry["reported"] and
                            (type(entry["evidence_ref"]) is not str or
                             not REFERENCE.fullmatch(entry["evidence_ref"])))
                        or (not entry["reported"] and entry["evidence_ref"] is not None)
                        or type(entry["recorded_at"]) is not str
                        or len(entry["recorded_at"]) > 40):
                    raise ChecklistError("Invalid recorded checklist metadata")
            return doc
        except (OSError, ValueError, UnicodeError) as exc:
            raise ChecklistError("Cannot safely parse checklist state") from exc
        finally:
            os.close(fd)

    def summary(self) -> dict:
        with self.lock:
            doc = self._load()
        return {
            "checks": doc["checks"],
            "reported_count": sum(bool(item["reported"]) for item in doc["checks"].values()),
            "independently_verified": False,
            "FBI_approval_verified": False,
            "production_ready": False,
            "notes": "Operator-reported document references only; no approval authenticity verified",
        }

    def update(self, data: dict, audit) -> dict:
        if type(data) is not dict or set(data) != {"id", "reported", "evidence_ref"}:
            raise ChecklistError("Expected checklist ID, reported flag and evidence reference")
        key, reported, reference = data["id"], data["reported"], data["evidence_ref"]
        if type(key) is not str or key not in SPEC:
            raise ChecklistError("Unknown Section 2 checklist ID")
        if type(reported) is not bool:
            raise ChecklistError("Reported state must be true or false")
        if reported:
            if type(reference) is not str or not REFERENCE.fullmatch(reference):
                raise ChecklistError("Use a nonidentifying evidence code (6–64 uppercase letters/digits)")
        elif reference is not None:
            raise ChecklistError("Clear evidence reference when removing a report")
        with self.lock:
            _private_parent(self.path)
            doc = self._load()
            doc["checks"][key] = {
                "reported": reported,
                "evidence_ref": reference,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
            serialized = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("ascii")
            if len(serialized) > MAX_SIZE:
                raise ChecklistError("Checklist capacity exceeded")
            # Audited attempt must exist before applying a state transition.
            audit.append("recipient_check_requested", "started")
            temp = self.path.with_name("." + self.path.name + "." + secrets.token_hex(10) + ".tmp")
            fd = -1
            try:
                fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, "wb", closefd=True) as stream:
                    fd = -1
                    stream.write(serialized)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp, self.path)
                dirfd = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(dirfd)
                finally:
                    os.close(dirfd)
            except OSError as exc:
                raise ChecklistError("Could not persist checklist securely") from exc
            finally:
                if fd >= 0:
                    os.close(fd)
                if temp.exists():
                    temp.unlink()
            audit.append("recipient_check_saved", "recorded")
            return {
                "id": key, "reported": reported,
                "recorded_at": doc["checks"][key]["recorded_at"],
                "independently_verified": False,
                "production_ready": False,
            }

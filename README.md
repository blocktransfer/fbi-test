# BlockTransfer FBI fingerprint sender lab

**Status: synthetic-only test sender; not connected to FBI NGI.**

This repository is an incremental engineering foundation for a future *authorized*
fingerprint submission sender. It is **not** a channeler, a certified FBI
connection, an EBTS encoder/validator, or evidence of CJIS compliance.

The FBI [CJIS Security Policy v6.1 (June 25, 2026)](https://le.fbi.gov/file-repository/cjis_security_policy_v6-1_20260625.pdf/view)
governs the security program. The separate
[FBI EBTS v11.4](https://fbibiospecs.fbi.gov/file-repository/ebts/ebts-v11-4.pdf/view)
specifies biometric transaction structures; it does not make this prototype
an authorized transmission path. The FBI describes electronic biometric
submission through a **CJIS WAN** connection available to authorized
agencies, rather than a public HTTP endpoint.

## Implemented

- `fbi_sender.py inspect-test`: locally inspect a private, explicitly
  marked synthetic file without any network action.
- `fbi_sender.py send-test`: **one** POST of a synthetic payload to an
  agency-provided **HTTPS test gateway**, with CA validation, server hostname
  verification, client certificate, and client key.
- Exact gateway hostname allowlisting; rejects HTTP, non-443 ports,
  URL userinfo/query/fragment, and HTTP redirects. No automatic retries.
- Input checks for owner-only file permissions, regular files, hardlinks,
  symlinks (on supported POSIX platforms), and a 50 MiB size ceiling.
- A content-free success receipt with a random test submission ID, time,
  and HTTP status. HTTP 2xx **does not** establish FBI acceptance.
- Offline unit tests and a GitHub Actions workflow. No live biometric or
  personally identifiable information is included in repository fixtures.

## Quick start (synthetic data only)

Requires Python 3.12+; no third-party Python dependencies.

Create a tiny synthetic payload with restrictive file permissions:

```sh
python - <<'PY'
import os
p = os.open("synthetic.bin", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
try:
    os.write(p, b"SYNTHETIC-NON-CJI-TEST-V1\n" + b"\x00\x01")
finally:
    os.close(p)
PY
python fbi_sender.py inspect-test synthetic.bin
python -m unittest discover -s tests -v
```

To exercise a real **agency-approved test gateway** only after receiving
its exact endpoint, CA trust material, client certificate, client key, and
written permission to test this transport:

```sh
python fbi_sender.py send-test synthetic.bin \
  --endpoint https://test-gateway.example/ingest \
  --approved-host test-gateway.example \
  --ca-bundle /secure/path/ca.pem \
  --client-cert /secure/path/client.pem \
  --client-key /secure/path/client.key \
  --authorization-ref agency-test-123
```

**All values above are placeholders**. `--authorization-ref` only verifies
a reference's syntax; the software cannot verify the authenticity of the
agency's authorization. Do not use the placeholder hostname as an actual
destination. The sender does not provide any FBI/CJIS WAN adapter.

The synthetic magic header is **not an EBTS record**. Only the fixed header,
two prescribed test bytes, and optional zero padding are accepted; arbitrary
trailing bytes are rejected. Never use real fingerprints, demographic
information, CHRI, CJI, or other PII.
Never put real data, keys, or agreements into issues, pull requests, logs,
CI jobs, or this public repository.

## How the security policy maps to this foundation

| Policy reference | Initial implementation / outstanding work |
| --- | --- |
| `5.1.1; CA-3 (information exchange agreements) | Written agency agreement and authorized interface **required externally** before any real exchange. |
| SC-8(1), SC-12, SC-13 (transmission and cryptography) | Test adapter uses HTTPS with server verification and client TLS certificates; **approved FIPS-validated cryptography and network controls remain unverified**. |
| AC-3, AC-4, IA-2 (access/identification) | Sender restricts test inputs and gateway destination; organizational identity, access, and MFA controls remain agency responsibilities. |
| AU-2, AU-3, AU-9, AU-11 (logging/security/retention) | Minimal receipt avoids payload and response contents; durable access-controlled, tamper-evident audit records with retention **not yet built**. |
| SC-28 (CJI at rest) | Sender creates no stored payloads; caller's source storage, platform encryption, and environment still need approved safeguards. |
| SI-12 (information management/retention) | No actual CJI may be processed in this prototype. Retention/disposal policies for future production require agency approval. |

## Integration gates before real fingerprint submissions

1. Confirm organizational legal authority, originating-agency identifier
   (ORI), purpose/transaction type, data routing, applicable agreements,
   agency/CSA contact, and an approved CJIS WAN or delegated interface.
2. Implement and validate the correct **EBTS v11.4** transaction types,
   fields, fingerprint image encodings and message acknowledgments against
   FBI/agency-provided certification fixtures.
3. Obtain agency approval for authentication, network protection, FIPS
   cryptographic boundary, system hardening, personnel screening, audit
   retention, incident reporting, and restricted CJI storage/processing.
4. Implement durable idempotency, reconciliation of uncertain sends,
   acknowledgments and response handling before permitting any production
   transactions. Network failures must not trigger blind resubmission.
5. Complete agency testing and onboarding. A successful HTTPS response from
   a test gateway is **not** NGI submission acceptance.

This project deliberately ships neither a production endpoint nor a way
to bypass these integration gates.

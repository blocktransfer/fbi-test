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

## Compact Council Section 1 domain support

Section 1 (PDF pp. 3–7) of the **November 29, 2023 Security and
Management Control Outsourcing Standard for Channeling** defines 25 legal,
security and workflow terms. These are *definitions*, not 25 separately
grantable permissions or services. The application implements each term in a
read-only, source-page-referenced glossary and applies enforceable distinctions
to a dry-run assessment.

- **Policy catalog:** ``1.01–1.25 via `GET /api/section-one` (admin access and
  system-use acknowledgment required).
- **Nonidentifying scenario assessment:** `POST /api/section-one/assess`
  accepts only enumerated roles and purposes plus boolean flags. It rejects
  names, fingerprint bytes, raw CHRI, applicant records, unknown fields, and
  non-boolean values. No assessment inputs are retained; only the fact that
  an assessment occurred is entered in the local audit journal.
- **Roles and authority (``1.02–1.07, 1.11, 1.17):** identifies contradictory
  or missing self-reported prerequisites. ARPOC cannot be outsourced;
  State Chief Administrator is a repository role; Channeler selection,
  agreements, and lawful authority must be established independently.
- **Data distinction (``1.08, 1.19):** fingerprint identification data alone
  does not automatically constitute CHRI but can still be PII. Classification
  is based on declared flags and is not a certified determination.
- **Identification (`1.22):** name-only comparison never establishes positive
  identification. Qualifying ten-rolled/ten-flat capture is not itself proof
  of a successful fingerprint comparison.
- **Restricted actions (``1.01, 1.14–1.15, 1.23–1.24):** no direct III access,
  no real NGI fingerprint submission/CHRI dissemination, no Rap Back messaging,
  and no representation that media has been sanitized.
- **Governance and event definitions (``1.09–1.10, 1.12–1.13, 1.16, 1.18,
  1.20–1.21, 1.25):** preserved as source-referenced terms; determining
  organizational compliance and incident handling requires actual evidence
  and authorized human decision-makers.

Use the dashboard's **Section 1 definitions** navigation item to browse all
25 terms, filter them and run the nonidentifying role/data worksheet. Any
checkbox reporting a written agreement, appointment, or FBI selection is
**not evidence** that the approval exists. The model *always* reports
`production_ready=false` and never enables actual submissions.

See [`docs/section-1-implementation.md`](docs/section-1-implementation.md)
for each definition's implementation boundary.

## Section 2 Authorized Recipient workflows

The 2023 Compact Council Channeling Outsourcing Standard, Section 2
(``2.01–2.14, PDF pp. 8–10), governs **Authorized Recipient**
responsibilities. The dashboard's **Section 2 recipient duties** view
supports 31 documentary checklist items with source citations, eight
deadline-event types, and nine blank correspondence templates.

Checklist state is saved in an owner-only local file at
`~/.blocktransfer-fbi-test/recipient-checklist.json`. Override the path
using `FBI_TEST_RECIPIENT_PATH`. Record only nonidentifying evidence
reference codes such as `CONTRACT-2026-001`; do not enter contracts,
personnel contacts, applicant details, fingerprints, incidents, PII or CHRI.
Files require 0600 permissions and the parent directory 0700. Mutations
require an audit journal write. No checkbox proves independent approval.

Deadlines include:
- ARPOC change (`2.06) and ARSO appointment/change (`2.07): **30 days**.
- Policy updates (`2.03): contract, renewal, or 60-calendar-day update
  notification window, whichever occurs sooner.
- PII breaches (`2.08): notification within **one hour** of discovery.
- Other violations or contract termination (`2.08): **four hours**.
- Written breach/violation report (`2.08): **five calendar days after
  initial notification**, not five days after discovery.
- Early voluntary termination (`2.14): written notice required but no
  numeric deadline is given in that subsection.

The API supports authenticated `GET /api/recipient`, `POST
/api/recipient/check`, `POST /api/recipient/deadlines` and `GET
/api/recipient/templates`. These never authorize CHRI exchange, send
notices, verify authority, or reinstate a suspended operation.

See [`docs/section-2-implementation.md`](docs/section-2-implementation.md)
for the clause-by-clause implementation matrix and external obligations.

## Section 3 Channeler responsibilities (synthetic-only)

The Compact Council's November 29, 2023 Channeling Outsourcing Standard,
**Section 3 (``3.01–3.25; printed pp. 3–7)**, sets security and operating
duties for an **FBI-selected Channeler**. The dashboard now has a
**Section 3 channeler duties** screen with all 25 clauses and 39
evidence-reference checkpoints. It is strictly separate from the Section 2
Authorized Recipient checklist.

Key functions:
- **Compliance and agency approvals:** document status codes for the
  physical/personnel/IT Security Program (including FBI written approval),
  current network diagram, **FBI preapproval of changes**, approved
  contingency plan, access logs and audit/inspection readiness.
- **Deadlines:** source-defined 60-day policy updates; one-hour PII breach
  notices; four-hour other incident/termination notices; written Channeler
  incident report within **five calendar days of discovery**; 24-hour
  employee access-record updates AND FBI notices.
- **Hypothetical CHRI custody (`3.12):** computes destruction immediately
  at confirmed recipient receipt or by day 30, whichever occurs first.
  This is a calculator, **not a CHRI data store or secure erasure system**.
- **Training (`3.19):** preassignment training, annual refresher and
  FBI certification anniversary schedule; separately represents agreements
  assigning the training duty to the Recipient.
- **Rap Back (``3.22–3.25):** yearly messaging milestone with validation
  explicitly reserved to the Recipient. Never enables real subscriptions,
  treats unverified FBI test approval as valid, or stores applicant PII.
- **Synthetic record checks (``3.13, 3.24):** validates a built-in dummy
  dissemination record containing the five required log fields and minimum
  one-year retention period, and validates synthetic TCN/Subscription-ID
  linkage with no additional applicant data. No real records are retained.
- **Twelve blank policy/correspondence templates** for secure completion
  outside this system. No report, notice or fingerprint information is sent.

Channeler metadata are kept in an owner-only local file
`~/.blocktransfer-fbi-test/channeler-checklist.json` (override with
`FBI_TEST_CHANNELER_PATH`); enter only restricted alphanumeric document
reference codes, never employee identities, actual CHRI, transaction
numbers, agreements or incident details. The audited local checklist
cannot verify documentary authenticity or FBI approval. All actual
CHRI intake, direct NGI access, EBTS exchange, Rap Back operations,
personnel access, record sanitization and official notification delivery
remain disabled or outside the prototype.

See [`docs/section-3-implementation.md`](docs/section-3-implementation.md)
for each clause, source page, implemented function and external dependency.

## Local admin frontend

Start the **local-only** administrative dashboard from the repository root:

```sh
python admin_ui.py
```

The server binds **only** to `127.0.0.1:8765`. It prints a unique URL such
as `http://127.0.0.1:8765/#token=...` in the terminal. Open that entire URL
in your browser. Its one-time session token is held in the tab and is removed
from the address bar after loading. The API requires this token and rejects
cross-origin or non-loopback-host requests. Closing the server ends the
session; restart it to issue a new token.

The responsive console provides:

- **Overview:** isolated test-only status and session counters.
- **Test console:** locally validates a deterministic non-CJI sample, or
  sends exactly one sample to an *authorized* test gateway when configured.
  Sending requires a typed authorization reference and explicit confirmation.
- **Readiness & controls:** source-referenced CJIS and Compact Council
  obligations, including technical, Authorized Recipient, Channeler, and FBI
  responsibilities, without making unsupported compliance claims.
- **Incident deadlines:** computes the 1-hour/4-hour and five-calendar-day
  notification milestones from CJIS IR-6 and Outsourcing §§2.08/3.15.
  No incident description is collected or saved, and **no notice is sent**.
  For Authorized Recipients, the five-day written-report clock is measured
  from initial notification; for Channelers it is measured from discovery.
- **Activity:** metadata-only recent receipts stored in RAM, plus an owner-only
  local SHA-256 hash-chained, fsynced audit journal on disk for security and
  gateway events. The hash chain detects local corruption but is **not**
  tamper-proof without independent protected anchors; shared tokens cannot
  identify individual administrators. Audit retention, backup, oversight, and
  operational monitoring remain external obligations. HTTP success is never
  FBI acceptance.

The UI never accepts or uploads fingerprint files, CJI, PII, arbitrary data
buffers, certificates, or private keys. It **cannot** submit fingerprints
to the FBI.

### Optional authorized test-gateway setup

The dashboard's transmission button remains disabled unless the **server**
is launched with all of the following environment variables:

```sh
export FBI_TEST_ENDPOINT='https://approved-test.example/ingest'
export FBI_TEST_APPROVED_HOST='approved-test.example'
export FBI_TEST_CA_BUNDLE='/secure/path/agency-ca.pem'
export FBI_TEST_CLIENT_CERT='/secure/path/test-client.pem'
export FBI_TEST_CLIENT_KEY='/secure/path/test-client.key'
export FBI_TEST_AUTHORIZATION_REF='agency-test-123'
export FBI_TEST_ENABLE_GATEWAY='synthetic-only'
python admin_ui.py
```

The host, endpoint, and certificate paths above are **placeholders** and
must be replaced only after receiving an approved agency test interface
and written authorization to use it. Environment values remain in the local
process; don't paste credential contents into browser inputs or GitHub.

The local typed authorization reference must match the server setting and
the gateway must be explicitly enabled as `synthetic-only`; neither test
reference nor the enablement flag verifies independent agency authorization.

An owner-only audit log is created by default under
`~/.blocktransfer-fbi-test/audit.jsonl`. Override its location only with a
secure local path using `FBI_TEST_AUDIT_PATH`; the destination directory
must have 0700 permissions and the file 0600. The audit journal is
fail-closed, contains no payloads, and is not a substitute for agency-managed
archiving, one-year record retention, monitored review, protected backups,
or external integrity anchoring (CJIS AU-2/3/9/11; Outsourcing 3.13).

All sends require TLS hostname verification and the supplied client
certificate. A request ID prevents repeated identical submissions within
the running process. In case of an uncertain gateway outcome, **do not
retry automatically or manually until the agency reconciles delivery**.
There is no production transmission mode.

Run the frontend and sender tests locally:

```sh
python -m unittest discover -s tests -v
node --check web/app.js
```

The dashboard uses Python's standard library and plain HTML, CSS, and JS,
with no required application packages or third-party frontend dependencies.

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
| 5.1.1; CA-3 (information exchange agreements) | Written agency agreement and authorized interface **required externally** before any real exchange. |
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

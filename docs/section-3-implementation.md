# Section 3 — Channeler implementation matrix

**Primary source:** National Crime Prevention and Privacy Compact Council,
*Security and Management Control Outsourcing Standard for Channeling*,
last updated November 29, 2023, **Section 3 (``3.01–3.25, printed pages 3–7)**.

The Standard places these obligations on a **Channeler**. The repository
still contains only a **synthetic-only local sender prototype**, NOT an
FBI-selected or approved Channeler service. A reported document-reference
code or success from a simulated test is never evidence that the FBI
approved any system, agreement, Security Program, network, contingency plan
or Rap Back service.

| Section / printed page | Requirement | Application functionality | Outstanding external action |
| --- | --- | --- | --- |
| 3.01 / 3 | Follow applicable laws, CJISSECPOL and Council/AG rules | Legal-policy evidence checkpoint and reference template | Actual legal/policy compliance |
| 3.02 / 3 | Supply current approved CHRI agreement portions on official request | Agreement availability checkpoint/template | Authorized contract repository and disclosure |
| 3.03 / 3 | Written early voluntary termination notice to Compact Officer/Chief Administrator and FBI | Event planner with no invented numeric deadline; template | Actual formal written notices |
| 3.04 / 3 | Notify Recipient of updated standards/policy; make versions available within 60 calendar days unless directed otherwise | 60-day event calculator, version checkpoints/template | Distribution of actual current documents |
| 3.05 / 3 | Physical, personnel, IT Security Program; selection/supervision/separation; **FBI written approval** | Four checkpoints, Security Program outline | Implemented program and written FBI approval |
| 3.06 / 3–4 | Program must follow incorporated and successor CJISSECPOL versions | Version tracking checkpoint | Actual controls and ongoing updates |
| 3.07 / 4 | Program subject to Recipient/Compact Officer/FBI review and remedial updates | Remediation checkpoint and program template | Independent review, remediation, verification |
| 3.08 / 4 | Current network diagram; FBI approval **before** changing diagram/configuration | Three checkpoints, pre-change template | Valid configuration and written FBI approval **before** implementation |
| 3.09 / 4 | FBI-approved documented IT contingency plan | Contingency checklist/template | Actual plan, testing and written FBI approval |
| 3.10 / 4 | All Channeler access attempts recorded and routinely reviewed by FBI | Audit-design checkpoint, prototype local access audit | Comprehensive production audit system and actual FBI review |
| 3.11 / 4 | Announced/unannounced Recipient/FBI inspections and configuration reviews | Inspection-readiness checkpoint/template | Facility access, inspection and network inspection |
| 3.12 / 4 | CHRI retained only until confirmed Recipient receipt or 30 days, whichever sooner; dissemination method/timing in contract | Hypothetical deletion deadline calculation and custody template | **Actual** approved CHRI storage, acknowledgment, destruction, sanitization and evidence |
| 3.13 / 5 | Dissemination log **at least one year**; Recipient FBI-assigned OCA/ORI, TCN, date, statutory authority, means | Synthetic five-field validator, one-year date calculation and log template | Actual confidential dissemination log and secure one-year retention |
| 3.14 / 5 | Protect CHRI/equipment; NGI checks and responses for authorized official purposes only | Access restriction checkpoint; sender accepts no CHRI | Approved end-to-end purpose limitation and security |
| 3.15 / 5 | Notify Recipient, Compact Officer/Chief Administrator and FBI within 1 hour of PII breach or 4 hours of other violation/termination; written security violation report **within 5 days of discovery** with required details | Discovery-based planner and report template | Actual detection, three recipient notifications and protected written report |
| 3.16 / 5 | If Channeler takes fingerprints, tell individuals they may report PII breaches directly to FBI; safeguard PII | Blank individual notice and PII checkpoint | Official notice delivery and PII processing safeguards |
| 3.17 / 5 | On Recipient CHRI exchange termination, delete or return CHRI records/media as policy and agreement specify | Event checklist and custody/disposition template | Actual compliant return/destruction |
| 3.18 / 6 | Update CHRI-access employee records **and** notify FBI within 24 hours of changes | 24-hour planner, two checkpoints, access/notice template | Actual employee roster and timely FBI notice |
| 3.19 / 6 | Unless Recipient retains duty under contract: train before assignment, annual refresher, yearly written FBI certification by contract anniversary | Training planner and annual-certification template | Actual personnel training, certification and submission |
| 3.20 / 6 | Written discipline policy for employees violating agreement security | Discipline checkpoint and template | Human resources policy and enforcement |
| 3.21 / 6 | Upon knowledge of violation, suspend employee from CHRI-access assignments | Immediate suspension checkpoint/template; prototype grants no CHRI access | Actual immediate personnel access revocation |
| 3.22 / 6 | EBTS conformance; required Rap Back messages/results and subscription handling | EBTS/Rap Back checkpoints/template; live exchange disabled | Implementation, transport and approved EBTS/Rap Back testing |
| 3.23 / 6 | Annual Rap Back validation **messaging**; substantive validation reserved to Recipient | Yearly message scheduler; never marks Recipient validation complete | Actual message exchange; Recipient performs validation |
| 3.24 / 7 | Rap Back links contain **only TCN and Rap Back Subscription Identifier**, no applicant PII | Strict two-field synthetic schema validator; no storage | Approved secure production subscription reference store |
| 3.25 / 7 | FBI testing and approval before Rap Back implementation; comply with designated privacy risk mitigation/validation strategy | Separate approval and mitigation checkpoints/template | Actual successful FBI testing, written approval and policy implementation |

## Implemented interfaces

Authenticated admin API (all require token and system-use acknowledgment):

- `GET /api/channeler`: 25 source clauses plus 39 evidence checkpoints.
- `POST /api/channeler/check`: owner-only, audited operator-reported
  evidence reference. Only allowlisted Section 3 checkpoint IDs and
  restricted reference codes; no applicant or employee details.
- `POST /api/channeler/deadlines`: source-defined incident, policy,
  personnel and termination deadlines.
- `POST /api/channeler/retention`: hypothetical earliest CHRI
  destruction date from receipt, acknowledgment and inspection times.
- `POST /api/channeler/training`: hypothetical annual and preassignment
  milestones with Recipient-retained-duty option.
- `POST /api/channeler/rapback`: hypothetical yearly message schedule;
  cannot validate Recipient subscriptions or enable service.
- `POST /api/channeler/dissemination`: accepts only dummy
  `TEST-OCA/ORI`, `TEST-TCN` and `TEST-AUTH` references plus date/means.
  Checks `3.13 shape and **one-year minimum** period but saves no record.
- `POST /api/channeler/rapback-reference`: checks dummy TCN and
  subscription ID only; extra applicant identifiers are rejected.
- `GET /api/channeler/templates`: 12 blank plans, notices, and forms
  for completion and authorized delivery outside the test system.

All output explicitly denies external verification, live service,
notifications, CHRI custody, biometric submission, real subscription
activation and actual secure deletion. The `3.15 five-day Channeler report
runs **from discovery**; the `2.08 Authorized Recipient report runs
**from initial notification**.

## Remaining production engineering and organizational requirements

The synthetic sender does **not** implement production CHRI retention
and sanitization, a real dissemination ledger, EBTS fingerprint
transactions, real Rap Back message delivery, FBI-approved network
changes, live employee access controls, physical facility audits,
annual security training records, incident-notification dispatch,
actual FBI audit access or actual written FBI approvals.

A local token and hash-chained audit log are insufficient to assert
CJISSECPOL production compliance. Real employee identities, CHRI, PII,
Rap Back identifiers, OCA/ORI or TCN must not be placed into this
repository, its local test forms, CI fixtures or GitHub issues.

Operational and legal verification with the actual Authorized Recipient,
Compact Officer/Chief Administrator, FBI CJIS contacts and qualified
security team is required before any production fingerprint channeling.

# Section 2 Authorized Recipient implementation matrix

**Source:** National Crime Prevention and Privacy Compact Council,
*Security and Management Control Outsourcing Standard for Channeling*,
approved November 29, 2023, Section 2 (``2.01–2.14), PDF pp. 8–10.
These duties belong to an **Authorized Recipient**. Software operation
does not make an entity an Authorized Recipient or FBI-approved Channeler.

| Section | Source-derived obligation or option | Implemented | Still requires external action |
| --- | --- | --- | --- |
| 2.01 (PDF 8) | Obtain prior written permission; supply ARPOC, authority, populations; appropriate state/FBI Compact Officer route | Five checklist items, blank permission request | Actual legal authority, named personnel and written permission |
| 2.02 (PDF 8) | Execute contract before Channeler CHRI access; incorporate policies; supply CHRI-related portions on request | Agreement checklists and template | Valid signatures, contract and disclosure |
| 2.03 (PDF 8) | Use current policies at contract, renewal or within 60-day notified update period, whichever sooner | Policy-update deadline calculator and version worksheet | Executed amendment and version review |
| 2.04(a)–(f) (PDF 8–9) | Specify access, purpose limitation, dissemination restriction, confidentiality, FBI audits/sanctions, termination conditions | Six individual checklist items and contract clauses | Actual enforceable contractual controls |
| 2.05 (PDF 9) | Understand Channeler's CHRI processing and transmission | Process/dataflow checkpoint and contract template | Review of actual architecture and flow |
| 2.06 (PDF 9) | Notify changes to ARPOC within 30 calendar days | Deadline calculator, change notice and checklist | Actual notice and proof of delivery |
| 2.07 (PDF 9) | Appoint ARSO; notify initial appointment within 30 days of approval and subsequent changes within 30 days | Three checkpoints, deadline calculator and notice | Actual appointment, contact and notice |
| 2.08 (PDF 9) | PII breach notice within 1 hour; other violation or termination within 4 hours; breach/violation written report within 5 days of initial notification | Timelines, report template listing OCA, Channeler, corrective steps, occurrence time, intent and count | Incident response, sending the two notices and completed report |
| 2.09 (PDF 10) | Recipient *may* terminate for Channeler security violation, failure to report, or refusal/inability to resolve | Optional contract-termination rights checkpoint | Actual termination decision |
| 2.10 (PDF 10) | Unreported violation can lead to CHRI suspension; reinstatement after satisfactory written assurances | Suspension/reinstatement checkpoints and assurance template | Official authority determination and assurances to Compact Council Chair or Attorney General |
| 2.11 (PDF 10) | Make facilities available for announced and unannounced state/FBI audits | Facility-inspection checkpoint and audit worksheet | Actual facility access and inspection |
| 2.12 (PDF 10) | Recipient *may* audit Channeler | Optional audit checkpoint and worksheet | Conduct of audit if chosen |
| 2.13 (PDF 10) | Recipient *may* impose stricter site security | Optional site-control checkpoint and worksheet | Contract and physical deployment |
| 2.14 (PDF 10) | Written notice of early voluntary termination to Compact Officer/Chief Administrator and FBI | Notice template and conditional checklist; no invented deadline | Actual written notice and proper termination |

## APIs and record handling

- `GET /api/recipient`: all 31 checklists and separately stored
  operator-reported nonidentifying reference codes.
- `POST /api/recipient/check`: strict payload consisting of
  `id`, Boolean `reported`, and `evidence_ref` (uppercase safe code
  when reported, null when cleared).
- `POST /api/recipient/deadlines`: accepts event categories and UTC
  timestamps; calculates 30/60-day, one/four-hour and five-day deadlines,
  but does not send notifications or persist inputs.
- `GET /api/recipient/templates`: nine blank copy-only letters,
  agreement outlines, reports and review worksheets.

All endpoints require existing local token authentication and AC-8-style
acknowledgment. The evidence file is stored with owner-only permissions
and is written atomically. Audit journal events precede state mutations.
Checklists are not independently verified and do not unlock FBI/NGI
access. The current audit chain also lacks external integrity anchoring.

## Important limitations

The test tool cannot establish specific national fingerprint-check
authority, verify the Compact Officer's written permission, collect legally
required ARPOC or ARSO personal details in a CJIS-approved system, send
required correspondence, perform physical facility inspections, enforce
actual agreements, conduct real audits or restore suspended CHRI access.

Section 2.08's five-day **Authorized Recipient** written-report clock
begins with **initial notification**. The separate Channeler report
language in `3.15 uses discovery. These must not be conflated.

Use organizationally approved methods for documents containing personal
data, CHRI, legal claims or incident details. Nothing on this screen
constitutes FBI approval, production readiness or CJIS certification.

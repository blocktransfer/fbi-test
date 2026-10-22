# Section 1: implementation boundary matrix

**Primary source:** National Crime Prevention and Privacy Compact Council,
*Security and Management Control Outsourcing Standard for Channeling*,
approved November 29, 2023, Section 1 (``1.01–1.25), PDF pages 3–7.

This matrix distinguishes (A) implemented synthetic-only, definition-based
checks, (B) explanatory domain vocabulary, and (C) facts that **cannot**
be established by the software without documented approvals and audits.
Every one of the 25 definitions appears in `channeling_definitions.py` and
the admin UI glossary.

| Section | Defined concept | Implemented treatment | What is not established |
| --- | --- | --- | --- |
| 1.01 | Access to CHRI | Direct III access never enabled | Exceptions for contracted or otherwise authorized access |
| 1.02 | Authorized Recipient | Authority basis and recipient-kind coherence check | Specific legal authority; Attorney General approval |
| 1.03 | ARPOC | Flags an outsourced/nonemployee role | Personnel status, appointment, oversight |
| 1.04 | ARSO | Source-based role/reference information | Appointment, training verification, agency communications |
| 1.05 | Channeler | Flags same-purpose role overlap, missing FBI selection or NGI authorization | Actual FBI selection, direct NGI agreement or legal status |
| 1.06 | Channeling | Read-only operational definition | Real service delivery |
| 1.07 | Chief Administrator | Flags non-repository employment, when applicable | Actual repository employment or delegation |
| 1.08 | CHRI | Distinguishes reported history from standalone biometric identification data | Real classification of an actual record |
| 1.09 | Criminal History Record Check | Read-only fingerprint-based check definition | Authorized search or result |
| 1.10 | CJIS APB | Read-only governance definition | APB review/approval or direct access grants |
| 1.11 | Compact Officer | State/federal role explanation; state employment guardrail | Actual appointment or full-time status |
| 1.12 | Compact Council | Read-only governance definition | Issuance of rules/approval |
| 1.13 | CJISSECPOL | Read-only security baseline definition | End-to-end compliance |
| 1.14 | Dissemination | CHRI dissemination remains disabled | Any authorized CHRI delivery |
| 1.15 | Noncriminal Justice Administrative Functions | Defines submission/receipt boundary; live service disabled | Production FBI message exchange |
| 1.16 | Noncriminal Justice Purposes | Selects documented-type category for synthetic dry-run | Actual statutory authority for specific individuals |
| 1.17 | Outsourcing Agreement | Flags whether agreement is reported | Executed and legally sufficient contract |
| 1.18 | Outsourcing Standard | Read-only law/security scope | Legal compliance certification |
| 1.19 | PII | Independently flags biometric/other identifier categories | Identity data intake, record-level classification |
| 1.20 | Physically Secure Location | Read-only physical/personnel control definition | Facility inspection or certification |
| 1.21 | PII Breach | Read-only event definition; separate time planner exists | Incident discovery, notice dispatch or case handling |
| 1.22 | Positive Identification | Rejects name-only as sufficient; labels ten-rolled/ten-flat capture as possible qualifying method | Positive comparison result; an FBI response |
| 1.23 | Rap Back Messaging Service | Read-only routing definition; service disabled | Live messaging, subscriptions, validation or approval |
| 1.24 | Sanitizing | Clarifies overwriting/degaussing versus mere file deletion | Actual sanitization of media under CJISSECPOL |
| 1.25 | Security Violation | Read-only legal/policy event definition | Determination of actual policy violations |

## Admin endpoints

- `GET /api/section-one` returns all 25 paraphrased definitions with original
  section and PDF-page references.
- `POST /api/section-one/assess` accepts a strict set of nonidentifying role,
  authority, purpose, data-classification and biometric-method flags.
  Outputs include contradictory-claim warnings and always return
  `production_ready: false`, `externally_verified: false`, and
  `real_ngi_submission_enabled: false`.

Both routes require the local admin token and AC-8-style system-use
acknowledgment. Assessment calls append only a sanitized event to the
local audit journal; raw inputs are not written there or elsewhere.

## Scope and operational limits

A displayed term, declared checkbox, agency-selection claim, government
authority category or test-gateway HTTP response is **not proof** of an
approved FBI channeler connection or CJIS conformance. The reference
screen does not implement biometric matching, Rap Back, record retention,
storage of PII, CHRI distribution, incident notification or hardware media
sanitization.

Independent legal review, specific statutory purpose, agreement/agency
authorization, personnel controls, physical security, communications
engineering, EBTS implementation and FBI acceptance testing are outside
Section 1's definitional scope and remain necessary before production.

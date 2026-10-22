# Section 5 — Miscellaneous Provisions

**Primary source:** National Crime Prevention and Privacy Compact Council,
*Security and Management Control Outsourcing Standard for Channeling*,
last updated **November 29, 2023**, **``5.01–5.08**,
printed **pages 10–11** / PDF **pages 18–19**.

The provisions concern legal scope, modifications of the Standard,
other-party rights, incorporation of CJISSECPOL, minimum security
measures, regulator audit/investigation powers, and postal routing.
**These are not eight new FBI sender protocols or production permissions.**
The code makes the restrictions visible and fail-closed, without
pretending to exercise Compact Council, APB or government authority.

| Section | Source-derived rule | Implemented capability | Remaining external action |
| --- | --- | --- | --- |
| **5.01 (PDF 18)** | Only the Compact Council may modify the Standard under 28 CFR Part 906, within the scope of that rule. Standard applies to every personnel, system, network and facility supporting/acting for the Authorized Recipient | Immutable source catalogue; strict four-asset coverage validator; documentary checkpoints | Government rulemaking and factual review of complete actual asset inventory |
| **5.02 (PDF 18)** | Standard does not confer rights, privileges or obligations on other persons beyond Channeler, Authorized Recipient, FBI and, where applicable, Compact Officer/Chief Administrator | Named-party and third-party rights scenario checker; no access/rights issuance | Actual legal capacity, authorizations and contract interpretation |
| **5.03 (PDF 18)** | CJIS Security Policy incorporated **by reference** | Explicit incorporation flag, version inventory outline, check | Current official CJIS Security Policy and conforming technical controls |
| **5.04 (PDF 18)** | Standard is **minimum basis**; Authorized Recipient–Channeler agreement may impose **stricter** terms. Footnote 17 gives examples including additional audits, fees or security; Council, Recipients, state Compact Officer/Chief Administrator may require stricter standards | Stricter-versus-baseline contract comparator, evidence item and blank contract supplement | Actual mutually applicable contract clauses, additional audits/fees/security and legal review |
| **5.05 (PDF 18)** | Only Council modifies Standard; CJIS Security Policy minima modified through **CJIS APB process**. Conformance cannot fall below Standard without Compact Council consent in consultation with U.S. Attorney General | Fail-closed checker rejects any local weakening; self-reported consent and consultation are **not verified**, never effective through app; source-based authority display | Official Council process, consultation, valid instruments, independently verified and implemented decisions |
| **5.06 (PDF 19)** | Compact Officer/Chief Administrator, Council and U.S. Attorney General may conduct **scheduled or unscheduled** audits. After termination, **Council, Attorney General and applicable state** may perform final Channeler systems audit | Separate actor/phase checks, readiness codes and blank audit-coordination outline | Real officials conducting announced/unannounced/final audits, access, evidence and findings |
| **5.07 (PDF 19)** | Compact Officer/Chief Administrator, Council and U.S. Attorney General may **investigate or decline** a report of unauthorized CHRI access | Strict named-authority checker for investigation and decline; blank external incident-referral outline | Real incident reporting under ``2–3 and competent authority's decision, actual investigation or declination |
| **5.08 (PDF 19)** | Notices, assurances, correspondence to FBI, Compact Council, FBI Compact Officer and U.S. Attorney General under the Standard sent by **First Class Mail** to published FBI Compact Officer routing | Read-only recipient/purpose post instruction and six blank copy-only documents; displays exact 2023 address | Verify current authoritative address; prepare/send First Class Mail; obtain evidence of posting/receipt and any substantive response |

## `5.08 postal address published in the 2023 Standard

    FBI Compact Officer
    BTC4
    FBI CJIS Division
    1000 Custer Hollow Road
    Clarksburg, WV 26306

The document expressly specifies **First Class Mail** for the notices,
assurances and correspondence within `5.08's scope. The software does
not substitute email, electronic forms or other routes. This source
does not establish the address is unchanged in 2026; an actual sender
must verify currently applicable instructions. The app never marks
mail as dispatched, received, or approved.

## Admin interfaces and safeguards

- `GET /api/misc` returns all eight clauses, 17 checklists and the
  published 2023 mail route with current validity **unverified**.
- `POST /api/misc/check` accepts an exact allowlisted ID, Boolean
  `reported` and restricted, nonidentifying evidence code. It uses
  a separate private atomic state file; security audit records contain
  only a sanitized event type.
- `POST /api/misc/scope` checks only enumerated party type,
  recipient-supporting asset type, and Boolean roles/rights claims.
- `POST /api/misc/changes` checks enumerated instrument,
  stricter/unchanged/weaker direction, actor and *reported* external
  consent/consultation. It **never** authorizes minimum relaxation,
  rule amendment or contract amendment.
- `POST /api/misc/authority` checks only whether actor/action
  combinations are *named in* ``5.06–5.07. It does not authenticate
  officials, authorize audits or decide investigations.
- `POST /api/misc/mail` returns the published routing instructions
  for four specified addressee types and three correspondence classes.
  No mail, postal verification or legal acknowledgment occurs.
- `GET /api/misc/templates` provides six **blank** copy-only outlines
  (cover, policy incorporation, stronger contract clauses, proposed
  change referral, government audits, unauthorized-access reporting).

The server requires local token authentication and its system-use
notice. Request schemas reject names, real CHRI, actual OCA/ORI,
applicant details, personnel records, incident descriptions, documents,
unrecognized roles and unsolicited data. No source-check operation
grants production permissions. All self-reported checklists remain
`independently_verified: false` and `production_ready: false`.

## Important distinction: implemented versus legally fulfilled

The prototype now **models all Section 5 provisions**, but does not
perform legal rulemaking, authenticate public officials, obtain Compact
Council consent, use the CJIS APB change process, verify actual
Recipient–Channeler agreements, grant rights, schedule government audits,
investigate CHRI events, mail correspondence or prove deliveries.

Actual operational compliance also requires the complete preceding
Sections 1–4, current CJISSECPOL, valid written agreements, security
engineering and regulator/agency reviews. A reported reference code
cannot override the Standard, change the recipient's authority, or
certify CJIS compliance.

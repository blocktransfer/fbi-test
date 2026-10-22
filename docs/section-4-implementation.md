# Section 4 — Responsibilities of the FBI

**Source:** Compact Council, *Security and Management Control Outsourcing
Standard for Channeling*, approved November 29, 2023,
Section 4 (``4.01–4.10), **printed pp. 8–9 (PDF pp. 16–17)**.

The actual responsibilities belong to the **FBI** and/or the
**Compact Officer/Chief Administrator**, not the sender operator.
Local functions supply source-grounded evidence tracking, deadline
planning and draft outlines. They NEVER execute or certify agency actions.

| Clause | External government requirement | Local software |
| --- | --- | --- |
| 4.01 | Compact Officer/Chief Administrator examines legal authority, writes approval response; FBI coordinates | Three evidence checks; blank response outline |
| 4.01(a) | Combined state/federal representative-sample audit program **before** permission; first audit within one year of first CHRI receipt; at least triennial thereafter with generally accepted statistical sampling | Four checks; calendar reference; sample-size estimate only |
| 4.02 | FBI update notices to Channelers, latest Standard/CJISSECPOL supplied within 60 calendar days unless directed otherwise | Two checks, 60-day calculator, distribution outline |
| 4.03 | FBI 90-day, one-year and triennial Channeler audits; audit certification **and copy of results** sent to FBI Compact Officer within 90 days of first CHRI receipt | Five checks, separated FBI audit calendar and blank certification form |
| 4.04 | FBI background-checks CHRI-access personnel, maintains roster and passed-check list, updates access records within 24 hours | Four checks, 24-hour calculator, no personnel record intake |
| 4.05 | FBI assigns OCA to EACH Authorized Recipient and ORI to EACH Channeler | Two document-reference checks, no identifier issuance |
| 4.06 | FBI ensures physical security of Channeler site | Site-review checkpoint and blank inspection outline |
| 4.07 | FBI ensures physical/personnel/IT Security Program against current policies and gives written approval | Two checks, blank written approval review |
| 4.08 | FBI reviews and provides written Security Awareness Training Program approval | One check, blank review outline |
| 4.09 | FBI reviews and provides written system contingency plan approval | One check, blank review outline |
| 4.10 | FBI approves Channeler network diagram, keeps current copy, reviews and approves modifications | Three checks and blank change-review outline |

## Source-faithful audit timing

The first combined sample audit under `4.01(a) is expressly due within
one year from first approved CHRI receipt. `4.03 expressly requires
FBI first audit certification and its results within 90 calendar days of
first CHRI receipt. Both obligations exist separately; one does not
discharge the other.

`4.03 additionally says the FBI conducts 90-day, one-year and triennial
audits. It does not expressly set the clock for every later one-year or
triennial audit. The calendar shows **illustrative** later anniversaries
from first receipt, not definitive source-prescribed due dates.

The `4.01(a) numeric sample-size planner accepts ONLY counts of
Channelers and Recipients, confidence (90/95/99%), margin (2/5/10%),
and method simple_random. It conservatively estimates a finite-population
sample (p = 0.5): `ceil(N*z²*0.25/(e²*(N-1)+z²*0.25))`.
It does not choose people or organizations, create a valid sampling
frame, determine coverage/nonresponse, run audits or satisfy the
requirement for a representative sample determined through generally
accepted statistical sampling methods.

## Files, API and security

- `fbi_oversight.py`: 11 source entries including `4.01(a), with
  government actors, printed page references, and 28 evidence checkpoints.
- `fbi_oversight_schedule.py`: UTC-only planning for policy distribution
  (60 days), FBI roster updates (24 hours), first audit certification
  (90 days), first combined audit (one year), later audit references.
- `fbi_oversight_sampling.py`: counts-only SRS estimation.
- `fbi_oversight_checklist.py`: separate owner-only, audited, atomic
  checklist store. Only restricted nonidentifying reference codes;
  no real federal decisions or documents.
- `fbi_oversight_templates.py`: nine blank copy-only review outlines;
  never sent to officials.
- `GET /api/fbi-oversight` returns source mapping + unverified status.
  `POST /api/fbi-oversight/check` stores only allowlisted references.
  `POST /api/fbi-oversight/deadlines` and `POST /api/fbi-oversight/sample`
  accept no personal identifiers and persist no planner inputs.
  `GET /api/fbi-oversight/templates` returns blank outlines.

All API access requires token/AC-8-style acknowledgement.
No API verifies approval, grants production access, issues an OCA/ORI,
screens personnel, signs federal decisions, conducts audits, maintains
official FBI diagrams or connects to FBI NGI. The local audit journal
is not an independently anchored compliance audit system.

Actual legal authority review, execution of the combined audit program,
FBI audits and certifications, OCA/ORI assignments, personnel clearance,
written plan approvals and production CJIS Security Policy safeguards
must be provided and verified by the proper government officials.

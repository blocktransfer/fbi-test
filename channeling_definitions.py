"""Section 1 (definitions 1.01-1.25) of Compact Council Channeling Standard.

Reference catalog only. Definitions establish vocabulary and boundaries, not
automatic FBI authorization, system compliance or an approved network route.
Source: National Crime Prevention and Privacy Compact Council, Security and
Management Control Outsourcing Standard for Channeling, 2023-11-29, PDF 3-7.
"""

from __future__ import annotations

from copy import deepcopy

SOURCE = {
    "title": "Security and Management Control Outsourcing Standard for Channeling",
    "publisher": "National Crime Prevention and Privacy Compact Council",
    "approved": "2023-11-29",
    "section": "Section 1 — Definitions",
    "pdf_pages": "3-7",
}

# (section, defined term, faithful short paraphrase, PDF page, implementation)
# "external" explicitly means the organization/agency must establish the fact.
DEFINITIONS = (
    ("1.01", "Access to CHRI", "Viewing or using CHRI from the III; channelers generally do not gain direct III terminal/automated access except under the stated exceptions.", "3", "boundary"),
    ("1.02", "Authorized Recipient", "An entity legally empowered to receive CHRI for noncriminal justice purposes under applicable federal authority or qualifying state authority with Attorney General approval.", "3", "external"),
    ("1.03", "Authorized Recipient Point of Contact (ARPOC)", "The Authorized Recipient employee who administers CJIS programs and oversees policy compliance; this role cannot be outsourced.", "3", "role_guard"),
    ("1.04", "Authorized Recipient Security Officer (ARSO)", "The appointed Authorized Recipient security overseer who monitors channeler safeguards, annual security training and FBI security communications.", "3", "external"),
    ("1.05", "Channeler", "An FBI-selected contractor separate from the Authorized Recipient for the specific purpose, with an agreement and direct NGI connection for forwarding fingerprints and receiving CHRI on the recipient's behalf.", "3-4", "role_guard"),
    ("1.06", "Channeling", "Noncriminal justice administrative functions performed by a Channeler; see the more specific description in 1.15.", "4", "boundary"),
    ("1.07", "Chief Administrator", "Chief/designee of a Non-Compact State criminal history repository; must be a repository employee and cannot be outsourced.", "4", "role_guard"),
    ("1.08", "Criminal History Record Information (CHRI)", "Identifiable descriptions and criminal-charge/disposition histories; standalone identification or fingerprint records without indications of criminal justice involvement are excluded.", "4", "classification"),
    ("1.09", "Criminal History Record Check", "An authorized noncriminal justice fingerprint-based state and/or FBI repository search for this Standard.", "4", "boundary"),
    ("1.10", "CJIS Advisory Policy Board (APB)", "FBI Director's advisory body for CJIS policy and expanded systems uses; it makes recommendations, not operational access grants.", "4", "external"),
    ("1.11", "Compact Officer", "FBI-designated Compact administrator or state repository Chief Administrator/designee, the latter a regular full-time repository employee.", "4-5", "external"),
    ("1.12", "Compact Council", "Council created by the 1998 Compact Act to establish rules and procedures for noncriminal justice use of the III.", "5", "external"),
    ("1.13", "CJIS Security Policy (CJISSECPOL)", "Current FBI security baseline protecting CJI through its life cycle, from creation to destruction at rest and in transit.", "5", "external"),
    ("1.14", "Dissemination", "Disclosure of CHRI from an authorized Channeler to its Authorized Recipient under this Standard.", "5", "boundary"),
    ("1.15", "Noncriminal Justice Administrative Functions", "Electronic fingerprint submission and CHRI receipt via FBI by a Channeler on behalf of an Authorized Recipient.", "5", "boundary"),
    ("1.16", "Noncriminal Justice Purposes", "Lawfully authorized, noncriminal justice uses such as employment suitability, licensing, immigration/naturalization and national security clearances.", "5", "classification"),
    ("1.17", "Outsourcing Agreement", "Contract or agreement under which a Channeler submits fingerprints and receives CHRI for an Authorized Recipient.", "5", "external"),
    ("1.18", "Outsourcing Standard", "Compact Council rules under 28 CFR part 906 governing permitted CHRI access, use, dissemination, retention, confidentiality, audits, sanctions and termination.", "6", "external"),
    ("1.19", "Personally Identifiable Information (PII)", "Information that distinguishes or traces an individual, including biometric records and linkable personal identifiers.", "6", "classification"),
    ("1.20", "Physically Secure Location", "Facility or space with sufficient physical and personnel controls to safeguard CHRI and supporting systems.", "6", "external"),
    ("1.21", "PII Breach", "Loss of control or actual/potential unauthorized acquisition, access or disclosure of PII.", "6", "classification"),
    ("1.22", "Positive Identification", "Identity established by fingerprint/other comparably reliable biometrics; name-only matches do not qualify. Footnote specifies qualifying ten-rolled or ten-flat prints for noncriminal justice uses.", "6", "identity_guard"),
    ("1.23", "Rap Back Messaging Service (RBMS)", "Noncriminal justice Rap Back messages, including unsolicited responses, to/from FBI via Channeler with immediate forwarding to the Authorized Recipient.", "7", "boundary"),
    ("1.24", "Sanitizing", "Overwriting or degaussing media as required by CJISSECPOL; deleting a file is not automatically demonstrated sanitization.", "7", "external"),
    ("1.25", "Security Violation", "Failure to prevent unlawful/noncompliant access, use, retention or disclosure of CHRI under governing laws, Compact rules or CJISSECPOL.", "7", "classification"),
)

def definition_catalog() -> dict:
    """Expose policy descriptions, not operational permissions or user data."""
    return {
        "source": deepcopy(SOURCE),
        "total": len(DEFINITIONS),
        "definitions_only": True,
        "production_ready": False,
        "entries": [
            {
                "section": section,
                "term": term,
                "summary": summary,
                "pdf_pages": pages,
                "implementation": implementation,
                "external_approval_verified": False,
            }
            for section, term, summary, pages, implementation in DEFINITIONS
        ],
    }

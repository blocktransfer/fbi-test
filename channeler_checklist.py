"""Section 3 Channeler checklist, separate from Recipient §2 tracking.

Reuses the tested owner-only, atomically written, audited metadata store.
Only safe evidence reference codes; never actual CHRI, PII or legal documents.
"""
from channeler_policy import CHECK_IDS
from recipient_checklist import RecipientChecklist, ChecklistError


class ChannelerChecklist(RecipientChecklist):
    allowed_keys = CHECK_IDS
    event_prefix = "channeler"

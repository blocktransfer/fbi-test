"""Private operator-reported Section 5 documentary checkpoints.

No legal amendments, waivers, agency findings, CHRI or personal information
are stored. Reported evidence references are NOT independent verification.
"""
from misc_provisions import CHECK_IDS
from recipient_checklist import RecipientChecklist, ChecklistError


class MiscChecklist(RecipientChecklist):
    allowed_keys = CHECK_IDS
    event_prefix = "misc"

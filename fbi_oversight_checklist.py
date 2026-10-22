"""Protected, nonidentifying self-reported Section 4 oversight reference metadata.

This is NOT the FBI's official audit record, background-check roster,
approval register, OCA/ORI assignment, or proof of permission.
"""
from fbi_oversight import CHECK_IDS
from recipient_checklist import RecipientChecklist, ChecklistError


class OversightChecklist(RecipientChecklist):
    allowed_keys = CHECK_IDS
    event_prefix = "fbi_oversight"

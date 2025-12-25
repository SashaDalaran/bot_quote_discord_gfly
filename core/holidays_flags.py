# ==================================================
# core/holidays_flags.py — Compatibility Re-Export
# ==================================================
#
# The project uses a single source of truth for flag/category emojis:
# services/holidays_flags.py (user-managed mapping).
#
# Some legacy modules import from core.holidays_flags, so we re-export here.
#
# Layer: Core
# ==================================================

from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

__all__ = ["COUNTRY_FLAGS", "CATEGORY_EMOJIS"]

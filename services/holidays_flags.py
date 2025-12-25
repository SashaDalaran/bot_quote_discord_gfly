# ==================================================
# services/holidays_flags.py — Re-exports for emoji/flag mappings
# ==================================================
#
# In the Telegram bot the mappings live in services/.
# In the Discord bot they historically lived in core/.
# To keep the "Services" layer consistent (and to allow
# shared service code like birthday_format.py), we re-export
# them from here.
#
# Layer: Services
# ==================================================

from core.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

__all__ = ["COUNTRY_FLAGS", "CATEGORY_EMOJIS"]

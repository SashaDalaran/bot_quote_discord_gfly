# core/settings.py
import os

# ============================
# Discord Bot Settings
# ============================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Channels
BANLU_CHANNEL_ID = int(os.getenv("BANLU_CHANNEL_ID", "0"))

HOLIDAYS_CHANNEL_IDS = [
    int(x) for x in os.getenv("HOLIDAYS_CHANNEL_IDS", "").split(",") if x
]

# ============================
# Timers / Scheduler
# ============================

DEFAULT_TIMEZONE = "UTC"
MAX_TIMERS_PER_CHANNEL = 50

# ============================
# Feature Flags
# ============================

ENABLE_DAILY_BANLU = True
ENABLE_HOLIDAYS = True
ENABLE_TIMERS = True

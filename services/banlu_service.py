# ==================================================
# services/banlu_service.py — Ban'Lu Quotes Service
# ==================================================
#
# Loads Ban'Lu quotes and provides helpers for daily posting.
#
# Layer: Services
# ==================================================

from __future__ import annotations

import os
import random
import re
from typing import List, Optional

from core.settings import BANLU_WOWHEAD_URL

# Optional: link/image for Ban'Lu embeds in Discord.
# If not provided, we default to the given Steam page (The Last of Us Part I)
# and its header image. You can override with:
# - BANLU_LINK_URL (clickable link on the embed)
# - BANLU_IMAGE_URL (image displayed in the embed)
DEFAULT_BANLU_STEAM_URL = "https://store.steampowered.com/app/1888930/The_Last_of_Us_Part_I/"

_STEAM_APP_RE = re.compile(r"/app/(\d+)/")

def _steam_header_image(url: str) -> Optional[str]:
    """Try to derive Steam header image URL from a Steam store URL."""
    m = _STEAM_APP_RE.search(url or "")
    if not m:
        return None
    app_id = m.group(1)
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

BANLU_LINK_URL = os.getenv("BANLU_LINK_URL", DEFAULT_BANLU_STEAM_URL)
BANLU_IMAGE_URL = os.getenv("BANLU_IMAGE_URL", _steam_header_image(BANLU_LINK_URL) or BANLU_WOWHEAD_URL)


def load_banlu_quotes(path: str) -> List[str]:
    """Load Ban’Lu quotes from UTF-8 file."""
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def get_random_banlu_quote(quotes: List[str]) -> Optional[str]:
    if not quotes:
        return None
    return random.choice(quotes)


def format_banlu_message(quote: str) -> str:
    """Discord-friendly message format."""
    # Keep it simple: short intro + quote + reference link.
    return (
        "🧙‍♂️ **Ban'Lu** — the Grandmaster of Deception\n"
        f"💬 *{quote}*\n"
        f"🔗 {BANLU_WOWHEAD_URL}"
    )

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
from typing import List, Optional

from core.settings import BANLU_WOWHEAD_URL


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

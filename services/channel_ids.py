# ==================================================
# services/channel_ids.py — Channel ID Helpers
# ==================================================
#
# Helpers for parsing and validating chat/channel IDs from environment variables.
#
# Layer: Services
#
# Why this exists:
# - Daily jobs can post to one or multiple channels.
# - Fly.io secrets/environment variables store these IDs as strings.
# - Parsing/validation should be centralized to avoid copy-paste.
#
# Responsibilities:
# - Parse comma-separated lists of integers from env values
# - Filter invalid entries with clear logging
#
# Env format:
#   SOME_CHANNEL_ID="123"                -> [123]
#   SOME_CHANNEL_ID="123,456,789"        -> [123,456,789]
#
# NOTE:
# - We intentionally support *one or many* IDs in the same variable.
# - We do NOT provide backward-compatible aliases here on purpose.
#   (Keep secrets clean and consistent.)
# ==================================================

from __future__ import annotations

import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def parse_chat_ids_from_env(env_key: str) -> List[int]:
    """Parse a comma-separated list of chat IDs from an env var.

    Examples:
        ENV_KEY="123"
        ENV_KEY="123,456,789"

    Notes:
    - Discord channel IDs are positive integers.
    - Missing/empty values mean "no configured destinations".

    Args:
        env_key: Environment variable name to read.

    Returns:
        List of valid channel IDs (ints). Invalid parts are ignored with warnings.
    """
    raw = (os.getenv(env_key) or "").strip()
    if not raw:
        return []

    ids: List[int] = []
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        # allow optional + sign
        if token.startswith("+"):
            token = token[1:].strip()
        try:
            value = int(token)
        except ValueError:
            logger.warning("Invalid channel ID '%s' in %s; skipping.", part, env_key)
            continue
        if value <= 0:
            logger.warning("Discord channel IDs must be positive (%s in %s); skipping.", value, env_key)
            continue
        ids.append(value)

    if not ids:
        logger.warning("No valid channel IDs found in %s; skipping send.", env_key)

    return ids

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
# Boundaries:
# - This module does NOT send messages.
# - It only prepares a validated list of IDs for callers.
#
# ==================================================

from __future__ import annotations

import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def parse_chat_ids_from_env(env_key: str) -> List[int]:
    """Parse a comma-separated list of chat IDs from an env var.

    Expected format:
        ENV_KEY="123,-1009876543210,456"

    Notes:
    - Telegram channel IDs are often negative (e.g. -100...).
    - We treat missing/empty values as "no configured destinations".

    Args:
        env_key:
            Name of the environment variable to read.

    Returns:
        A list of valid integer chat IDs. Empty if none.
    """

    # --------------------------------------------------
    # Read raw value (secrets/config live in env)
    # --------------------------------------------------
    raw = (os.getenv(env_key) or "").strip()
    if not raw:
        # Not an error: daily jobs may be disabled by simply not setting env vars.
        return []

    # --------------------------------------------------
    # Split + normalize tokens
    # --------------------------------------------------
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    ids: List[int] = []

    # --------------------------------------------------
    # Validate each token
    # --------------------------------------------------
    for p in parts:
        try:
            ids.append(int(p))
        except ValueError:
            # Log and skip instead of crashing at startup.
            logger.warning("Invalid chat id '%s' in %s; skipping it.", p, env_key)

    # --------------------------------------------------
    # Final sanity logging (helps during deployments)
    # --------------------------------------------------
    if not ids:
        logger.warning("No valid chat IDs found in %s; skipping send.", env_key)

    return ids


def parse_chat_ids(env_key: str) -> List[int]:
    """
    Backward-compatible alias.

    Older modules import `parse_chat_ids(...)`.
    The canonical function is now `parse_chat_ids_from_env(...)`,
    but we keep this wrapper to avoid breaking imports.
    """
    return parse_chat_ids_from_env(env_key)

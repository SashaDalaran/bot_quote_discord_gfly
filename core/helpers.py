# ==================================================
# core/helpers.py — File Utils, Timer Storage, Formatting
# ==================================================

import os
import json

TIMERS_FILE = "timers.json"


# ===========================
# File Utilities
# ===========================
def load_lines(path: str) -> list[str]:
    """
    Read a text file line-by-line, stripping whitespace.
    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


# ===========================
# Timer Storage (timers.json)
# ===========================
def load_timers() -> dict:
    """
    Load timers.json and return its data structure.

    Returns a default structure if:
    - the file does not exist
    - the JSON is corrupted
    """
    if not os.path.exists(TIMERS_FILE):
        return {"next_timer_id": 1, "timers": []}

    try:
        with open(TIMERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to a safe default structure
        return {"next_timer_id": 1, "timers": []}


def save_timers(data: dict) -> None:
    """
    Save the timer dictionary back to timers.json
    using pretty-printed UTF-8 JSON.
    """
    with open(TIMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ===========================
# Time Formatting
# ===========================
def format_remaining(sec: int) -> str:
    """
    Format remaining seconds as:
        1d 4h 20m 15s

    Components that are zero (except seconds)
    are omitted for readability.
    """
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, sec = divmod(sec, 60)

    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")

    parts.append(f"{sec}s")  # seconds always included

    return " ".join(parts)


# ===========================
# Update Interval Selection
# ===========================
def choose_update_interval(sec_left: int) -> float:
    """
    Choose how often the timer UI should update,
    depending on the remaining time.

    This mirrors the logic of the Telegram version:
      > 10m → 30s
      >  3m → 5s
      >  1m → 2s
      > 10s → 1s
      >  3s → 0.5s
      otherwise → 0.25s
    """
    if sec_left > 10 * 60:
        return 30
    if sec_left > 3 * 60:
        return 5
    if sec_left > 60:
        return 2
    if sec_left > 10:
        return 1
    if sec_left > 3:
        return 0.5
    return 0.25

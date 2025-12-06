import os
import json

TIMERS_FILE = "timers.json"


def load_lines(path: str) -> list[str]:
    """Read a file line by line."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [x.strip() for x in f.readlines() if x.strip()]


# ---------- timers.json operations ----------

def load_timers() -> dict:
    """Load timers.json (return default structure if missing or corrupted)."""
    if not os.path.exists(TIMERS_FILE):
        return {"next_timer_id": 1, "timers": []}

    try:
        with open(TIMERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"next_timer_id": 1, "timers": []}


def save_timers(data: dict) -> None:
    """Save timers.json."""
    with open(TIMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- timer time formatting ----------

def format_remaining(sec: int) -> str:
    """Return a string like: 1d 4h 20m 15s."""
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
    parts.append(f"{sec}s")

    return " ".join(parts)


def choose_update_interval(sec_left: int) -> float:
    """
    Pick update interval based on remaining time.
    Same logic as the Telegram version.
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

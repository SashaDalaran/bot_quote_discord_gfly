# ==================================================
# core/timers.py — Persistent Timer Storage & Helpers
# ==================================================

from core.helpers import load_timers, save_timers


# ===========================
# Load Existing Timers on Startup
# ===========================
timers_data = load_timers()

# All active timers stored as: { timer_id: timer_dict }
date_timers: dict[int, dict] = {
    t["timer_id"]: t for t in timers_data["timers"]
}

# Next available ID for new timers
next_timer_id: int = timers_data.get("next_timer_id", 1)


# ===========================
# Create New Timer
# ===========================
def create_timer(channel_id, message_id, text, timestamp, tz_offset, pinned) -> int:
    """
    Create a new date-based timer and persist it.

    Returns:
        timer_id (int)
    """
    global next_timer_id

    timer = {
        "timer_id": next_timer_id,
        "channel_id": channel_id,
        "message_id": message_id,
        "text": text,
        "target_timestamp": timestamp,
        "tz_offset": tz_offset,
        "pinned": pinned,
    }

    date_timers[next_timer_id] = timer
    next_timer_id += 1
    save()

    return timer["timer_id"]


# ===========================
# Delete Timer
# ===========================
def delete_timer(timer_id: int) -> None:
    """
    Remove a timer by its ID.
    If the timer doesn't exist, nothing happens.
    """
    date_timers.pop(timer_id, None)
    save()


# ===========================
# Save All Timers to File
# ===========================
def save() -> None:
    """
    Persist the current state of timers to timers.json.
    """
    save_timers(
        {
            "next_timer_id": next_timer_id,
            "timers": list(date_timers.values()),
        }
    )

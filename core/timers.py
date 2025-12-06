from core.helpers import load_timers, save_timers

timers_data = load_timers()
date_timers = {t["timer_id"]: t for t in timers_data["timers"]}
next_timer_id = timers_data.get("next_timer_id", 1)


def create_timer(channel_id, message_id, text, timestamp, tz_offset, pinned):
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


def delete_timer(timer_id):
    date_timers.pop(timer_id, None)
    save()


def save():
    save_timers({
        "next_timer_id": next_timer_id,
        "timers": list(date_timers.values())
    })

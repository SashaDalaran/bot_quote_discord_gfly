# ==================================================
# services/birthday_service.py — Guild Events / Birthdays Service
# ==================================================
#
# Loads and normalizes guild event data (challenges, heroes, birthdays) used by daily jobs.
#
# Layer: Services
#
# Responsibilities:
# - Encapsulate domain logic and data access
# - Keep formatting rules consistent across commands and daily jobs
# - Provide stable functions consumed by commands/daily scripts
#
# Boundaries:
# - Services may use core utilities, but should avoid importing command modules.
# - Services should not perform Telegram network calls directly (commands/daily own messaging).
#
# ==================================================
import json
import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# Normalization helpers
# -----------------------------------------------------------------------------

# Common Cyrillic lookalikes that can sneak into tags like "Сhallenge".
_CYR_TO_LAT = str.maketrans({
    "С": "C",
    "с": "c",
    "О": "O",
    "о": "o",
    "А": "A",
    "а": "a",
    "Е": "E",
    "е": "e",
    "Р": "P",
    "р": "p",
    "Н": "H",
    "н": "h",
    "К": "K",
    "к": "k",
    "Т": "T",
    "т": "t",
    "М": "M",
    "м": "m",
    "В": "B",
    "в": "b",
    "Х": "X",
    "х": "x",
})


def _norm_token(value: Any) -> str:
    """Service function:  norm token."""
    if value is None:
        return ""
    s = str(value).strip().translate(_CYR_TO_LAT)
    s = " ".join(s.split())
    return s.lower()


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------


def _birthday_file_path() -> str:
    """Path to birthday + guild events json file (relative to project root)."""
    return os.path.join("data", "birthday.json")


def _strip_loose_json_list(text: str) -> str:
    """Turn a 'loose JSON' list into valid JSON.

    Supports files that look like:
        # comment
        { ... },
        { ... },

    We remove comment lines and wrap into [ ... ].
    """
    lines: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r",\s*]", "]", cleaned)
    cleaned = cleaned.strip()

    if not cleaned.startswith("["):
        cleaned = f"[{cleaned}]"

    return cleaned


def load_birthday_events(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Service function: load birthday events."""
    path = path or _birthday_file_path()

    try:
        raw_text = open(path, "r", encoding="utf-8").read()
    except FileNotFoundError:
        return []

    raw_text = raw_text.strip()
    if not raw_text:
        return []

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        try:
            data = json.loads(_strip_loose_json_list(raw_text))
        except json.JSONDecodeError:
            return []

    # allow either: [ {...}, {...} ]  OR  {"events": [ ... ]}
    if isinstance(data, dict):
        data = data.get("events", [])

    if not isinstance(data, list):
        return []

    return [e for e in data if isinstance(e, dict)]


# -----------------------------------------------------------------------------
# Date parsing / matching
# -----------------------------------------------------------------------------


def _parse_mmdd(mmdd: str) -> Optional[Tuple[int, int]]:
    """Service function:  parse mmdd."""
    m = re.fullmatch(r"\s*(\d{2})-(\d{2})\s*", mmdd)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def event_active_on(date_str: str, today: date) -> bool:
    """True if an event is active on the given 'today' date."""
    ds = (date_str or "").strip()
    if not ds:
        return False

    # single day
    if ":" not in ds:
        parsed = _parse_mmdd(ds)
        if not parsed:
            return False
        month, day = parsed
        return today.month == month and today.day == day

    # range
    start_s, end_s = ds.split(":", 1)
    start = _parse_mmdd(start_s)
    end = _parse_mmdd(end_s)
    if not start or not end:
        return False

    sm, sd = start
    em, ed = end
    wraps_year = (em, ed) < (sm, sd)

    try:
        if not wraps_year:
            start_date = date(today.year, sm, sd)
            end_date = date(today.year, em, ed)
            return start_date <= today <= end_date

        # wraps across year boundary, e.g. 12-19:01-20
        if (today.month, today.day) <= (em, ed):
            start_date = date(today.year - 1, sm, sd)
            end_date = date(today.year, em, ed)
        else:
            start_date = date(today.year, sm, sd)
            end_date = date(today.year + 1, em, ed)

        return start_date <= today <= end_date
    except ValueError:
        # invalid calendar date
        return False


# -----------------------------------------------------------------------------
# Grouping
# -----------------------------------------------------------------------------


def _event_kind(event: Dict[str, Any]) -> str:
    """Classify event into: challenge | hero | birthday | other."""
    categories = [_norm_token(x) for x in (event.get("category") or []) if x]
    countries = [_norm_token(x) for x in (event.get("countries") or []) if x]

    if "birthday" in categories:
        return "birthday"

    if "challenge" in categories or "challenge" in countries:
        return "challenge"

    if "accept" in categories or "hero" in categories:
        return "hero"

    # soft fallback: a single-day murloc entry is very likely a birthday
    if "murloc" in countries and ":" not in str(event.get("date", "")):
        return "birthday"

    return "other"


def get_today_birthday_payload(
    events: Optional[List[Dict[str, Any]]] = None,
    today: Optional[date] = None,
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """Return payload for birthday_format.format_birthday_message.

    Returns None when there is nothing to send.
    """
    today = today or date.today()
    events = events if events is not None else load_birthday_events()

    challenges: List[Dict[str, Any]] = []
    heroes: List[Dict[str, Any]] = []
    birthdays: List[Dict[str, Any]] = []

    for event in events:
        if not event_active_on(str(event.get("date", "")), today):
            continue

        kind = _event_kind(event)
        if kind == "challenge":
            challenges.append(event)
        elif kind == "hero":
            heroes.append(event)
        elif kind == "birthday":
            birthdays.append(event)

    if not (challenges or heroes or birthdays):
        return None

    return {
        "challenges": challenges,
        "heroes": heroes,
        "birthdays": birthdays,
    }
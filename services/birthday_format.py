# ==================================================
# services/birthday_format.py — Guild Events Message Formatter
# ==================================================
#
# Formats guild events (challenges/heroes/birthdays) into Telegram-friendly messages with consistent emoji rules.
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
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from services.birthday_service import _norm_token  # reuse normalization (avoid duplicates)
# IMPORTANT:
# - Do NOT modify services/holidays_flags.py (user-managed mapping).
# - That module may or may not expose UI_EMOJIS depending on the deployed version.
#   To avoid startup crashes, we only import the stable maps and keep local UI defaults here.
from services.holidays_flags import CATEGORY_EMOJIS, COUNTRY_FLAGS

# Normalized lookup maps (without touching services/holidays_flags.py)
_COUNTRY_FLAGS_NORM = {
    _norm_token(k): v for k, v in COUNTRY_FLAGS.items() if _norm_token(k)
}
_CATEGORY_EMOJIS_NORM = {
    _norm_token(k): v for k, v in CATEGORY_EMOJIS.items() if _norm_token(k)
}

# Normalized lookup dicts (built from holidays_flags.py at import time)
def _norm_key(value: Any) -> str:
    """Service function:  norm key."""
    s = _norm_token(value)
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

_COUNTRY_FLAGS_NORM = {_norm_key(k): v for k, v in COUNTRY_FLAGS.items()}
_CATEGORY_EMOJIS_NORM = {_norm_key(k): v for k, v in CATEGORY_EMOJIS.items()}


# Minimal UI emojis used only for section headers/formatting.
# (Categories & countries must come from holidays_flags.)
UI = {
    "calendar": "📅",
    "challenge": "🏆",
    "heroes": "🦸",
    "birthdays": "🎂",
}


# ------------------------------
# Formatting helpers
# ------------------------------

def _ensure_blank(lines: List[str]) -> None:
    """Append a single blank line if the last line is not blank.

    We use this to guarantee consistent spacing between sections
    without creating double-empty lines.
    """
    if lines and lines[-1] != "":
        lines.append("")


# ------------------------------
# Date helpers
# ------------------------------

_MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def _format_short_date(d: date) -> str:
    """Service function:  format short date."""
    return f"{d.day:02d} {_MONTH_ABBR[d.month]}"


def _format_range(start: date, end: date) -> str:
    # Example: Dec 19–Jan 20
    """Service function:  format range."""
    return f"{_MONTH_ABBR[start.month]} {start.day}–{_MONTH_ABBR[end.month]} {end.day}"


def _days_word(n: int) -> str:
    # English pluralization helper: day/days
    """Service function:  days word."""
    n = abs(int(n))
    if 11 <= (n % 100) <= 14:
        return "days"
    last = n % 10
    if last == 1:
        return "day"
    if 2 <= last <= 4:
        return "days"
    return "days"


@dataclass(frozen=True)
class RangeProgress:
    start: date
    end: date
    day_index: int
    total_days: int
    remaining_days: int


def _range_dates(date_str: str, today: date) -> Optional[Tuple[date, date]]:
    """Parse 'MM-DD:MM-DD' into actual start/end dates around 'today'.

    Handles year wrap (e.g. 12-19:01-20).
    """
    if ":" not in date_str:
        return None

    start_str, end_str = date_str.split(":", 1)
    sm, sd = map(int, start_str.split("-"))
    em, ed = map(int, end_str.split("-"))

    wraps = (em, ed) < (sm, sd)

    # choose a year so that today is inside the window
    if wraps:
        if today.month > sm or (today.month == sm and today.day >= sd):
            start_y = today.year
            end_y = today.year + 1
        else:
            start_y = today.year - 1
            end_y = today.year
    else:
        start_y = today.year
        end_y = today.year

    return date(start_y, sm, sd), date(end_y, em, ed)


def _range_progress(date_str: str, today: date) -> Optional[RangeProgress]:
    """Service function:  range progress."""
    rng = _range_dates(date_str, today)
    if not rng:
        return None

    start, end = rng
    if not (start <= today <= end):
        return None

    day_index = (today - start).days + 1
    total_days = (end - start).days + 1
    remaining_days = total_days - day_index

    return RangeProgress(
        start=start,
        end=end,
        day_index=day_index,
        total_days=total_days,
        remaining_days=remaining_days,
    )


# ------------------------------
# Emoji resolvers
# ------------------------------


def _first_token(values: List[str]) -> str:
    """Service function:  first token."""
    return values[0] if values else ""


def _emoji_for_category(categories: List[str]) -> str:
    """Service function:  emoji for category."""
    if not categories:
        return ""
    out = []
    for cat in categories:
        emoji = _CATEGORY_EMOJIS_NORM.get(_norm_key(cat))
        if emoji:
            out.append(emoji)
    return "".join(out)


def _emoji_for_country(countries: List[str]) -> str:
    """Service function:  emoji for country."""
    if not countries:
        return ""
    out = []
    for c in countries:
        emoji = _COUNTRY_FLAGS_NORM.get(_norm_key(c))
        if emoji:
            out.append(emoji)
    return "".join(out)


def _as_list(value: Any) -> List[str]:
    """Normalize a value that can be list/str/None into a list of strings.

    Birthday JSON may use either singular or plural keys and can store either:
      - "country": "US" or "countries": ["US", "CA"]
      - "category": "Fun" or "categories": ["Fun", "Religious"]

    We keep order and do NOT deduplicate (user may intentionally map the same emoji for
    multiple tokens and want to see them all).
    """

    if value is None:
        return []
    if isinstance(value, list):
        out: List[str] = []
        for v in value:
            s = str(v).strip()
            if s:
                out.append(s)
        return out
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        # Allow light separators if user stores "US,CA" etc.
        parts = re.split(r"[,;/]", s)
        return [p.strip() for p in parts if p.strip()]
    s = str(value).strip()
    return [s] if s else []


def _emoji_for_categories_all(categories: List[str]) -> str:
    """Service function:  emoji for categories all."""
    emojis: List[str] = []
    for token in categories:
        key = _norm_key(token)
        emoji = _CATEGORY_EMOJIS_NORM.get(key)
        if emoji:
            emojis.append(emoji)
    return "".join(emojis)


def _emoji_for_countries_all(countries: List[str]) -> str:
    """Service function:  emoji for countries all."""
    emojis: List[str] = []
    for token in countries:
        key = _norm_key(token)
        emoji = _COUNTRY_FLAGS_NORM.get(key)
        if emoji:
            emojis.append(emoji)
    return "".join(emojis)


# ------------------------------
# Name parsing
# ------------------------------


def _split_owner_task(name: str) -> Tuple[str, str]:
    """Challenge line: 'OWNER TASK...' -> ('OWNER', 'TASK...')."""
    parts = name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:]).replace("  ", " ")


def _split_owner_desc(name: str) -> Tuple[str, str]:
    """Hero line: 'OWNER - desc' or 'OWNER desc' -> ('OWNER', 'desc')."""
    s = name.strip()
    if " - " in s:
        left, right = s.split(" - ", 1)
        return left.strip(), right.strip()
    if "-" in s:
        left, right = s.split("-", 1)
        return left.strip(), right.strip()
    parts = s.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:]).strip()


# ------------------------------
# Public API
# ------------------------------


def format_birthday_message(payload: Dict[str, Any], today: date) -> str:
    """Render a single message for the 'Guild events' channel."""

    title = payload.get("title", "Guild events")
    challenges: List[Dict[str, Any]] = payload.get("challenges", [])
    heroes: List[Dict[str, Any]] = payload.get("heroes", [])
    birthdays: List[Dict[str, Any]] = payload.get("birthdays", [])

    cal = "📅"
    cake = "🎂"
    range_emoji = "🗓️"

    lines: List[str] = []
    lines.append(f"{cal} {title} — {_format_short_date(today)}")
    lines.append("")

    # -------------------
    # Guild Challenge
    # -------------------
    lines.append("🏆 Guild Challenge")
    _ensure_blank(lines)  # always separate header from content

    if not challenges:
        lines.append("↳ no active challenges")
        _ensure_blank(lines)  # ensure spacing before the next section
    else:
        for ev in challenges:
            name = str(ev.get("name", "")).strip()
            categories = ev.get("category", []) or []
            countries = ev.get("countries", []) or []

            owner, task = _split_owner_task(name)
            owner_emoji = _emoji_for_country(countries)
            task_emoji = _emoji_for_category(categories)

            if owner:
                lines.append(f"{owner_emoji} {owner}".strip())
            if task:
                lines.append(f"↳ {task_emoji} {task}".strip())

            prog = _range_progress(str(ev.get("date", "")), today)
            if prog:
                lines.append(f"↳ challenge period {range_emoji} {_format_range(prog.start, prog.end)}")
                lines.append(
                    f"↳ Currently day {prog.day_index} out of {prog.remaining_days} {_days_word(prog.remaining_days)} remaining "
                )
            lines.append("")

        # one consistent separator between sections
        _ensure_blank(lines)

    # -------------------
    # Heroes
    # -------------------
    lines.append("🦸 Heroes")

    if not heroes:
        lines.append("↳ no heroes found")
        _ensure_blank(lines)  # ensure spacing before the next section
    else:
        for ev in heroes:
            name = str(ev.get("name", "")).strip()
            categories = ev.get("category", []) or []
            countries = ev.get("countries", []) or []

            hero, _desc = _split_owner_desc(name)
            hero_emoji = _emoji_for_country(countries)
            status_emoji = _emoji_for_category(categories)

            if hero:
                lines.append(f"{hero_emoji} {hero}".strip())
            # This phrase is intentionally normalized for the 'accept/complete' hero format
            lines.append(f"↳ {status_emoji} Challenge accepted, but not completed".strip())

            prog = _range_progress(str(ev.get("date", "")), today)
            if prog:
                lines.append(
                    f"↳ period {range_emoji} {_format_range(prog.start, prog.end)}"
                )
                lines.append(
                    f"↳  {prog.remaining_days} {_days_word(prog.remaining_days)} "
                    f"(day {prog.day_index} of {prog.total_days})"
                )
            lines.append("")

        # one consistent separator between sections
        _ensure_blank(lines)

    # -------------------
    # Birthdays
    # -------------------
    lines.append(f"{cake} Birthdays")

    if not birthdays:
        lines.append("↳ no birthdays found")
    else:
        for ev in birthdays:
            name = str(ev.get("name", "")).strip()
            if not name:
                continue

            # Birthday JSON can contain either singular or plural fields
            categories = _as_list(ev.get("categories", ev.get("category", [])))
            countries = _as_list(ev.get("countries", ev.get("country", [])))

            # Use *all* provided categories/countries (no de-dup)
            cat_emojis = _emoji_for_categories_all(categories) or "🥳"
            country_emojis = _emoji_for_countries_all(countries)

            # Optional birthday phrase/message (preferred)
            message = (
                str(
                    ev.get("message")
                    or ev.get("text")
                    or ev.get("phrase")
                    or ev.get("msg")
                    or ""
                )
                .strip()
            )

            lines.append(f"{cat_emojis} {name}".strip())

            # Second line: country emojis + message (or country keys as fallback)
            if message:
                lines.append(f"{country_emojis} {message}".strip())
            else:
                # If all tokens were resolved to emojis (e.g. 'murloc'), don't print raw keys like 'murloc'.
                unresolved: List[str] = []
                is_murloc = any(_norm_key(c) == "murloc" for c in countries)

                for c in countries:
                    raw = str(c).strip()
                    k = _norm_token(c)
                    if not raw:
                        continue
                    if k and k not in _COUNTRY_FLAGS_NORM:
                        unresolved.append(raw)

                if unresolved:
                    # Keep unresolved raw keys visible
                    lines.append(" ".join([country_emojis, " ".join(unresolved)]).strip())
                else:
                    # Only emojis (clean)
                    if country_emojis:
                        if is_murloc:
                            lines.append(f"{country_emojis} Mrgl Mrgl!".strip())
                        else:
                            lines.append(country_emojis)
                    else:
                        lines.append(" ".join([str(c).strip() for c in countries if str(c).strip()]))

    # Trim trailing blanks
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)

# ==================================================
# services/holidays_service.py — Holidays Service
# ==================================================
#
# Loads static and dynamic holidays, resolves today's holidays, and returns normalized holiday entries.
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
import logging
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

from core.dynamic_holidays import get_dynamic_holidays

logger = logging.getLogger(__name__)

# ==================================================
# Types & constants
# ==================================================

Holiday = Dict[str, object]

# Root directory containing static holiday JSON files
HOLIDAYS_PATH = Path("data/holidays")

# ==================================================
# Static holidays loader
# ==================================================
#
# Loads holidays defined in static JSON files.
#
# Each JSON entry is expected to contain:
# - name: str
# - date: "MM-DD"
# - countries: list[str] (optional)
# - categories / category: list[str] or str (optional)
#
# Dates are normalized into a full date (parsed_date)
# relative to the provided 'today' value.
#
def load_static_holidays(today: date) -> List[Holiday]:
    """Service function: load static holidays."""
    holidays: List[Holiday] = []

    if not HOLIDAYS_PATH.exists():
        logger.warning("Holidays folder not found: %s", HOLIDAYS_PATH)
        return holidays

    for file in sorted(HOLIDAYS_PATH.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to read %s", file)
            continue

        for entry in data:
            mmdd = entry.get("date")
            if not mmdd:
                continue

            # Build a full date for the current year
            parsed = datetime.strptime(
                f"{today.year}-{mmdd}", "%Y-%m-%d"
            ).date()

            # If the holiday already passed this year,
            # shift it to the next year
            if parsed < today:
                parsed = parsed.replace(year=today.year + 1)

            holidays.append(
                {
                    "name": entry["name"],
                    "date": mmdd,
                    "parsed_date": parsed,
                    "countries": entry.get("countries", []),
                    "categories": (
                        entry.get("category")
                        or entry.get("categories")
                        or []
                    ),
                    "source": file.name,
                }
            )

    return holidays

# ==================================================
# Combined holidays loader
# ==================================================
#
# Loads and merges:
# - static holidays (from JSON files)
# - dynamic holidays (calculated at runtime)
#
# The result is a single, sorted list of holidays.
#
def load_all_holidays(today: date | None = None) -> List[Holiday]:
    """Service function: load all holidays."""
    if today is None:
        today = date.today()

    holidays = load_static_holidays(today)

    # Append dynamically calculated holidays
    for dynamic in get_dynamic_holidays():
        holidays.append(
            {
                "name": dynamic["name"],
                "date": dynamic["date"],
                "parsed_date": datetime.strptime(
                    dynamic["full_date"], "%Y-%m-%d"
                ).date(),
                "countries": dynamic.get("countries", []),
                "categories": dynamic.get("categories", []),
                "source": "dynamic",
            }
        )

    # Sort holidays chronologically
    holidays.sort(key=lambda h: h["parsed_date"])
    return holidays

# ==================================================
# Public API
# ==================================================
#
# Returns only holidays that occur on the given day.
#
def get_today_holidays(today: date | None = None) -> List[Holiday]:
    """Service function: get today holidays."""
    if today is None:
        today = date.today()

    today_mmdd = today.strftime("%m-%d")
    holidays = load_all_holidays(today)

    return [h for h in holidays if h["date"] == today_mmdd]
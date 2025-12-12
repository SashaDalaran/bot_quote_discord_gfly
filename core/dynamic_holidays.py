# ==================================================
# core/dynamic_holidays.py — Dynamic Holiday Generator
# ==================================================

from datetime import datetime, timedelta, date


# ===========================
# Western (Catholic) Easter Calculation
# ===========================
def _easter_western(year: int) -> date:
    """
    Calculate the date of Western (Catholic) Easter
    using the standard Gregorian computus.
    Returns a datetime.date object.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451

    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    return date(year, month, day)


# ===========================
# Orthodox Easter (Approximation)
# ===========================
def _easter_orthodox(year: int) -> date:
    """
    Approximate Orthodox Easter by adding 13 days
    to the Western Easter (Julian vs Gregorian shift).
    This is sufficient for bot-level accuracy.
    """
    western = _easter_western(year)
    return western + timedelta(days=13)


# ===========================
# Public API: Dynamic Holidays
# ===========================
def get_dynamic_holidays() -> list[dict]:
    """
    Return upcoming occurrences of:
      • Catholic Easter
      • Orthodox Easter

    If Easters for the current year have already passed,
    the function automatically shifts calculations to next year.
    """

    today = datetime.now().date()
    year = today.year

    catholic = _easter_western(year)
    orthodox = _easter_orthodox(year)

    # If both holidays are in the past → use next year
    if max(catholic, orthodox) < today:
        year += 1
        catholic = _easter_western(year)
        orthodox = _easter_orthodox(year)

    return [
        {
            "full_date": catholic.strftime("%Y-%m-%d"),
            "date": catholic.strftime("%m-%d"),
            "name": "Catholic Easter",
            "countries": ["catholic"],
            "categories": ["Religious"],
        },
        {
            "full_date": orthodox.strftime("%Y-%m-%d"),
            "date": orthodox.strftime("%m-%d"),
            "name": "Orthodox Easter",
            "countries": ["orthodox"],
            "categories": ["Religious"],
        },
    ]

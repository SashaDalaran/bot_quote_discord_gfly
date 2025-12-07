# core/dynamic_holidays.py
from datetime import datetime, timedelta


def easter_date(year):
    """Return the date of Easter for a given year (Western)."""
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
    return f"{month:02d}-{day:02d}"


def orthodox_easter(year):
    """Orthodox Easter based on Western + 13 days."""
    western = datetime.strptime(easter_date(year), "%m-%d")
    orthodox = western + timedelta(days=13)
    return f"{orthodox.month:02d}-{orthodox.day:02d}"


def get_dynamic_holidays():
    year = datetime.now().year

    easter = easter_date(year)
    orthodox = orthodox_easter(year)

    return [
        {
            "date": easter,
            "name": "Catholic Easter",
            "country": "world",      # 🌍 флаг — универсальный
        },
        {
            "date": orthodox,
            "name": "Orthodox Easter",
            "country": "orthodox",   # использует флаг ✝️
        },
    ]
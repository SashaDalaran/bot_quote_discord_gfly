from datetime import datetime, timedelta

def easter_date(year):
    """Return Catholic Easter date (Western)."""
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
    """Orthodox Easter = Catholic Easter + 13 days (Julian offset)."""
    western = datetime.strptime(easter_date(year), "%m-%d")
    orthodox_dt = western + timedelta(days=13)
    return f"{orthodox_dt.month:02d}-{orthodox_dt.day:02d}"


def ensure_future(mm_dd):
    """Take MM-DD and return the nearest future date (this year or next)."""
    now = datetime.now()
    this_year_date = datetime.strptime(f"{now.year}-{mm_dd}", "%Y-%m-%d")

    if this_year_date >= now:
        return this_year_date
    else:
        return datetime.strptime(f"{now.year + 1}-{mm_dd}", "%Y-%m-%d")


def get_dynamic_holidays():
    year = datetime.now().year

    catholic = ensure_future(easter_date(year))
    orthodox = ensure_future(orthodox_easter(year))

    return [
        {
            "date": catholic.strftime("%Y-%m-%d"),
            "name": "Catholic Easter",
            "country": "catholic",
            "parsed_date": catholic,
        },
        {
            "date": orthodox.strftime("%Y-%m-%d"),
            "name": "Orthodox Easter",
            "country": "orthodox",
            "parsed_date": orthodox,
        },
    ]
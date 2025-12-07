from datetime import datetime, timedelta


def easter_date(year):
    """Return Catholic Easter MM-DD."""
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
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day = (h + l - 7*m + 114) % 31 + 1
    return f"{month:02d}-{day:02d}"


def orthodox_easter(year):
    """Orthodox Easter is Catholic Easter + 13 days."""
    base = datetime.strptime(easter_date(year), "%m-%d")
    shifted = base + timedelta(days=13)
    return f"{shifted.month:02d}-{shifted.day:02d}"


def get_dynamic_holidays():
    now = datetime.now()
    year = now.year

    catholic = easter_date(year)
    orthodox = orthodox_easter(year)

    def normalize_future(mm_dd):
        """Convert MM-DD to the closest upcoming full datetime."""
        dt = datetime.strptime(f"{now.year}-{mm_dd}", "%Y-%m-%d")
        if dt.date() < now.date():
            dt = datetime.strptime(f"{now.year + 1}-{mm_dd}", "%Y-%m-%d")
        return dt

    return [
        {
            "name": "Catholic Easter",
            "date": catholic,                   # MM-DD
            "country": "catholic",
            "parsed_date": normalize_future(catholic)
        },
        {
            "name": "Orthodox Easter",
            "date": orthodox,                   # MM-DD
            "country": "orthodox",
            "parsed_date": normalize_future(orthodox)
        },
    ]
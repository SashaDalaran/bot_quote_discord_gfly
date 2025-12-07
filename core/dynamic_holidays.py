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
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return f"{month:02d}-{day:02d}"


def orthodox_easter(year):
    """Orthodox Easter = Catholic Easter + 13 days."""
    dt = datetime.strptime(easter_date(year), "%m-%d")
    dt = dt + timedelta(days=13)
    return f"{dt.month:02d}-{dt.day:02d}"


def get_dynamic_holidays():
    now = datetime.now()
    year = now.year

    # calculate dates
    catholic = easter_date(year)
    orthodox = orthodox_easter(year)

    def ensure_future(mm_dd):
        """MM-DD → nearest future datetime."""
        dt = datetime.strptime(f"{now.year}-{mm_dd}", "%Y-%m-%d")
        if dt < now:
            dt = datetime.strptime(f"{now.year+1}-{mm_dd}", "%Y-%m-%d")
        return dt

    catholic_dt = ensure_future(catholic)
    orthodox_dt = ensure_future(orthodox)

    return [
        {
            "name": "Catholic Easter",
            "date": catholic,          # MM-DD
            "country": "catholic",
            "parsed_date": catholic_dt
        },
        {
            "name": "Orthodox Easter",
            "date": orthodox,          # MM-DD
            "country": "orthodox",
            "parsed_date": orthodox_dt
        },
    ]
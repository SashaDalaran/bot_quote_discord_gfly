# core/dynamic_holidays.py
from datetime import datetime, timedelta, date


def _easter_western(year: int) -> date:
    """
    Возвращает дату католической Пасхи (григорианский календарь)
    как объект datetime.date.
    Алгоритм — стандартный, только возвращаем date, а не строку.
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


def _easter_orthodox(year: int) -> date:
    """
    Условная дата православной Пасхи:
    берём западную Пасху и добавляем 13 дней (сдвиг юлианского календаря).
    Для нашего бота такой точности более чем достаточно.
    """
    western = _easter_western(year)
    return western + timedelta(days=13)


def get_dynamic_holidays():
    """
    Возвращает список из двух ближайших праздников:
    - Catholic Easter
    - Orthodox Easter

    ВСЕГДА берём **следующую** Пасху (может быть уже в следующем году).
    """
    today = datetime.now().date()
    year = today.year

    # Начально считаем Пасху на этот год
    catholic = _easter_western(year)
    orthodox = _easter_orthodox(year)

    # Если обе Пасхи уже прошли — берём следующий год
    if max(catholic, orthodox) < today:
        year += 1
        catholic = _easter_western(year)
        orthodox = _easter_orthodox(year)

    # Возвращаем в формате, удобном для holidays_cmd:
    # - full_date: YYYY-MM-DD (для точной сортировки)
    # - date: MM-DD (как у JSON-файлов, для отображения)
    return [
        {
            "full_date": catholic.strftime("%Y-%m-%d"),
            "date": catholic.strftime("%m-%d"),
            "name": "Catholic Easter",
            "countries": ["catholic"],
        },
        {
            "full_date": orthodox.strftime("%Y-%m-%d"),
            "date": orthodox.strftime("%m-%d"),
            "name": "Orthodox Easter",
            "countries": ["orthodox"],
        },
    ]
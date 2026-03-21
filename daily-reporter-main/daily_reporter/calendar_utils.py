from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str


def _easter_sunday(year: int) -> date:
    """
    Anonymous Gregorian algorithm (Meeus/Jones/Butcher).
    Valid for Gregorian years (1583+). Good enough for Colombia official holidays.
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


def _next_monday(d: date) -> date:
    return d + timedelta(days=(7 - d.weekday()) % 7)


def colombia_holidays(year: int) -> list[Holiday]:
    """
    Colombia official public holidays approximation:
    - Fixed-date holidays
    - "Ley Emiliani" holidays moved to Monday (Epiphany, St Joseph, etc.)
    - Easter-related holidays (Holy Thursday/Friday, Ascension, Corpus Christi, Sacred Heart)

    Note: This is intentionally self-contained (no external holiday libraries).
    """
    easter = _easter_sunday(year)

    holidays: list[Holiday] = []

    # Fixed-date (some are not moved)
    fixed = [
        (1, 1, "Año Nuevo"),
        (5, 1, "Día del Trabajo"),
        (7, 20, "Independencia de Colombia"),
        (8, 7, "Batalla de Boyacá"),
        (12, 8, "Inmaculada Concepción"),
        (12, 25, "Navidad"),
    ]
    for m, d, name in fixed:
        holidays.append(Holiday(date(year, m, d), name))

    # Easter week
    holidays.append(Holiday(easter - timedelta(days=3), "Jueves Santo"))
    holidays.append(Holiday(easter - timedelta(days=2), "Viernes Santo"))

    # Emiliani-moved holidays (move to next Monday)
    emiliani = [
        (1, 6, "Reyes Magos"),
        (3, 19, "San José"),
        (6, 29, "San Pedro y San Pablo"),
        (8, 15, "Asunción de la Virgen"),
        (10, 12, "Día de la Raza"),
        (11, 1, "Todos los Santos"),
        (11, 11, "Independencia de Cartagena"),
    ]
    for m, d, name in emiliani:
        holidays.append(Holiday(_next_monday(date(year, m, d)), name))

    # Easter-related, moved to Monday
    holidays.append(Holiday(_next_monday(easter + timedelta(days=39)), "Ascensión del Señor"))
    holidays.append(Holiday(_next_monday(easter + timedelta(days=60)), "Corpus Christi"))
    holidays.append(Holiday(_next_monday(easter + timedelta(days=68)), "Sagrado Corazón"))

    # Deduplicate (in case of edge collisions), keep first name
    seen: set[date] = set()
    out: list[Holiday] = []
    for h in sorted(holidays, key=lambda x: x.day):
        if h.day in seen:
            continue
        seen.add(h.day)
        out.append(h)
    return out


def is_business_day_colombia(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    year_holidays = {h.day for h in colombia_holidays(d.year)}
    return d not in year_holidays


def business_day_reason(d: date) -> str | None:
    if d.weekday() == 5:
        return "Saturday"
    if d.weekday() == 6:
        return "Sunday"
    for h in colombia_holidays(d.year):
        if h.day == d:
            return f"Holiday: {h.name}"
    return None



"""Quarterly windows in publication-year convention: Q1 = Dec-Feb, Q2 = Mar-May, Q3 = Jun-Aug, Q4 = Sep-Nov."""
from __future__ import annotations

import calendar
import re
from datetime import date


def window(quarter: str) -> tuple[date, date]:
    if not re.fullmatch(r"\d{4}-Q[1-4]", quarter):
        raise ValueError("Expected YYYY-QN")
    year, q = int(quarter[:4]), int(quarter[-1])
    if q == 1:
        return date(year - 1, 12, 1), date(year, 2, calendar.monthrange(year, 2)[1])
    first = 3 * q - 3
    last = first + 2
    return date(year, first, 1), date(year, last, calendar.monthrange(year, last)[1])


def label(quarter: str) -> str:
    start, end = window(quarter)
    return f"{start:%b %Y} – {end:%b %Y}"


def current(today: date | None = None) -> str:
    today = today or date.today()
    year = today.year + 1 if today.month == 12 else today.year
    return f"{year}-Q{(today.month % 12) // 3 + 1}"

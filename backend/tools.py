from langchain.tools import tool
from datetime import datetime, timedelta, timezone
import calendar
from typing import Dict
from util import make_api_call

@tool
def get_supported_pollsters():
    """Get the pollsters that are supported and available"""
    return make_api_call("https://api.votehub.com/pollsters")

@tool
def get_supported_poll_types():
    """Get the poll types that are supported and available"""
    return make_api_call("https://api.votehub.com/poll-types")

@tool
def get_poll_subjects():
    """Get a list of subjects with their associated poll types, including covered races, approvals, favorabilities, and generic ballot. This shows which subjects can be used with different poll types."""
    return make_api_call("https://api.votehub.com/subjects")

@tool
def date_n_units_ago(n: int, unit: str) -> str:
    """
    Calculate the date n units ago from today.
    Args:
        n (int): number of units ago
        unit (str): one of "day", "week", "month", or "year"
    Returns:
        str: date in YYYY-MM-DD format
    """
    today = datetime.now(timezone.utc)
    if unit == "day":
        result = today - timedelta(days=n)
    elif unit == "week":
        result = today - timedelta(weeks=n)
    elif unit == "month":
        # If today is 31st and target month doesn't have 31, fallback to last day of target month
        year = today.year
        month = today.month - n
        while month <= 0:
            month += 12
            year -= 1
        day = today.day
        # Calculate last day in the target month
        last_day = 28
        for d in (31, 30, 29, 28):
            try:
                datetime(year, month, d)
                last_day = d
                break
            except ValueError:
                continue
        if day > last_day:
            day = last_day
        result = datetime(year, month, day).date()
    elif unit == "year":
        year = today.year - n
        month = today.month
        day = today.day
        # Handle leap year case (Feb 29)
        try:
            result = datetime(year, month, day).date()
        except ValueError:
            # fallback to Feb 28 if not a leap year
            result = datetime(year, month, 28).date()
    else:
        raise ValueError("Unit must be one of: 'day', 'week', 'month', 'year'.")
    return result.strftime("%Y-%m-%d")

@tool
def get_month_range_by_name(month_name: str) -> Dict[str, str]:
    """
    Calculate the beginning and end dates of the next, current, or past named month relative to today.

    Args:
        month_name (str): Name of the month (e.g., "January", "Feb", "March", etc., case-insensitive).

    Returns:
        dict: {
            "start_date": str (YYYY-MM-DD, first day of that month in this year or prior/next year),
            "end_date": str (YYYY-MM-DD, last day of that month in this year or prior/next year)
        }

    The month returned is the most recent occurrence of the named month that is on or before today, 
    unless that month is the current month, in which case it uses the current year.
    """

    today = datetime.now(timezone.utc)
    month_name = month_name.strip().lower()

    # Map input to month number, supports abbreviations and full names
    month_lookup = {month.lower(): i for i, month in enumerate(calendar.month_name) if month}
    month_abbr_lookup = {month.lower(): i for i, month in enumerate(calendar.month_abbr) if month}
    lookup = {**month_lookup, **month_abbr_lookup}

    if month_name not in lookup:
        raise ValueError(f"Invalid month name: '{month_name}'")

    month_num = lookup[month_name]

    # Figure out which year to use: most recent occurrence of that month (<= today)
    if today.month < month_num:
        year = today.year - 1
    else:
        year = today.year

    start_date = datetime(year, month_num, 1).date()

    # Figure out the last valid day in the month
    if month_num == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month_num + 1
        next_year = year

    first_of_next_month = datetime(next_year, next_month, 1).date()
    last_date = first_of_next_month - timedelta(days=1)

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": last_date.strftime("%Y-%m-%d")
    }

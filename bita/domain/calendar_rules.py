import pandas as pd
from datetime import date
from ..dtos import CalendarRule, CalendarRuleType


def get_calendar_dates(rule: CalendarRule) -> pd.DatetimeIndex:
    """
    Generate calendar dates based on the provided rule.

    Args:
        rule: Calendar rule configuration

    Returns:
        DatetimeIndex of dates for portfolio review
    """
    if rule.type_ == CalendarRuleType.CUSTOM_DATES:
        return pd.DatetimeIndex(rule.dates)

    max_date = date(2025, 1, 22)
    return pd.date_range(
        start=rule.initial_date,
        end=max_date,
        freq="Q"
    )

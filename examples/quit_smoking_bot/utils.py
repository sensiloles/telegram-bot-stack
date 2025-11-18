"""Utility functions for Quit Smoking Bot."""

import datetime

# Handle both package and direct execution imports
try:
    from config import MAX_PRIZE_FUND, MONTHLY_AMOUNT, PRIZE_FUND_INCREASE
except ImportError:
    from .config import MAX_PRIZE_FUND, MONTHLY_AMOUNT, PRIZE_FUND_INCREASE


def calculate_period(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
) -> tuple[int, int, int]:
    """Calculate years, months and days between two dates.

    Args:
        start_date: Starting datetime
        end_date: Ending datetime

    Returns:
        Tuple of (years, months, days)
    """
    years = end_date.year - start_date.year
    months = end_date.month - start_date.month
    days = end_date.day - start_date.day

    if days < 0:
        # Borrow from months
        months -= 1
        # Add days from previous month
        last_day = (end_date.replace(day=1) - datetime.timedelta(days=1)).day
        days += last_day

    if months < 0:
        # Borrow from years
        years -= 1
        months += 12

    return years, months, days


def calculate_prize_fund(months: int) -> int:
    """Calculate the prize fund based on the number of months.

    Prize fund increases by PRIZE_FUND_INCREASE each month,
    starting from MONTHLY_AMOUNT, up to MAX_PRIZE_FUND.

    Args:
        months: Number of months elapsed

    Returns:
        Prize fund amount in rubles
    """
    if months < 0:
        return 0

    prize_fund = MONTHLY_AMOUNT + (months * PRIZE_FUND_INCREASE)
    return min(prize_fund, MAX_PRIZE_FUND)

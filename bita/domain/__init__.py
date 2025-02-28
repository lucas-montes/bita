import pandas as pd
from pathlib import Path
import time
from datetime import date
from ..dtos import (
    BacktestRequest,
    BacktestResponse,
    CalendarRule,
    CalendarRuleType,
    BacktestFilter,
    FilterType,
)

from .weighting import calculate_weights


def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest based on the provided configuration.

    Args:
        request: Backtest configuration

    Returns:
        Backtest results
    """
    start_time = time.perf_counter()

    calendar_dates = _get_calendar_dates(request.calendar_rule)
    df_filter = _read_parquet(request.backtest_filter.d.value)
    securities_filtered = _apply_filter(request.backtest_filter, df_filter, calendar_dates)

    if not securities_filtered.empty:
        df_weights = _read_parquet(request.weighting_method.d.value)
        weights_by_date = calculate_weights(
            request.weighting_method,
            securities_filtered.columns,
            df_weights,
            calendar_dates,
        )

    execution_time = time.perf_counter() - start_time

    return BacktestResponse(execution_time=execution_time, weights=weights_by_date)


def _read_parquet(path: str) -> pd.DataFrame:
    project_root = Path(__file__).resolve().parent.parent.parent
    file_path = project_root / "data" / f"{path}.parquet"
    return pd.read_parquet(file_path)


def _get_calendar_dates(rule: CalendarRule) -> pd.DatetimeIndex:
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
    return pd.date_range(start=rule.initial_date, end=max_date, freq="QE")


def _apply_filter(
    filter_config: BacktestFilter,
    data: pd.DataFrame,
    dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """
    Apply filter to select securities based on the filter configuration.

    Args:
        filter_config: Filter configuration
        data: DataFrame containing the data field values
        dates: Dates to filter on

    Returns:
        DataFrame of selected securities
    """
    current_data = data.loc[dates]
    if filter_config.type_ == FilterType.TOP_N:
        return (
            current_data.transpose()
            .nlargest(filter_config.n, current_data.index)
            .transpose()
        )

    return current_data.where(current_data > filter_config.p).dropna(axis=1)

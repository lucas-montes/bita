import pandas as pd
from pathlib import Path
import time
from .dtos import (
    BacktestRequest,
    BacktestResponse
)
from .application import WeightingMethod

def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest based on the provided configuration.

    Args:
        request: Backtest configuration

    Returns:
        Backtest results
    """
    start_time = time.perf_counter()

    calendar_dates = request.calendar_rule.get_dates()
    df_filter = _read_parquet(request.backtest_filter.d.value).loc[calendar_dates]
    securities_filtered = request.backtest_filter.apply_filter(df_filter)

    try:
        #NOTE: If this often happens a if statement would be better
        df_weights = _read_parquet(request.weighting_method.d.value)
        weights_by_date = _calculate_weights(
            request.weighting_method,
            securities_filtered.columns,
            df_weights,
            securities_filtered.index,
        ).to_dict("index")
    except ZeroDivisionError:
        weights_by_date = {}

    execution_time = time.perf_counter() - start_time

    return BacktestResponse(execution_time=execution_time, weights=weights_by_date)


def _read_parquet(path: str) -> pd.DataFrame:
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / f"{path}.parquet"
    return pd.read_parquet(file_path)

def _calculate_weights(
    weighting_method: WeightingMethod,
    securities: pd.Index,
    data: pd.DataFrame,
    dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """
    Calculate weights for the selected securities based on the weighting method.

    Args:
        weighting_method: Weighting method configuration
        securities: List of selected security IDs
        data: Data frame containing the data field values
        dates: Current date to calculate weights for|

    Returns:
        DataFrame with securities weights
    """
    df = data.loc[dates].filter(securities)
    if weighting_method.empty_bounds():
        df[:] = 1 / len(securities)
        return df

    return _calculate_optimized_weights(df, weighting_method.lb, weighting_method.ub)


def _calculate_row_weight(df_row: pd.Series, lb: float, ub: float)-> pd.Series:
    n = len(df_row)

    sorted_series = df_row.sort_values(ascending=False)

    weights = pd.Series(lb, index=sorted_series.index)

    remaining_weight = 1.0 - (n * lb)

    max_additional = ub - lb

    num_max_weight = min(n, int(remaining_weight / max_additional))

    if num_max_weight > 0:
        weights.iloc[:num_max_weight] += max_additional
        remaining_weight -= num_max_weight * max_additional

    if remaining_weight > 0 and num_max_weight < n:
        weights.iloc[num_max_weight] += remaining_weight

    return weights


def _calculate_optimized_weights(data: pd.DataFrame, lb: float, ub: float)-> pd.DataFrame:
    return data.apply(_calculate_row_weight, lb=lb, ub=ub, axis=1)

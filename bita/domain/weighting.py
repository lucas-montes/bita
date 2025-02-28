import pandas as pd
from bita.dtos import WeightingMethod, WeightingMethodType


def calculate_weights(
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
    df = data.filter(securities)
    if weighting_method.type_ == WeightingMethodType.EQUAL_WEIGHT:
        df[:] = 1 / len(securities)
        return df

    return _calculate_optimized_weights(df, weighting_method.lb, weighting_method.ub)


def _calculate_row_weight(df_row, lb, ub):
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


def _calculate_optimized_weights(data: pd.DataFrame, lb, ub):
    return data.apply(_calculate_row_weight, lb=lb, ub=ub, axis=1)

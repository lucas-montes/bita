import pandas as pd
from bita.dtos import BacktestFilter, FilterType


def apply_filter(
    filter_config: BacktestFilter,
    data: pd.DataFrame,
    dates: pd.DatetimeIndex
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
        return current_data.transpose().nlargest(filter_config.n, current_data.index).transpose()

    return current_data.where(current_data > filter_config.p).dropna(axis=1)

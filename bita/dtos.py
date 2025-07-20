from datetime import date

from pydantic import BaseModel

from .application import (
    BacktestFilterLowerThanP,
    BacktestFilterTopN,
    CustomDatesRule,
    QuarterlyDatesRule,
    WeightingMethod,
)


class BacktestRequest(BaseModel):
    calendar_rule: CustomDatesRule | QuarterlyDatesRule
    backtest_filter: BacktestFilterTopN | BacktestFilterLowerThanP
    weighting_method: WeightingMethod


class BacktestResponse(BaseModel):
    execution_time: float
    weights: dict[date, dict[str, float]]

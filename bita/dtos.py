from pydantic import BaseModel
from datetime import date

from .application import WeightingMethod, CustomDatesRule, QuarterlyDatesRule, BacktestFilterTopN, BacktestFilterLowerThanP


class BacktestRequest(BaseModel):
    calendar_rule: CustomDatesRule | QuarterlyDatesRule
    backtest_filter: BacktestFilterTopN | BacktestFilterLowerThanP
    weighting_method: WeightingMethod


class BacktestResponse(BaseModel):
    execution_time: float
    weights: dict[date, dict[str, float]]

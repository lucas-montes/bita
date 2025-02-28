from pydantic import BaseModel, Field, field_validator
from datetime import date
from enum import Enum


class CalendarRuleType(str, Enum):
    CUSTOM_DATES = "custom_dates"
    QUARTERLY_DATES = "quarterly_dates"


class FilterType(str, Enum):
    TOP_N = "top_n"
    FILTER_BY_VALUE = "filter_by_value"


class SecurityValue(str, Enum):
    MARKET_CAP = "market_capitalization"
    VOLUME = "volume"
    PRICES = "prices"
    ADTV = "adtv_3_motnhs"


class WeightingMethodType(str, Enum):
    EQUAL_WEIGHT = "equal_weight"
    OPTIMIZED_WEIGHT = "optimized_weight"


class CalendarRule(BaseModel):
    type_: CalendarRuleType
    dates: list[date] = []
    initial_date: date | None = None


class BacktestFilter(BaseModel):
    type_: FilterType
    n: int | None = Field(default=None, gt=0)
    p: float | None = Field(default=None, gt=0)
    d: SecurityValue


class WeightingMethod(BaseModel):
    type_: WeightingMethodType
    lb: float | None = Field(default=None, gt=0)
    ub: float | None = Field(default=None, gt=0)
    d: SecurityValue


class BacktestRequest(BaseModel):
    calendar_rule: CalendarRule
    backtest_filter: BacktestFilter
    weighting_method: WeightingMethod


class BacktestResponse(BaseModel):
    execution_time: float
    weights: dict[date, dict[str, float]]

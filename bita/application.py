from pydantic import BaseModel, Field, field_validator
from datetime import date
from enum import Enum
import pandas as pd

class SecurityValue(str, Enum):
    MARKET_CAP = "market_capitalization"
    VOLUME = "volume"
    PRICES = "prices"
    ADTV = "adtv_3_motnhs"


class WeightingMethod(BaseModel):
    lb: float | None = Field(default=None, gt=0)
    ub: float | None = Field(default=None, gt=0)
    d: SecurityValue

    def empty_bounds(self)->bool:
        return self.lb is None and self.ub is None


class AbstractBacktestFilter(BaseModel):
    d: SecurityValue

    def apply_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class BacktestFilterTopN(AbstractBacktestFilter):
    n: int = Field(gt=0)

    def apply_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        return (
            data.transpose()
            .nlargest(self.n, data.index)
            .transpose()
        )


class BacktestFilterLowerThanP(AbstractBacktestFilter):
    p: float = Field(gt=0)

    def apply_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.where(data > self.p).dropna(axis=1)


class AbstractDateFactory(BaseModel):
    def get_dates(self) -> pd.DatetimeIndex:
        raise NotImplementedError


class CustomDatesRule(AbstractDateFactory):
    dates: list[date]

    @field_validator("dates")
    def validate_zones(cls, v) -> list[date]:
        if not v:
            raise ValueError("dates cannot be empty")
        return v

    def get_dates(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.dates)


class QuarterlyDatesRule(AbstractDateFactory):
    initial_date: date

    def get_dates(self) -> pd.DatetimeIndex:
        max_date = date(2025, 1, 22)
        return pd.date_range(start=self.initial_date, end=max_date, freq="QE")

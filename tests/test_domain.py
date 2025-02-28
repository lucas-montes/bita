import pandas as pd
from pandas.testing import assert_index_equal, assert_frame_equal

from bita import domain
from bita.dtos import CalendarRule, BacktestFilter, WeightingMethod


def test_calendar_rule_custom_dates():
    rules = CalendarRule(
        dates=["2024-01-01", "2024-01-15", "2024-02-01"], type_="custom_dates"
    )
    result = domain._get_calendar_dates(rules)
    expected = pd.DatetimeIndex(["2024-01-01", "2024-01-15", "2024-02-01"])
    assert_index_equal(result, expected)


def test_calendar_rule_quarterly_dates():
    rules = CalendarRule(initial_date="2024-01-01", type_="quarterly_dates")
    result = domain._get_calendar_dates(rules)
    expected = pd.DatetimeIndex(
        ["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31"]
    )
    assert_index_equal(result, expected)


def test_filter_top():
    values = {
        "0": [95.036355, 4.731177, 13.964960],
        "1": [31.936291, 18.733920, 21.162002],
        "2": [29.631908, 46.853490, 76.815065],
        "3": [42.654515, 66.993398, 73.648067],
    }
    index = pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01"])
    data = pd.DataFrame(values, index=index)
    filter_config = BacktestFilter(type_="top_n", n=2, d="prices")
    result = domain._apply_filter(
        filter_config,
        data,
        pd.to_datetime(["2024-01-01", "2024-01-15"]),
    )
    expected = pd.DataFrame.from_dict(
        {
            pd.Timestamp("2024-01-01 00:00:00"): {"0": 95.036355, "3": 42.654515},
            pd.Timestamp("2024-01-15 00:00:00"): {"0": 4.731177, "3": 66.993398},
        },
        orient="index",
    )

    assert_frame_equal(result, expected)


def test_filter_greater():
    values = {
        "0": [95.036355, 4.731177, 13.964960],
        "1": [31.936291, 18.733920, 21.162002],
        "2": [29.631908, 46.853490, 76.815065],
        "3": [42.654515, 66.993398, 73.648067],
    }
    index = pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01"])
    data = pd.DataFrame(values, index=index)
    filter_config = BacktestFilter(type_="filter_by_value", p=19.0, d="prices")
    result = domain._apply_filter(
        filter_config,
        data,
        pd.to_datetime(["2024-01-01", "2024-01-15"]),
    )
    expected = pd.DataFrame.from_dict(
        {
            pd.Timestamp("2024-01-01 00:00:00"): {"2": 29.631908, "3": 42.654515},
            pd.Timestamp("2024-01-15 00:00:00"): {"2": 46.85349, "3": 66.993398},
        },
        orient="index",
    )

    assert_frame_equal(result, expected)


def test_weighting_method_equal_weight():
    config = WeightingMethod(type_="equal_weight", d="prices")
    values = {
        "0": [95.036355, 4.731177, 13.964960],
        "1": [31.936291, 18.733920, 21.162002],
        "2": [29.631908, 46.853490, 76.815065],
        "3": [42.654515, 66.993398, 73.648067],
    }
    index = pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01"])
    data = pd.DataFrame(values, index=index)
    securities = pd.Index(["0", "1", "2"])
    dates = pd.DatetimeIndex(["2024-01-01", "2024-01-15"])
    result = domain.weighting.calculate_weights(config, securities, data, dates)

    expected = pd.DataFrame.from_dict(
        {
            pd.Timestamp("2024-01-01 00:00:00"): {
                "0": 0.3333333333333333,
                "1": 0.3333333333333333,
                "2": 0.3333333333333333,
            },
            pd.Timestamp("2024-01-15 00:00:00"): {
                "0": 0.3333333333333333,
                "1": 0.3333333333333333,
                "2": 0.3333333333333333,
            },
            pd.Timestamp("2024-02-01 00:00:00"): {
                "0": 0.3333333333333333,
                "1": 0.3333333333333333,
                "2": 0.3333333333333333,
            },
        },
        orient="index",
    )
    assert_frame_equal(result, expected)


def test_calculate_optimized_weights():
    values = {
        "0": [95.036355, 4.731177, 13.964960],
        "1": [31.936291, 18.733920, 21.162002],
        "2": [29.631908, 46.853490, 76.815065],
        "3": [42.654515, 66.993398, 73.648067],
    }
    index = pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01"])
    data = pd.DataFrame(values, index=index)
    securities = pd.Index(["1", "2", "3"])

    result = domain.weighting._calculate_optimized_weights(data[securities], lb=0.1, ub=0.5)

    expected = pd.DataFrame.from_dict(
        {
            pd.Timestamp("2024-01-01 00:00:00"): {
                "1": 0.3999999999999999,
                "2": 0.1,
                "3": 0.5,
            },
            pd.Timestamp("2024-01-15 00:00:00"): {
                "1": 0.1,
                "2": 0.3999999999999999,
                "3": 0.5,
            },
            pd.Timestamp("2024-02-01 00:00:00"): {
                "1": 0.1,
                "2": 0.5,
                "3": 0.3999999999999999,
            },
        },
        orient="index",
    )
    assert_frame_equal(result, expected)

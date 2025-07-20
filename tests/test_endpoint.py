from fastapi.testclient import TestClient

from bita import app

client = TestClient(app)


def test_empty_dates():
    payload = {
        "calendar_rule": {"dates": []},
        "backtest_filter": {"n": 5, "d": "market_capitalization"},
        "weighting_method": {
            "d": "volume",
        },
    }

    response = client.post("/backtest", json=payload)
    assert response.status_code == 422


def test_custom_dates_equal_weight():
    payload = {
        "calendar_rule": {"dates": ["2024-01-01", "2024-01-15", "2024-02-01"]},
        "backtest_filter": {"n": 5, "d": "market_capitalization"},
        "weighting_method": {
            "d": "volume",
        },
    }

    response = client.post("/backtest", json=payload)
    assert response.status_code == 200


def test_quarterly_dates_optimized_weight():
    payload = {
        "calendar_rule": {"initial_date": "2024-01-01"},
        "backtest_filter": {"p": 50.0, "d": "prices"},
        "weighting_method": {"d": "volume", "lb": 0.05, "ub": 0.4},
    }

    response = client.post("/backtest", json=payload)
    assert response.status_code == 200

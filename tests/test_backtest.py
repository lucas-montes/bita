from fastapi.testclient import TestClient
from bita import app


client = TestClient(app)


def test_custom_dates_equal_weight():
    """Test backtest with custom dates and equal weight."""
    payload = {
        "calendar_rule": {
            "type": "custom_dates",
            "dates": ["2024-01-01", "2024-01-15", "2024-02-01"]
        },
        "filter": {
            "type": "top_n",
            "n": 5,
            "data_field": "market_capitalization"
        },
        "weighting_method": {
            "type": "equal_weight"
        },
    }

    response = client.post("/backtest", json=payload)
    assert response.status_code == 200


def test_quarterly_dates_optimized_weight():
    """Test backtest with quarterly dates and optimized weight."""
    payload = {
        "calendar_rule": {
            "type": "quarterly_dates",
            "initial_date": "2024-01-01"
        },
        "filter": {
            "type": "filter_by_value",
            "p": 50.0,
            "data_field": "prices"
        },
        "weighting_method": {
            "type": "optimized_weight",
            "data_field": "volume",
            "lb": 0.05,
            "ub": 0.4
        },
    }

    response = client.post("/backtest", json=payload)
    assert response.status_code == 200

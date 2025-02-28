from fastapi import FastAPI, HTTPException
from bita.dtos import BacktestRequest, BacktestResponse
from bita.domain import run_backtest
import time

app = FastAPI(
    title="Bitacore Mini",
    description="A miniature backtesting API for financial portfolios",
    version="1.0.0"
)


@app.post("/backtest", response_model=BacktestResponse)
async def backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest with the provided configuration.

    The backtest will:
    1. Generate calendar dates based on the specified calendar rule
    2. Filter securities at each date based on the filter configuration
    3. Calculate weights for the selected securities using the specified weighting method

    Returns:
        BacktestResponse: Contains execution time and calculated weights for each date
    """
    try:
        return run_backtest(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"timestamp": time.time()}

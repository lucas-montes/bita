# Bitacore Mini - Backtesting API

Bitacore Mini is a platform for running backtests of financial indices using custom rules through a modern API. It allows you to:
- Generate synthetic financial data for testing
- Define custom portfolio selection and weighting rules
- Run backtests and retrieve portfolio weights for each date
- Benchmark and load-test the API

## How It Works

### Data Model
All data fields are stored in Parquet files as matrices:
- **Index:** Each row is a date (market close)
- **Columns:** Each column is a security (unique string ID)
- **Values:** Each cell is the value for a security on a date (e.g., price, volume)

The API expects the following Parquet files in the `data/` directory:
- `market_capitalization.parquet`
- `prices.parquet`
- `volume.parquet`
- `adtv_3_month.parquet`

### Backtest Flow
1. **Portfolio Creation:**
   - Select securities for the portfolio using generic filters (e.g., top N, threshold)
   - Portfolio is reviewed on a schedule (calendar rule)
2. **Weighting:**
   - Assign weights to each security (equal or optimized)
   - Weights sum to 100% per date


### API Endpoints
- `POST /backtest`: Run a backtest with custom rules and get weights per date
- `GET /health`: Health check endpoint

API docs are available at [localhost:8000/docs](http://localhost:8000/docs)

---

## Getting Started

### Installation Methods

#### 1. Python (Recommended for Development)

```bash
# Clone the repository
$ git clone https://github.com/lucas-montes/bita.git
$ cd bita

# Install dependencies (editable mode)
$ pip install -e .[dev]

# Generate test data
$ python generate-data.py --path ./data --num_securities 1000
```

#### 2. Docker

```bash
# Build and run the API
$ docker compose up --build

# The API will be available at http://localhost:8000
```

#### 3. Nix (Reproducible Dev Environment)
Enter a Nix shell with all dependencies
```bash
nix develop
```

Generate test data
```bash
python generate-data.py --path ./data --num_securities 1000
```

---

## Running the API

### Development Server
```bash
fastapi dev bita
```

### Production Server (Docker Compose)
```bash
docker compose up --build
```

---

## Running Tests

### Unit Tests

From the project root
```bash
PYTHONPATH=$(pwd) pytest
```

Or, if installed
```bash
pytest
```

### Simulation/Load Testing
```bash
locust
```

---

## Linting, Formatting, and Type Checking

### Lint with Ruff
```bash
ruff check .
```

### Format with Ruff
```bash
ruff format .
```

### Type Check with mypy
```bash
mypy bita
```

---

## Project Structure

- `generate-data.py`: Script to generate synthetic Parquet data
- `bita/`: Main package with API, domain logic, and DTOs
- `tests/`: Unit and integration tests
- `data/`: Parquet files for backtesting (generated or mounted)
- `Dockerfile`, `docker-compose.yaml`: Containerization and orchestration
- `locustfile.py`, `locust_helpers.py`: Load testing with Locust

---

## CI/CD

A GitHub Actions workflow is provided in `.github/workflows/ci.yml` to run linting, type checking, and tests on every push and pull request.

---

## Notes
- Uses `pyarrow` backend for performance
- Data files must exist in `data/` before running the API
- See API docs at [localhost:8000/docs](http://localhost:8000/docs)
- For benchmarking, see `memray` and `pytest-benchmark` in dev dependencies

---

# Bitacore Mini - Backtesting API

## Notes
1. Using the pyarrow backend can drive some perf improvements
2. Reading the files with pyarrow instead of pandas can allow to do some predicate pushdown
3. Memray or pytest-benchmark could be used in tests to have better restrictions memory and performance wise
4. Business should have used behave for the specifications 
5. If we have multiple cores we could use an processpool to execute the blocking functions

## Getting Started

### Installation

#### Using Python

1. Clone the repository:
   ```bash
   git clone https://github.com/lucas-montes/bita.git
   cd bita
   ```

2. Install dependencies:
  If you don't use nix and direnv
   ```bash
   pip install -r requirements.txt
   ```

3. Generate test data:
   ```bash
   python generate_data.py --path ./data --num_securities 1000
   ```

4. Run the server:
   ```bash
   fastapi dev bita
   ```

#### Using Docker

Build and run with Docker:
```bash
docker compose up --build
```

### API Usage
You can find the docs at:
```
localhost:8000/docs
```

### Running Tests

You can either use
```bash
PYTHONPATH=$(pwd) pytest
```

Or install the app an run
```bash
pytest
```

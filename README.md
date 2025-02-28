# Bitacore Mini - Backtesting API

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

1. Build and run with Docker:
   ```bash
   docker build -t bita .
   docker run -p 8000:8000 -v $(pwd)/data:/app/data bita
   ```

### API Usage
You can find the docs at:
```
localhost:8000/docs
```

### Running Tests

If you use nix
```bash
PYTHONPATH=$(pwd) pytest tests/test_services.py
```

Otherwise
´´´bash
pytest
´´´

import pandas as pd
import numpy as np
import os
import argparse

def generate_data(path, num_securities=1000):
    """
    Generate dummy data for testing the backtesting API.

    Args:
        path: Path to save the Parquet files
        num_securities: Number of securities to generate
    """

    os.makedirs(path, exist_ok=True)

    data_field_identifiers = [
        "market_capitalization",
        "prices",
        "volume",
        "adtv_3_month"
    ]

    securities = list(map(str, range(num_securities)))

    dates = pd.date_range("2020-01-01", "2025-01-22")

    for data_field_identifier in data_field_identifiers:
        print(f"Generating {data_field_identifier} data...")

        data = np.random.uniform(low=1, high=100, size=(len(dates), len(securities)))

        df = pd.DataFrame(
            data,
            index=dates,
            columns=securities
        )

        file_path = os.path.join(path, f"{data_field_identifier}.parquet")
        df.to_parquet(file_path)
        print(f"Saved {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dummy data for backtesting")
    parser.add_argument("--path", type=str, default="./data", help="Path to save the Parquet files")
    parser.add_argument("--num_securities", type=int, default=1000, help="Number of securities to generate")

    args = parser.parse_args()
    generate_data(args.path, args.num_securities)

    print("Data generation complete!")

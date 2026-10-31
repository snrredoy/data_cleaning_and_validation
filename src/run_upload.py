
from pathlib import Path

import pandas as pd

from src.database import insert_customers

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "output" / "valid_customers.csv"


def main():
    df = pd.read_csv(INPUT_FILE, dtype="string")

    result = insert_customers(df, batch_size=2)

    print("Customer upload completed.")
    print(f"Inserted: {result['inserted']}")
    print(f"Updated: {result['updated']}")
    print(f"Unchanged: {result['unchanged']}")


if __name__ == "__main__":
    main()

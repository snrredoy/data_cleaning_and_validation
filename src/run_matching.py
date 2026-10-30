from pathlib import Path

import pandas as pd

from src.matching import cross_match

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BASE_DIR / "output" / "valid_customers.csv"
REFERENCE_FILE = BASE_DIR / "data" / "raw" / "customers_reference.csv"
OUTPUT_DIR = BASE_DIR / "output" / "comparison_reports"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_df = pd.read_csv(SOURCE_FILE, dtype="string")
    reference_df = pd.read_csv(REFERENCE_FILE, dtype="string")

    matched, unmatched, discrepancies = cross_match(
        source_df,
        reference_df,
    )

    matched.to_csv(OUTPUT_DIR / "matched_records.csv", index=False)
    unmatched.to_csv(OUTPUT_DIR / "unmatched_records.csv", index=False)
    discrepancies.to_csv(
        OUTPUT_DIR / "discrepancy_report.csv",
        index=False,
    )

    print("Cross-matching completed.")
    print(f"Matched records: {len(matched)}")
    print(f"Unmatched records: {len(unmatched)}")
    print(f"Discrepancies: {len(discrepancies)}")
    print(f"Reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

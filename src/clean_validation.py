import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "customers.csv"
OUTPUT_DIR = BASE_DIR / "output"

REQUIRED_COLUMNS = {"customer_id", "name", "email", "city"}

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$"
)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    df["email"] = df["email"].str.lower()
    df["customer_id"] = df["customer_id"].str.upper()

    return df


def validate_data(df: pd.DataFrame) -> pd.Series:
    errors = pd.Series("", index=df.index, dtype="string")

    def add_error(mask, message):
        mask = mask.fillna(False)
        errors.loc[mask] = errors.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    for col in REQUIRED_COLUMNS:
        missing = df[col].isna() | df[col].eq("")
        add_error(missing, f"Missing value in '{col}'")

    valid_ids = df["customer_id"].notna() & df["customer_id"].ne("")
    duplicate_ids = valid_ids & df["customer_id"].duplicated(keep=False)
    add_error(duplicate_ids, "Duplicate customer ID")

    email_ok = df["email"].str.fullmatch(EMAIL_PATTERN, na=False)
    add_error(~email_ok, "Invalid email format")

    return errors


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_FILE, dtype=str)

    df = clean_column_names(df)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = df.reset_index(drop=True)
    df.insert(0, "source_row", range(2, len(df) + 2))

    df = clean_text(df)

    df["validation_errors"] = validate_data(df)

    valid_mask = df["validation_errors"].eq("")
    valid_records = df.loc[valid_mask].copy()
    rejected_records = df.loc[~valid_mask].copy()

    valid_records.drop(columns=["validation_errors"]).to_csv(
        OUTPUT_DIR / "valid_customers.csv", index=False
    )

    rejected_records.to_csv(OUTPUT_DIR / "rejected_customers.csv", index=False)

    summary = pd.DataFrame(
        [
            {"metric": "Total records", "count": len(df)},
            {"metric": "Valid records", "count": len(valid_records)},
            {"metric": "Rejected records", "count": len(rejected_records)},
        ]
    )

    summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)

    print("Data cleaning and validation completed.")
    print(f"Summary: {summary.to_string(index=False)}")
    print(f"Report saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

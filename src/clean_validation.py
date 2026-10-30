import re
from pathlib import Path

import pandas as pd

from src.readers import read_input, read_excel_sheets
from src.rules import load_rules

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "customers_multi_sheet.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

rules = load_rules()
REQUIRED_COLUMNS = set(rules["required_columns"])
UNIQUE_COLUMNS = set(rules["unique_columns"])
NORMALIZE = rules["normalize"]

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$"
)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    return df


def clean_text(df: pd.DataFrame, normalize: dict[str, bool]) -> pd.DataFrame:
    df = df.copy()

    if normalize.get("trim_whitespace", True):
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)

    if normalize.get("lowercase_email", True):
        if "email" in df.columns:
            df["email"] = df["email"].str.lower()

    if normalize.get("uppercase_customer_id", True):
        if "customer_id" in df.columns:
            df["customer_id"] = df["customer_id"].str.upper()

    return df


def validate_data(df: pd.DataFrame, rules: dict) -> pd.Series:
    errors = pd.Series("", index=df.index, dtype="string")

    def add_error(mask, message):
        mask = mask.fillna(False)
        errors.loc[mask] = errors.loc[mask].apply(lambda old: f"{old}; {message}" if old else message)

    for col in REQUIRED_COLUMNS:
        missing = df[col].isna() | df[col].eq("")
        add_error(missing, f"Missing value in '{col}'")

    for col in UNIQUE_COLUMNS:
        values = df[col]

        non_empty = values.notna() & values.ne("")
        duplicates = non_empty & values.duplicated(keep=False)
        add_error(duplicates, f"Duplicate value in '{col}'")

    if rules.get("email_validation", True):
        if "email" in df.columns:
            email_ok = df["email"].str.fullmatch(EMAIL_PATTERN, na=False)
            add_error(~email_ok, "Invalid email format")

    return errors

def load_input_data(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() == ".xlsx":
        sheets = read_excel_sheets(file_path)

        frames = [
            sheet.assign(source_sheet=sheet_name)
            for sheet_name, sheet in sheets.items()
        ]

        return pd.concat(frames, ignore_index=True)

    df = read_input(file_path)
    df["source_sheet"] = "CSV"
    return df


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_input_data(INPUT_FILE)

    df = clean_column_names(df)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = df.reset_index(drop=True)
    df.insert(0, "source_row", range(2, len(df) + 2))

    df = clean_text(df, normalize=NORMALIZE)

    df["validation_errors"] = validate_data(df, rules)

    valid_mask = df["validation_errors"].eq("")
    valid_records = df.loc[valid_mask].copy()
    rejected_records = df.loc[~valid_mask].copy()

    valid_records.drop(columns=["validation_errors"]).to_csv(OUTPUT_DIR / "valid_customers.csv", index=False)

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

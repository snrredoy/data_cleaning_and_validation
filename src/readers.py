from pathlib import Path

import pandas as pd


def read_input(
    file_path: Path | str,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, dtype=str)
    if suffix in [".xls", ".xlsx"]:
        return pd.read_excel(path, sheet_name=sheet_name, dtype=str, engine="openpyxl")

    raise ValueError(f"Unsupported file format: {suffix}. Supported formats are .csv, .xls, .xlsx")


def read_excel_sheets(
    file_path: str | Path,
) -> dict[str, pd.DataFrame]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() != ".xlsx":
        raise ValueError("Expected an .xlsx file")

    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype="string",
        engine="openpyxl",
    )

    return sheets

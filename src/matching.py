import pandas as pd


def cross_match(
    source_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    key: str = "customer_id",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_df = source_df.copy()
    reference_df = reference_df.copy()
    source_key = source_df[key]
    reference_key = reference_df[key]

    source_df[key] = source_df[key].astype("string").str.strip().str.upper()
    reference_df[key] = reference_df[key].astype("string").str.strip().str.upper()

    if key not in source_df.columns or key not in reference_df.columns:
        raise ValueError(f"Both datasets must contain '{key}'")

    if (
        source_key.isna().any()
        or source_key.eq("").any()
        or reference_key.isna().any()
        or reference_key.eq("").any()
    ):
        raise ValueError(f"'{key}' cannot contain missing values or blank values")

    if source_df[key].duplicated().any():
        raise ValueError(f"Duplicate '{key}' values found in source dataset")

    if reference_df[key].duplicated().any():
        raise ValueError(f"Duplicate '{key}' values found in reference dataset")

    merged = source_df.merge(
        reference_df,
        on=key,
        how="outer",
        suffixes=("_source", "_reference"),
        indicator=True,
    )

    matched_rows = merged[merged["_merge"] == "both"].copy()

    common_columns = (set(source_df.columns) & set(reference_df.columns)) - {key}

    discrepancy_rows = []

    for _, row in matched_rows.iterrows():
        for column in sorted(common_columns):
            source_value = row[f"{column}_source"]
            reference_value = row[f"{column}_reference"]

            if not (pd.isna(source_value) and pd.isna(reference_value)) and source_value != reference_value:
                discrepancy_rows.append(
                    {
                        key: row[key],
                        "column": column,
                        "source_value": source_value,
                        "reference_value": reference_value,
                    }
                )

    discrepancies = pd.DataFrame(
        discrepancy_rows,
        columns=[key, "column", "source_value", "reference_value"],
    )

    discrepancy_ids = set(discrepancies[key])
    matched = matched_rows[~matched_rows[key].isin(discrepancy_ids)].copy()

    unmatched = merged[merged["_merge"] != "both"].copy()

    matched.drop(columns=["_merge"], inplace=True)
    unmatched.drop(columns=["_merge"], inplace=True)

    return matched, unmatched, discrepancies

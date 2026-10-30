# Data Cleaning and Validation Automation

A small, repeatable Python pipeline for cleaning, validating, and comparing
customer data. The pipeline reads CSV or multi-sheet Excel input, normalizes
common text formatting issues, separates valid and rejected records, and can
compare the cleaned data with a reference dataset.

## What it does

For each input record, the cleaning pipeline:

1. Normalizes column names by trimming whitespace, converting them to lowercase,
   and replacing spaces with underscores.
2. Trims whitespace from text values.
3. Lowercases email addresses and uppercases customer IDs.
4. Checks that the required columns and values are present.
5. Rejects duplicate customer IDs and email addresses.
6. Validates email addresses when enabled in the validation rules.
7. Tracks the source row and, for Excel input, the source worksheet.
8. Writes valid records, rejected records with error messages, and an overall
   summary.

The comparison workflow:

1. Loads the cleaned records from `output/valid_customers.csv`.
2. Loads a reference customer dataset.
3. Normalizes customer IDs before matching.
4. Detects fully matched, unmatched, and discrepant records.
5. Writes comparison reports to `output/comparison_reports/`.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/) for creating the environment and running the
  project

The project dependencies are declared in `pyproject.toml` and pinned in
`uv.lock`.

## Quick start

From the project directory:

```bash
uv sync
./run.sh
```

`run.sh` changes to the project directory before running the pipeline, so it
can also be started using an absolute path:

```bash
/path/to/data-cleaning-and-validation/run.sh
```

If the script is not executable on your system, run:

```bash
bash run.sh
```

You can run the Python module directly instead:

```bash
uv run python -m src.clean_validation
```

The command prints the record counts and the location of the generated reports.

After cleaning and validation, run the comparison workflow with:

```bash
uv run python -m src.run_matching
```

The comparison command requires `output/valid_customers.csv` to exist and
prints the counts and location of the comparison reports.

## Input file

The default source data is the multi-sheet Excel workbook:

```text
data/raw/customers_multi_sheet.xlsx
```

Every CSV file or Excel worksheet must contain these columns:

| Column | Description |
| --- | --- |
| `customer_id` | A non-empty identifier that must be unique |
| `name` | A non-empty customer name |
| `email` | A non-empty address in a valid email format |
| `city` | A non-empty city |

Column names may contain leading/trailing whitespace or spaces between words;
the pipeline normalizes them before validation. All input values are read as
strings. Records from Excel worksheets include the worksheet name in the
`source_sheet` column. CSV input is labeled with `source_sheet` set to `CSV`.

CSV input is also supported by changing `INPUT_FILE` in
`src/clean_validation.py` to a `.csv` file, such as
`data/raw/customers.csv`.

Validation behavior is configured in:

```text
config/validation_rules.json
```

This file defines required columns, columns that must be unique, email format
validation, and text normalization options.

## Output files

Reports are written to `output/` (the directory is created automatically):

| File | Contents |
| --- | --- |
| `valid_customers.csv` | Records that passed every validation check |
| `rejected_customers.csv` | Records that failed validation, including a `validation_errors` column |
| `summary.csv` | Total, valid, and rejected record counts |

Rejected records keep their original input row number in the `source_row` column.
If a record has multiple validation failures, they are listed together in
`validation_errors`, separated by semicolons.

With the sample input currently configured in the repository, the summary is:

```text
Total records:    7
Valid records:    3
Rejected records: 4
```

## Using your own data

1. Back up or replace the configured input file
   (`data/raw/customers_multi_sheet.xlsx` by default).
2. Keep the required columns listed above.
3. Run `./run.sh`.
4. Review the files in `output/`.

Each run overwrites the three output CSV files with results from the current
input.

## Customer comparison

The comparison workflow reads:

```text
output/valid_customers.csv
data/raw/customers_reference.csv
```

Both datasets must contain a unique, non-empty `customer_id` column. Customer
IDs are trimmed and converted to uppercase before matching. The workflow
compares columns shared by both datasets and reports differences in their
values.

Comparison reports are written to `output/comparison_reports/`:

| File | Contents |
| --- | --- |
| `matched_records.csv` | Records whose IDs and shared field values match |
| `unmatched_records.csv` | Records present in only one dataset |
| `discrepancy_report.csv` | One row per differing field, including source and reference values |

The reference dataset can be replaced with another CSV as long as it retains
the required `customer_id` column and the shared columns to compare.

## Project layout

```text
.
├── data/
│   └── raw/
│       ├── customers.csv       # Optional CSV input
│       ├── customers_multi_sheet.xlsx # Default Excel input
│       └── customers_reference.csv # Reference data for comparison
├── output/
│   └── comparison_reports/     # Generated comparison reports
├── src/
│   ├── clean_validation.py     # Cleaning and validation pipeline
│   ├── matching.py             # Customer matching and discrepancy detection
│   ├── readers.py              # CSV and Excel readers
│   ├── rules.py                # Validation rules loader
│   └── run_matching.py         # Comparison workflow runner
├── config/
│   └── validation_rules.json   # Validation and normalization settings
├── requirements.txt            # Locked package list
├── pyproject.toml              # Project metadata and dependencies
├── run.sh                      # Convenience runner
└── uv.lock                     # Reproducible dependency lock file
```

## Troubleshooting

- **`uv: command not found`**: install uv using the
  [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
- **Missing required columns**: check the header row in
  the configured input file; the required columns are `customer_id`, `name`,
  `email`, and `city`.
- **Permission denied when running `./run.sh`**: use `bash run.sh`, or make the
  script executable with `chmod +x run.sh`.
- **Invalid records**: open `output/rejected_customers.csv` and read the
  `validation_errors` column for the reason each record was rejected.
- **Comparison input missing**: run the cleaning workflow before
  `uv run python -m src.run_matching`; the comparison workflow requires
  `output/valid_customers.csv`.
- **Comparison key errors**: ensure both datasets contain a unique,
  non-empty `customer_id` column.

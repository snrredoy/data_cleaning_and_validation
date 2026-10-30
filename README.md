# Data Cleaning and Validation Automation

A small, repeatable Python pipeline for cleaning and validating customer data
stored in a CSV file. The pipeline reads the raw input, normalizes common text
formatting issues, separates valid and rejected records, and writes a summary
report.

## What it does

For each input record, the pipeline:

1. Normalizes column names by trimming whitespace, converting them to lowercase,
   and replacing spaces with underscores.
2. Trims whitespace from text values.
3. Lowercases email addresses and uppercases customer IDs.
4. Checks that the required columns and values are present.
5. Rejects duplicate customer IDs.
6. Validates email addresses.
7. Writes valid records, rejected records with error messages, and an overall
   summary.

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

## Input file

Place the source data at:

```text
data/raw/customers.csv
```

The CSV must contain these columns:

| Column | Description |
| --- | --- |
| `customer_id` | A non-empty identifier that must be unique |
| `name` | A non-empty customer name |
| `email` | A non-empty address in a valid email format |
| `city` | A non-empty city |

Column names may contain leading/trailing whitespace or spaces between words;
the pipeline normalizes them before validation. All input values are read as
strings.

## Output files

Reports are written to `output/` (the directory is created automatically):

| File | Contents |
| --- | --- |
| `valid_customers.csv` | Records that passed every validation check |
| `rejected_customers.csv` | Records that failed validation, including a `validation_errors` column |
| `summary.csv` | Total, valid, and rejected record counts |

Rejected records keep their original CSV row number in the `source_row` column.
If a record has multiple validation failures, they are listed together in
`validation_errors`, separated by semicolons.

With the sample data included in this repository, the summary is:

```text
Total records:    7
Valid records:    3
Rejected records: 4
```

## Using your own data

1. Back up or replace `data/raw/customers.csv`.
2. Keep the required columns listed above.
3. Run `./run.sh`.
4. Review the files in `output/`.

Each run overwrites the three output CSV files with results from the current
input.

## Project layout

```text
.
├── data/
│   └── raw/
│       └── customers.csv       # Input CSV
├── output/                     # Generated reports
├── src/
│   └── clean_validation.py     # Cleaning and validation pipeline
├── requirements.txt            # Locked package list
├── pyproject.toml              # Project metadata and dependencies
├── run.sh                      # Convenience runner
└── uv.lock                     # Reproducible dependency lock file
```

## Troubleshooting

- **`uv: command not found`**: install uv using the
  [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
- **Missing required columns**: check the header row in
  `data/raw/customers.csv`; the required columns are `customer_id`, `name`,
  `email`, and `city`.
- **Permission denied when running `./run.sh`**: use `bash run.sh`, or make the
  script executable with `chmod +x run.sh`.
- **Invalid records**: open `output/rejected_customers.csv` and read the
  `validation_errors` column for the reason each record was rejected.

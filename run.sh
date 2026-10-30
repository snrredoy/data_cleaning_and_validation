#!/usr/bin/env bash

set -euo pipefail

# Go to the project root
cd "$(dirname "$0")"

# Run the data cleaning automation
uv run python -m src.clean_validation

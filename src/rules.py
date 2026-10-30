import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = PROJECT_ROOT / "config" / "validation_rules.json"

def load_rules() -> dict[str, Any]:
    if not RULES_FILE.exists():
        raise FileNotFoundError(f"Rules file not found: {RULES_FILE}")

    with RULES_FILE.open("r", encoding="utf-8") as f:
        rules = json.load(f)

    if not isinstance(rules, dict):
        raise ValueError(f"Invalid rules format in {RULES_FILE}. Expected a JSON object.")

    return rules
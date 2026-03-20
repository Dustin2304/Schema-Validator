# Schema Validator

[![CI](https://github.com/Dustin2304/Schema-Validator/actions/workflows/ci.yml/badge.svg)](https://github.com/Dustin2304/Schema-Validator/actions/workflows/ci.yml)

A Python toolkit for Excel data pipelines — schema validation module.

## What it does

Validates a `pandas.DataFrame` against a declared `Schema`. Reports violations for:

- Missing or extra columns
- Null values in non-nullable columns
- Wrong data types
- Values outside `min_value` / `max_value` range
- Values not in `allowed_values`

## Usage

```python
from src.core.models import ColumnSchema, DType, Schema
from src.core.validator import validate
import pandas as pd

schema = Schema(columns=[
    ColumnSchema(name="age",  dtype=DType.INTEGER, min_value=0, max_value=120),
    ColumnSchema(name="name", dtype=DType.STRING),
])

df = pd.DataFrame({"age": [25, -1], "name": ["Alice", "Bob"]})
report = validate(df, schema)

print(report.summary)
# Validation failed with 1 violation(s): min_value
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install ruff mypy pandas pytest pytest-cov

ruff check src/ tests/
mypy src/
pytest tests/ --cov=src --cov-report=term-missing
```

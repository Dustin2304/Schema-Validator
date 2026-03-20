from __future__ import annotations

import pandas as pd

from src.core.models import ColumnSchema, DType, Schema
from src.core.validator import validate


def test_valid_dataframe_passes() -> None:
    schema = Schema(
        columns=[
            ColumnSchema(name="age", dtype=DType.INTEGER),
            ColumnSchema(name="name", dtype=DType.STRING),
        ]
    )
    df = pd.DataFrame({"age": [25, 30], "name": ["Alice", "Bob"]})

    report = validate(df, schema)

    assert report.is_valid is True
    assert report.violations == []


def test_missing_column_detected() -> None:
    schema = Schema(
        columns=[
            ColumnSchema(name="age", dtype=DType.INTEGER),
            ColumnSchema(name="name", dtype=DType.STRING),
        ]
    )
    df = pd.DataFrame({"age": [25, 30]})  # "name" fehlt

    report = validate(df, schema)

    assert report.is_valid is False
    assert len(report.violations) == 1
    assert report.violations[0].column == "name"
    assert report.violations[0].rule == "missing_column"

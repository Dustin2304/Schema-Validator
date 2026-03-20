from __future__ import annotations

import pandas as pd

from src.core.models import DType, Schema, ValidationReport, Violation

_DTYPE_MAP: dict[DType, type] = {
    DType.INTEGER: int,
    DType.FLOAT:   float,
    DType.STRING:  str,
    DType.BOOLEAN: bool,
}


def validate(df: pd.DataFrame, schema: Schema) -> ValidationReport:
    violations: list[Violation] = []

    # Rule 1: missing columns
    for col in schema.column_names:
        if col not in df.columns:
            violations.append(
                Violation(
                    column=col,
                    rule="missing_column",
                    message=f"Required column '{col}' is missing.",
                )
            )

    # Rule 2: extra columns
    if not schema.allow_extra_cols:
        for col in df.columns:
            if col not in schema.column_names:
                violations.append(
                    Violation(
                        column=col,
                        rule="extra_column",
                        message=f"Unexpected column '{col}' is not in schema.",
                    )
                )

    # Per-column rules — only for columns that are present in both
    present = {c for c in schema.column_names if c in df.columns}
    for col_schema in schema.columns:
        if col_schema.name not in present:
            continue
        series = df[col_schema.name]

        # Rule 3: nullable
        null_mask = series.isna()
        if not col_schema.nullable and null_mask.any():
            violations.append(
                Violation(
                    column=col_schema.name,
                    rule="nullable",
                    message=(
                            f"Column '{col_schema.name}' contains null values"
                            " but is not nullable."
                        ),
                    row_indices=list(df.index[null_mask]),
                )
            )

        # Rule 4: dtype — only check non-null values; skip DATE (needs custom logic)
        if col_schema.dtype != DType.DATE:
            expected_py_type = _DTYPE_MAP[col_schema.dtype]
            non_null = series.dropna()
            bad_mask = ~non_null.apply(lambda v: isinstance(v, expected_py_type))
            if bad_mask.any():
                violations.append(
                    Violation(
                        column=col_schema.name,
                        rule="dtype",
                        message=(
                            f"Column '{col_schema.name}' contains values that are not"
                            f" of type {col_schema.dtype.value}."
                        ),
                        row_indices=list(non_null.index[bad_mask]),
                    )
                )

        # Rule 5: range min/max — only for numeric non-null values
        numeric_series = pd.to_numeric(series, errors="coerce").dropna()
        if col_schema.min_value is not None:
            below = numeric_series[numeric_series < col_schema.min_value]
            if not below.empty:
                violations.append(
                    Violation(
                        column=col_schema.name,
                        rule="min_value",
                        message=(
                            f"Column '{col_schema.name}' has values below"
                            f" min_value={col_schema.min_value}."
                        ),
                        row_indices=list(below.index),
                    )
                )
        if col_schema.max_value is not None:
            above = numeric_series[numeric_series > col_schema.max_value]
            if not above.empty:
                violations.append(
                    Violation(
                        column=col_schema.name,
                        rule="max_value",
                        message=(
                            f"Column '{col_schema.name}' has values above"
                            f" max_value={col_schema.max_value}."
                        ),
                        row_indices=list(above.index),
                    )
                )

        # Rule 6: allowed values
        if col_schema.allowed_values:
            non_null_series = series.dropna()
            bad = non_null_series[~non_null_series.isin(col_schema.allowed_values)]
            if not bad.empty:
                violations.append(
                    Violation(
                        column=col_schema.name,
                        rule="allowed_values",
                        message=(
                            f"Column '{col_schema.name}' contains values not in"
                            f" allowed list: {sorted(set(bad.tolist()))}."
                        ),
                        row_indices=list(bad.index),
                    )
                )

    return ValidationReport(
        is_valid=len(violations) == 0,
        violations=violations,
    )

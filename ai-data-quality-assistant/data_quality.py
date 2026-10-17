"""Rule-based data-quality checks for tabular data."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd


def analyze_dataframe(df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, pd.DataFrame]]:
    """Return a list of findings and a dictionary of inspectable affected records."""
    findings: list[dict[str, Any]] = []
    details: dict[str, pd.DataFrame] = {}

    for col in df.columns:
        count = int(df[col].isna().sum())
        if count:
            key = f"Missing values — {col}"
            findings.append({
                "issue": "Missing values",
                "column": str(col),
                "count": count,
                "details": f"{count} missing value(s) in column '{col}'.",
            })
            details[key] = df[df[col].isna()].copy()

    duplicate_mask = df.duplicated(keep=False)
    duplicate_count = int(df.duplicated(keep="first").sum())
    if duplicate_count:
        findings.append({
            "issue": "Duplicate rows",
            "column": "All columns",
            "count": duplicate_count,
            "details": f"{duplicate_count} repeated row(s), excluding the first occurrence.",
        })
        details["Duplicate rows"] = df[duplicate_mask].copy()

    for col in df.columns:
        if re.search(r"(^id$|_id$|id$|email|code$)", str(col).lower()):
            dup_mask = df[col].notna() & df[col].duplicated(keep=False)
            count = int(df[col].duplicated(keep="first").sum())
            if count:
                key = f"Repeated identifier — {col}"
                findings.append({
                    "issue": "Repeated identifier",
                    "column": str(col),
                    "count": count,
                    "details": f"{count} repeated value(s) in likely identifier column '{col}'.",
                })
                details[key] = df[dup_mask].copy()

    bad_columns = [
        str(c) for c in df.columns
        if str(c).strip() != str(c) or " " in str(c) or str(c) != str(c).lower()
    ]
    if bad_columns:
        findings.append({
            "issue": "Inconsistent column names",
            "column": ", ".join(bad_columns),
            "count": len(bad_columns),
            "details": "Column names contain spaces, leading/trailing whitespace, or uppercase characters.",
        })
        details["Inconsistent column names"] = pd.DataFrame({"column_name": bad_columns})

    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = df[col].notna() & ((df[col] < lower) | (df[col] > upper))
        count = int(mask.sum())
        if count:
            key = f"Potential numeric outliers — {col}"
            findings.append({
                "issue": "Potential numeric outliers",
                "column": str(col),
                "count": count,
                "details": f"{count} value(s) outside the IQR range [{lower:.3g}, {upper:.3g}]. Review before changing data.",
            })
            details[key] = df[mask].copy()

    return findings, details


def build_summary(df: pd.DataFrame, findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Create transparent, rule-based recommendations from the findings."""
    recommendations: list[str] = []
    issue_names = {item["issue"] for item in findings}
    if "Missing values" in issue_names:
        recommendations.append("Review missing values by column and decide whether to fill, flag, or leave them blank based on business rules.")
    if "Duplicate rows" in issue_names:
        recommendations.append("Inspect repeated rows before removing them; confirm whether they represent accidental duplicates or valid repeated events.")
    if "Repeated identifier" in issue_names:
        recommendations.append("Check uniqueness rules for identifier columns and resolve collisions at the source when possible.")
    if "Inconsistent column names" in issue_names:
        recommendations.append("Standardize column names to lowercase snake_case before downstream transformations.")
    if "Potential numeric outliers" in issue_names:
        recommendations.append("Review potential outliers with domain context; an unusual value is not automatically an error.")
    if not recommendations:
        recommendations.append("No issues were detected by the configured checks. Add domain-specific validation rules for stronger assurance.")
    recommendations.append("Record any corrections and validation rules so the data-quality process is repeatable.")
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "recommendations": recommendations,
    }

"""Deterministic data-quality checks, configurable rules, and report metadata."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

HIGH_SEVERITY = {
    "Required column missing values",
    "Custom uniqueness rule",
    "Numeric range violation",
    "Disallowed values",
}
MEDIUM_SEVERITY = {
    "Missing values",
    "Duplicate rows",
    "Repeated identifier",
    "Inconsistent column names",
    "Potential numeric outliers",
}


def analyze_dataframe(df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, pd.DataFrame]]:
    findings: list[dict[str, Any]] = []
    details: dict[str, pd.DataFrame] = {}

    for col in df.columns:
        count = int(df[col].isna().sum())
        if count:
            findings.append({
                "issue": "Missing values", "column": str(col), "count": count,
                "details": f"{count} missing value(s) in column '{col}'.",
            })
            details[f"Missing values — {col}"] = df[df[col].isna()].copy()

    duplicate_mask = df.duplicated(keep=False)
    duplicate_count = int(df.duplicated(keep="first").sum())
    if duplicate_count:
        findings.append({
            "issue": "Duplicate rows", "column": "All columns", "count": duplicate_count,
            "details": f"{duplicate_count} repeated row(s), excluding the first occurrence.",
        })
        details["Duplicate rows"] = df[duplicate_mask].copy()

    for col in df.columns:
        if re.search(r"(^id$|_id$|id$|email|code$)", str(col).lower()):
            dup_mask = df[col].notna() & df[col].duplicated(keep=False)
            count = int(df[col].duplicated(keep="first").sum())
            if count:
                findings.append({
                    "issue": "Repeated identifier", "column": str(col), "count": count,
                    "details": f"{count} repeated value(s) in likely identifier column '{col}'.",
                })
                details[f"Repeated identifier — {col}"] = df[dup_mask].copy()

    bad_columns = [
        str(c) for c in df.columns
        if str(c).strip() != str(c) or " " in str(c) or str(c) != str(c).lower()
    ]
    if bad_columns:
        findings.append({
            "issue": "Inconsistent column names", "column": ", ".join(bad_columns),
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
            findings.append({
                "issue": "Potential numeric outliers", "column": str(col), "count": count,
                "details": f"{count} value(s) outside the IQR range [{lower:.3g}, {upper:.3g}]. Review before changing data.",
            })
            details[f"Potential numeric outliers — {col}"] = df[mask].copy()

    return enrich_findings(findings), details


def validate_with_rules(
    df: pd.DataFrame, rules: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, pd.DataFrame]]:
    findings: list[dict[str, Any]] = []
    details: dict[str, pd.DataFrame] = {}

    for col in rules.get("required_columns", []):
        if col not in df.columns:
            continue
        mask = df[col].isna()
        count = int(mask.sum())
        if count:
            findings.append({
                "issue": "Required column missing values", "column": str(col), "count": count,
                "details": f"{count} row(s) have missing values in required column '{col}'.",
            })
            details[f"Required column missing values — {col}"] = df[mask].copy()

    for col in rules.get("unique_columns", []):
        if col not in df.columns:
            continue
        mask = df[col].notna() & df[col].duplicated(keep=False)
        count = int(df[col].duplicated(keep="first").sum())
        if count:
            findings.append({
                "issue": "Custom uniqueness rule", "column": str(col), "count": count,
                "details": f"{count} repeated value(s) violate the configured uniqueness rule for '{col}'.",
            })
            details[f"Custom uniqueness rule — {col}"] = df[mask].copy()

    for col, limits in rules.get("numeric_ranges", {}).items():
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        lower, upper = limits.get("min"), limits.get("max")
        mask = pd.Series(False, index=df.index)
        if lower is not None:
            mask |= df[col].notna() & (df[col] < lower)
        if upper is not None:
            mask |= df[col].notna() & (df[col] > upper)
        count = int(mask.sum())
        if count:
            findings.append({
                "issue": "Numeric range violation", "column": str(col), "count": count,
                "details": f"{count} value(s) fall outside the configured range [{lower}, {upper}] for '{col}'.",
            })
            details[f"Numeric range violation — {col}"] = df[mask].copy()

    for col, allowed in rules.get("allowed_values", {}).items():
        if col not in df.columns or not allowed:
            continue
        non_missing = df[col].notna()
        mask = non_missing & ~df[col].astype(str).isin([str(v) for v in allowed])
        count = int(mask.sum())
        if count:
            findings.append({
                "issue": "Disallowed values", "column": str(col), "count": count,
                "details": f"{count} value(s) are not in the configured allowed-value list for '{col}'.",
            })
            details[f"Disallowed values — {col}"] = df[mask].copy()

    return enrich_findings(findings), details


def enrich_findings(findings: list[dict[str, Any]], start: int = 1) -> list[dict[str, Any]]:
    """Add sequential IDs and severity labels to one list of findings."""
    enriched = []
    for index, finding in enumerate(findings, start=start):
        issue = finding["issue"]
        if issue in HIGH_SEVERITY:
            severity = "High"
        elif issue in MEDIUM_SEVERITY:
            severity = "Medium"
        else:
            severity = "Low"
        enriched.append({
            "finding_id": f"DQ-{index:03d}",
            **finding,
            "severity": severity,
        })
    return enriched


def assign_global_finding_ids(
    standard_findings: list[dict[str, Any]],
    custom_findings: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Re-number standard and custom findings in one continuous sequence."""
    combined = []
    for finding in standard_findings + custom_findings:
        combined.append({key: value for key, value in finding.items() if key != "finding_id" and key != "severity"})
    enriched = enrich_findings(combined)
    standard_count = len(standard_findings)
    return enriched[:standard_count], enriched[standard_count:]


def build_quality_status(findings: list[dict[str, Any]]) -> str:
    if any(item.get("severity") == "High" for item in findings):
        return "FAIL"
    if findings:
        return "PASS WITH WARNINGS"
    return "PASS"


def build_summary(df: pd.DataFrame, findings: list[dict[str, Any]]) -> dict[str, Any]:
    recommendations: list[str] = []
    issue_names = {item["issue"] for item in findings}
    if issue_names & {"Missing values", "Required column missing values"}:
        recommendations.append("Review missing values and decide whether to fill, flag, or leave them blank based on business rules.")
    if "Duplicate rows" in issue_names:
        recommendations.append("Inspect repeated rows before removing them; confirm whether they represent accidental duplicates or valid repeated events.")
    if issue_names & {"Repeated identifier", "Custom uniqueness rule"}:
        recommendations.append("Check uniqueness rules for identifier columns and resolve collisions at the source when possible.")
    if "Inconsistent column names" in issue_names:
        recommendations.append("Standardize column names to lowercase snake_case before downstream transformations.")
    if "Potential numeric outliers" in issue_names:
        recommendations.append("Review potential outliers with domain context; an unusual value is not automatically an error.")
    if "Numeric range violation" in issue_names:
        recommendations.append("Review numeric range violations against documented business constraints before changing values.")
    if "Disallowed values" in issue_names:
        recommendations.append("Check categorical values against the approved domain or reference list.")
    if not recommendations:
        recommendations.append("No issues were detected by the configured checks. Consider adding domain-specific rules for stronger assurance.")
    recommendations.append("Record corrections and validation rules so the data-quality process is repeatable.")
    return {"row_count": int(len(df)), "column_count": int(len(df.columns)), "recommendations": recommendations}

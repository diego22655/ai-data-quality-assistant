import json

import pandas as pd

from data_quality import (
    analyze_dataframe, build_quality_status, build_summary, validate_with_rules,
)


def test_standard_checks_find_common_issues():
    df = pd.DataFrame({
        "customer_id": ["C001", "C002", "C002", "C004"],
        "email": ["a@example.com", "b@example.com", "b@example.com", None],
        "spend": [10, 20, 20, 999],
    })
    findings, details = analyze_dataframe(df)
    issue_types = {item["issue"] for item in findings}
    assert {"Missing values", "Duplicate rows", "Repeated identifier", "Potential numeric outliers"} <= issue_types
    assert details


def test_clean_data_returns_no_findings():
    df = pd.DataFrame({"customer_id": ["C001", "C002", "C003"], "spend": [10, 12, 11]})
    findings, _ = analyze_dataframe(df)
    assert findings == []


def test_required_column_rule():
    df = pd.DataFrame({"email": ["a@example.com", None]})
    findings, details = validate_with_rules(df, {"required_columns": ["email"]})
    assert findings[0]["issue"] == "Required column missing values"
    assert len(details["Required column missing values — email"]) == 1


def test_unique_rule_ignores_nulls():
    df = pd.DataFrame({"customer_id": ["A", "A", None]})
    findings, _ = validate_with_rules(df, {"unique_columns": ["customer_id"]})
    assert findings[0]["count"] == 1


def test_numeric_range_rule():
    df = pd.DataFrame({"age": [17, 25, 90]})
    findings, _ = validate_with_rules(df, {"numeric_ranges": {"age": {"min": 18, "max": 80}}})
    assert findings[0]["count"] == 2


def test_allowed_values_rule():
    df = pd.DataFrame({"country": ["Peru", "Chile", "Mars", None]})
    findings, _ = validate_with_rules(df, {"allowed_values": {"country": ["Peru", "Chile"]}})
    assert findings[0]["count"] == 1


def test_findings_have_ids_and_severity():
    df = pd.DataFrame({"email": [None]})
    findings, _ = analyze_dataframe(df)
    assert findings[0]["finding_id"] == "DQ-001"
    assert findings[0]["severity"] == "Medium"


def test_quality_status_fail_with_high_severity():
    assert build_quality_status([{"severity": "High"}]) == "FAIL"


def test_quality_status_warning_for_medium_only():
    assert build_quality_status([{"severity": "Medium"}]) == "PASS WITH WARNINGS"


def test_quality_status_pass_for_no_findings():
    assert build_quality_status([]) == "PASS"


def test_json_report_fields_are_serializable():
    df = pd.DataFrame({"customer_id": ["A", "B"], "spend": [10, 12]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    report = {"status": build_quality_status(findings), "findings": findings, "recommendations": summary["recommendations"]}
    assert json.loads(json.dumps(report))["status"] == "PASS"


def test_invalid_numeric_range_not_used_by_ui_logic_is_not_a_module_rule():
    # Core validator remains robust when bounds are explicitly provided.
    df = pd.DataFrame({"age": [10, 20, 90]})
    findings, _ = validate_with_rules(df, {"numeric_ranges": {"age": {"min": 18, "max": 80}}})
    assert findings[0]["count"] == 2

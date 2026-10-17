import json
import pandas as pd

from data_quality import (
    analyze_dataframe, assign_global_finding_ids, build_quality_status,
    build_summary, validate_with_rules,
)


def test_standard_checks_find_common_issues():
    df = pd.DataFrame({"customer_id": ["C001", "C002", "C002", "C004"], "email": ["a@example.com", "b@example.com", "b@example.com", None], "spend": [10, 20, 20, 999]})
    findings, details = analyze_dataframe(df)
    assert {"Missing values", "Duplicate rows", "Repeated identifier", "Potential numeric outliers"} <= {f["issue"] for f in findings}
    assert details


def test_clean_data_returns_no_findings():
    findings, _ = analyze_dataframe(pd.DataFrame({"customer_id": ["C001", "C002", "C003"], "spend": [10, 12, 11]}))
    assert findings == []


def test_required_column_rule():
    df = pd.DataFrame({"email": ["a@example.com", None]})
    findings, details = validate_with_rules(df, {"required_columns": ["email"]})
    assert findings[0]["issue"] == "Required column missing values"
    assert len(details["Required column missing values — email"]) == 1


def test_unique_rule_ignores_nulls():
    findings, _ = validate_with_rules(pd.DataFrame({"customer_id": ["A", "A", None]}), {"unique_columns": ["customer_id"]})
    assert findings[0]["count"] == 1


def test_numeric_range_rule():
    findings, _ = validate_with_rules(pd.DataFrame({"age": [17, 25, 90]}), {"numeric_ranges": {"age": {"min": 18, "max": 80}}})
    assert findings[0]["count"] == 2


def test_allowed_values_rule():
    findings, _ = validate_with_rules(pd.DataFrame({"country": ["Peru", "Chile", "Mars", None]}), {"allowed_values": {"country": ["Peru", "Chile"]}})
    assert findings[0]["count"] == 1


def test_global_ids_are_unique_across_standard_and_custom_findings():
    df = pd.DataFrame({"email": [None, "x@example.com"], "customer_id": ["A", "A"]})
    standard, _ = analyze_dataframe(df)
    custom, _ = validate_with_rules(df, {"required_columns": ["email"], "unique_columns": ["customer_id"]})
    standard, custom = assign_global_finding_ids(standard, custom)
    all_ids = [f["finding_id"] for f in standard + custom]
    assert len(all_ids) == len(set(all_ids))
    assert all_ids == [f"DQ-{i:03d}" for i in range(1, len(all_ids) + 1)]


def test_custom_findings_keep_high_severity_after_global_numbering():
    df = pd.DataFrame({"email": [None]})
    standard, _ = analyze_dataframe(df)
    custom, _ = validate_with_rules(df, {"required_columns": ["email"]})
    standard, custom = assign_global_finding_ids(standard, custom)
    assert custom[0]["finding_id"] == f"DQ-{len(standard)+1:03d}"
    assert custom[0]["severity"] == "High"


def test_quality_status_fail_with_high_severity():
    assert build_quality_status([{"severity": "High"}]) == "FAIL"


def test_quality_status_warning_for_medium_only():
    assert build_quality_status([{"severity": "Medium"}]) == "PASS WITH WARNINGS"


def test_quality_status_pass_for_no_findings():
    assert build_quality_status([]) == "PASS"


def test_report_fields_are_json_serializable():
    df = pd.DataFrame({"customer_id": ["A", "B"], "spend": [10, 12]})
    findings, _ = analyze_dataframe(df)
    report = {"status": build_quality_status(findings), "findings": findings, "recommendations": build_summary(df, findings)["recommendations"]}
    assert json.loads(json.dumps(report))["status"] == "PASS"

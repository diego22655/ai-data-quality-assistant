import json

import pandas as pd

from data_quality import analyze_dataframe, build_summary, validate_with_rules


def test_detects_missing_values_and_duplicate_rows():
    df = pd.DataFrame({
        "customer_id": ["C001", "C002", "C002", "C004"],
        "email": ["a@example.com", "b@example.com", "b@example.com", None],
        "spend": [10, 20, 20, 999],
    })
    findings, details = analyze_dataframe(df)
    issue_types = {item["issue"] for item in findings}
    assert "Missing values" in issue_types
    assert "Duplicate rows" in issue_types
    assert "Repeated identifier" in issue_types
    assert "Potential numeric outliers" in issue_types
    assert details


def test_clean_data_returns_no_findings():
    df = pd.DataFrame({"customer_id": ["C001", "C002", "C003"], "spend": [10, 12, 11]})
    findings, _ = analyze_dataframe(df)
    assert findings == []


def test_required_column_rule():
    df = pd.DataFrame({"email": ["a@example.com", None], "age": [20, 30]})
    findings, details = validate_with_rules(df, {"required_columns": ["email"]})
    assert findings[0]["issue"] == "Required column missing values"
    assert findings[0]["count"] == 1
    assert len(details["Required column missing values — email"]) == 1


def test_unique_column_rule_ignores_missing_values():
    df = pd.DataFrame({"customer_id": ["A", "A", None]})
    findings, _ = validate_with_rules(df, {"unique_columns": ["customer_id"]})
    assert findings[0]["issue"] == "Custom uniqueness rule"
    assert findings[0]["count"] == 1


def test_numeric_range_rule():
    df = pd.DataFrame({"age": [17, 25, 90]})
    findings, details = validate_with_rules(
        df, {"numeric_ranges": {"age": {"min": 18, "max": 80}}}
    )
    assert findings[0]["issue"] == "Numeric range violation"
    assert findings[0]["count"] == 2
    assert len(details["Numeric range violation — age"]) == 2


def test_allowed_values_rule():
    df = pd.DataFrame({"country": ["Peru", "Chile", "Mars", None]})
    findings, details = validate_with_rules(
        df, {"allowed_values": {"country": ["Peru", "Chile"]}}
    )
    assert findings[0]["issue"] == "Disallowed values"
    assert findings[0]["count"] == 1
    assert details["Disallowed values — country"]["country"].tolist() == ["Mars"]


def test_report_json_is_serializable():
    df = pd.DataFrame({"customer_id": ["A", "B"], "spend": [10, 12]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    report = {
        "row_count": int(len(df)),
        "findings": findings,
        "recommendations": summary["recommendations"],
    }
    encoded = json.dumps(report)
    assert json.loads(encoded)["row_count"] == 2


def test_empty_findings_still_have_recommendations():
    df = pd.DataFrame({"value": [1, 2, 3]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    assert findings == []
    assert summary["recommendations"]

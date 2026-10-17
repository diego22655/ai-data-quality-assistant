import json

import pandas as pd

from data_quality import analyze_dataframe, build_summary


def test_detects_missing_values_and_duplicate_rows():
    df = pd.DataFrame({
        "customer_id": ["C001", "C002", "C002", "C004"],
        "email": ["a@example.com", "b@example.com", "b@example.com", None],
        "spend": [10, 20, 20, 999],
    })
    findings, details = analyze_dataframe(df)
    issue_types = {finding["issue"] for finding in findings}
    assert "Missing values" in issue_types
    assert "Duplicate rows" in issue_types
    assert "Repeated identifier" in issue_types
    assert "Potential numeric outliers" in issue_types
    assert details


def test_detects_inconsistent_column_names():
    df = pd.DataFrame({"Customer Name": ["Ana"], " Age ": [30]})
    findings, _ = analyze_dataframe(df)
    assert any(item["issue"] == "Inconsistent column names" for item in findings)


def test_clean_data_returns_no_findings():
    df = pd.DataFrame({"customer_id": ["C001", "C002", "C003"], "spend": [10, 12, 11]})
    findings, _ = analyze_dataframe(df)
    assert findings == []


def test_summary_contains_recommendations():
    df = pd.DataFrame({"customer_id": ["C001", "C001"], "email": [None, "a@example.com"]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    assert summary["recommendations"]


def test_report_payload_is_json_serializable():
    df = pd.DataFrame({"customer_id": ["C001", "C002"], "spend": [10, 12]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "issue_type_count": int(len(findings)),
        "findings": findings,
        "recommendations": summary["recommendations"],
    }
    serialized = json.dumps(report, ensure_ascii=False)
    assert json.loads(serialized)["row_count"] == 2


def test_empty_findings_still_produce_summary():
    df = pd.DataFrame({"a": [1, 2, 3]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    assert findings == []
    assert len(summary["recommendations"]) >= 1

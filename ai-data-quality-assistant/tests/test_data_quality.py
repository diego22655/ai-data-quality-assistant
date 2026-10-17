import pandas as pd
from data_quality import analyze_dataframe, build_summary


def test_detects_missing_values_and_duplicate_rows():
    df = pd.DataFrame({
        "customer_id": [1, 1, 3, 4],
        "email": ["a@example.com", "a@example.com", None, "d@example.com"],
        "spend": [10, 10, 12, 999],
    })
    findings, details = analyze_dataframe(df)
    issue_types = {f["issue"] for f in findings}
    assert "Missing values" in issue_types
    assert "Duplicate rows" in issue_types
    assert "Repeated identifier" in issue_types
    assert "Potential numeric outliers" in issue_types
    assert details


def test_clean_data_returns_no_findings():
    df = pd.DataFrame({"customer_id": [1, 2, 3], "spend": [10, 12, 11]})
    findings, _ = analyze_dataframe(df)
    assert findings == []


def test_summary_contains_recommendations():
    df = pd.DataFrame({"customer_id": [1, 1], "email": [None, "a@example.com"]})
    findings, _ = analyze_dataframe(df)
    summary = build_summary(df, findings)
    assert summary["recommendations"]

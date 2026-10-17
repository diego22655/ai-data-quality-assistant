# AI Data Quality Assistant

A lightweight CSV data-quality profiler built with Python, pandas, and Streamlit. It combines deterministic checks, configurable business rules, affected-row inspection, structured exports, and automated tests. No paid AI API is required.

## Features
- Detect missing values, exact duplicate rows, repeated likely identifiers, inconsistent column names, and potential numeric outliers using IQR.
- Configure required columns, unique columns, numeric ranges, and allowed categorical values.
- Inspect affected records.
- Export a JSON report and a CSV findings file.
- Assign finding IDs and severity labels, and produce an overall `PASS`, `PASS WITH WARNINGS`, or `FAIL` status.
- Show a distinct affected-row count to avoid simply summing overlapping findings.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell: `.venv\\Scripts\\Activate.ps1`.

## Run tests
```bash
pytest -q
```

## Interpretation and limitations
- A high-severity finding causes `FAIL`; medium-severity findings without high-severity findings produce `PASS WITH WARNINGS`; no findings produce `PASS`.
- Severity levels are example defaults and should be adjusted to match a team's business rules.
- A potential outlier is a review candidate, not automatically an error.
- Custom rules are configured for each uploaded file and are not saved between sessions.
- The application does not send uploaded rows to an external AI service.

## Portfolio summary
**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream data pipelines.

**Approach:** A repeatable profiling workflow that detects common issues, applies configurable business constraints, surfaces affected records, and exports a structured quality report.

**Skills demonstrated:** Python, pandas, data validation, unit testing, Streamlit, rule-based profiling, and report generation.

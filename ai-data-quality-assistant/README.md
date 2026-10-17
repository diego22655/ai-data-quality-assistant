# AI Data Quality Assistant

A CSV data-quality profiler built with Python, pandas, and Streamlit. It combines deterministic checks, configurable business rules, affected-row inspection, structured exports, and automated tests. No paid AI API is required.

## Features
- Missing values, duplicate rows, repeated likely identifiers, inconsistent column names, and potential numeric outliers (IQR).
- Configurable required columns, unique columns, numeric ranges, and allowed categorical values.
- Finding IDs unique across standard and custom checks, severity labels, and overall `PASS`, `PASS WITH WARNINGS`, or `FAIL` status.
- JSON report and CSV findings export; inspect affected records in the UI.
- Automated tests for standard checks, custom rules, report status, serialization, and global finding IDs.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests with `pytest -q`.

## Severity and status
High-severity findings produce `FAIL`; medium-severity findings without high-severity findings produce `PASS WITH WARNINGS`; no findings produce `PASS`. These are example defaults and should be aligned with business requirements.

## Privacy and limitations
The application does not send uploaded rows to an external AI service. A potential outlier is a review candidate, not automatically an error. Custom rules are selected for each uploaded file and are not saved between sessions.

## Portfolio summary
**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream data pipelines.

**Approach:** A repeatable profiling workflow that detects common issues, applies configurable business constraints, surfaces affected records, and exports a structured quality report.

**Skills demonstrated:** Python, pandas, data validation, unit testing, Streamlit, rule-based profiling, and report generation.

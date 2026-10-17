# AI Data Quality Assistant

A portfolio project that profiles CSV files using deterministic data-quality checks and configurable column-level rules. It includes a Streamlit UI, affected-row inspection, JSON/CSV exports, and automated tests. It does not require a paid AI API.

## Features

### Standard checks
- Missing values
- Exact duplicate rows
- Repeated values in likely identifier columns
- Inconsistent column names
- Potential numeric outliers using the IQR rule

### Configurable rules
- Required columns (no missing values)
- Unique columns
- Numeric minimum/maximum ranges
- Allowed values for categorical columns

### Reports
- JSON report with report version, counts, configured rules, findings, and recommendations
- CSV export of findings
- Inspectable affected rows for each finding

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1`.

## Run tests

```bash
pytest -q
```

## Privacy and limitations

- Validation is deterministic and runs locally in the app process.
- The uploaded CSV is not sent to an external AI provider.
- A potential outlier is a review candidate, not automatically an error.
- Custom rules are selected for each uploaded file and are not saved between sessions.
- Rule configuration uses column names from the uploaded CSV.

## Project structure

```text
ai-data-quality-assistant/
├── app.py
├── data_quality.py
├── requirements.txt
├── README.md
├── sample_data/
│   └── customers.csv
└── tests/
    └── test_data_quality.py
```

## Portfolio summary

**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream data pipelines.

**Approach:** A repeatable first-pass profiling workflow that detects common issues, lets users define business constraints, surfaces affected records, and exports structured reports.

**Skills demonstrated:** Python, pandas, data validation, unit testing, Streamlit, rule-based profiling, and report generation.

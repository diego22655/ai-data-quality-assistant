# AI Data Quality Assistant

A small portfolio project that helps analysts inspect CSV files for common data-quality issues. It combines transparent, reproducible validation rules with a simple Streamlit interface.

> **Current scope:** The current version uses deterministic, rule-based checks. It does **not** call an AI model yet. The name describes the planned direction; the README and demo are explicit about what is implemented today.

## Features

- Upload a CSV file in a browser interface
- Detect missing values
- Detect exact duplicate rows
- Flag repeated values in likely identifier columns (such as `customer_id` or `email`)
- Flag inconsistent column naming conventions
- Flag potential numeric outliers using the 1.5 × IQR rule
- Inspect affected rows and download JSON/CSV reports
- Provide recommendations that explain the checks and their limitations

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Install dependencies and launch the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in your terminal (usually `http://localhost:8501`).

## Try the sample data

Upload `sample_data/customers.csv` from the app. It intentionally includes examples of missing values, duplicate records, repeated customer IDs, inconsistent column names, and a potential outlier.

## Checks and limitations

- A missing value is not always invalid; business context determines the correct treatment.
- Repeated IDs are flagged only when column names resemble identifiers. This is a heuristic, not a schema guarantee.
- IQR outliers are review candidates, not automatic errors.
- The app does not modify or overwrite uploaded source data.
- No data is intentionally sent to an external service by this application.
- This version does not use a generative AI API. AI-based explanations can be added later as a separate, clearly labeled feature.

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

## Next improvements

1. Add configurable rules per column (required fields, allowed ranges, uniqueness).
2. Add unit tests and continuous integration.
3. Add optional AI explanations with an explicit user-provided API key, after reviewing privacy and cost implications.
4. Add a deployed demo so reviewers can try the workflow without installing Python.

## Portfolio summary

**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream pipelines.

**Approach:** Provide a repeatable first-pass validation workflow that identifies common issues, surfaces affected records, and exports findings for review.

**Skills demonstrated:** Python, pandas, data validation, ETL concepts, reporting, and lightweight app development.

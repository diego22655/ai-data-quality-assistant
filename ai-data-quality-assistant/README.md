# AI Data Quality Assistant

A portfolio project that helps analysts inspect CSV files for common data-quality issues. It combines transparent validation rules, a Streamlit interface, downloadable reports, automated tests, and an optional AI explanation feature.

## Features

- Upload a CSV file through a browser interface
- Detect missing values, exact duplicate rows, repeated values in likely identifier columns, inconsistent column names, and potential numeric outliers using the IQR rule
- Inspect affected rows and download JSON/CSV reports
- Run automated tests for the validation logic and report generation
- Optionally generate a natural-language explanation from summarized findings using the OpenAI API

## Important implementation details

- Rule-based checks are deterministic and remain the source of truth.
- The AI feature is optional and requires an API key configured as a Streamlit secret named `OPENAI_API_KEY`.
- The application sends only summarized findings and recommendations to the model—not the uploaded CSV rows.
- Never commit API keys to GitHub. API usage may incur charges depending on your provider account and current pricing.
- A potential outlier is not automatically an error; review it with business context.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

## Enable AI explanations

For local development, set an environment variable named `OPENAI_API_KEY` before running Streamlit. For Streamlit Community Cloud, open the app's settings and add this under **Secrets**:

```toml
OPENAI_API_KEY = "your_api_key_here"
```

Use your own valid API key. Do not paste it into source code or commit it to the repository. The app continues to work without a key; the AI button remains disabled.

## Try the sample data

Upload `sample_data/customers.csv`. It intentionally includes missing values, duplicate rows, repeated identifiers, inconsistent column names, and a potential numeric outlier.

## Project structure

```text
ai-data-quality-assistant/
├── app.py
├── ai_explainer.py
├── data_quality.py
├── requirements.txt
├── README.md
├── sample_data/
│   └── customers.csv
└── tests/
    └── test_data_quality.py
```

## Portfolio summary

**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream pipelines.

**Approach:** Provide a repeatable first-pass validation workflow that identifies common issues, surfaces affected records, exports findings, and optionally explains the findings in plain language.

**Skills demonstrated:** Python, pandas, data validation, testing, reporting, Streamlit, API integration, and responsible handling of API credentials.

# 🔎 AI Data Quality Assistant

A lightweight CSV data-quality profiling tool built with **Python, pandas, and Streamlit**. It detects common data-quality issues, applies configurable business rules, identifies affected records, and generates downloadable reports.

The project demonstrates a reproducible, rule-based approach to data validation without requiring a paid AI API.

## 🚀 Features

- **Standard data-quality checks:** missing values, duplicate rows, repeated identifiers, inconsistent column names, and potential numeric outliers using the Interquartile Range (IQR) method.
- **Configurable business rules:** required columns, unique columns, numeric ranges, and allowed categorical values.
- **Finding identification:** sequential IDs unique across standard and custom findings.
- **Severity classification:** High, Medium, and Low.
- **Overall quality status:** `PASS`, `PASS WITH WARNINGS`, or `FAIL`.
- **Affected-record inspection:** review the rows associated with each finding.
- **Report exports:** download a detailed JSON report and a CSV findings file.
- **Automated tests:** validate standard checks, custom rules, severity classification, report serialization, and global finding IDs.

## 🛠️ Technology stack

- Python
- pandas
- Streamlit
- pytest
- JSON and CSV

## ⚙️ Run locally

**Requirements:** Python 3.10 or newer.

### 1. Clone the repository

```bash
git clone https://github.com/diego22655/ai-data-quality-assistant.git
cd ai-data-quality-assistant
```

### 2. Create and activate a virtual environment

macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## 🧪 Run automated tests

With the virtual environment activated, run:

```bash
python -m pytest -q
```

The test suite covers standard data-quality checks, configurable validation rules, severity and status logic, JSON serialization, and uniqueness of finding IDs across standard and custom checks.

## 📊 Quality status logic

- **PASS:** no findings were detected by the configured checks.
- **PASS WITH WARNINGS:** findings exist, but none has High severity.
- **FAIL:** at least one High-severity finding exists.

These are example defaults and should be adapted to the business requirements of each data pipeline.

## 🔐 Privacy and limitations

- Uploaded records are analyzed locally within the application's processing flow and are not sent to an external AI service by this tool.
- Potential outliers are flagged for review; they are not automatically classified as errors.
- Custom rules are selected for each uploaded file and are not persisted between sessions.
- The application provides deterministic, rule-based analysis. Generative AI explanations are not currently required for the core functionality.

## 💡 Project overview

**Problem:** Data-quality issues can silently affect analytics, dashboards, and downstream data pipelines.

**Solution:** A repeatable profiling workflow that detects common issues, applies configurable business constraints, highlights affected records, and exports structured quality reports.

**Skills demonstrated:** Python, pandas, data validation, unit testing, Streamlit application development, rule-based profiling, and report generation.

## 🔗 Links

- **Source code:** https://github.com/diego22655/ai-data-quality-assistant
- **Live application:** https://ant-e9eyd9awuscspx2kyyilrf.streamlit.app

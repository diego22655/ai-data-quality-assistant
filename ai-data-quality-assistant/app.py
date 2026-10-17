import io
import json

import pandas as pd
import streamlit as st

from data_quality import analyze_dataframe, build_summary, validate_with_rules

st.set_page_config(page_title="AI Data Quality Assistant", page_icon="🔎", layout="wide")
st.title("🔎 AI Data Quality Assistant")
st.write(
    "A lightweight data-quality profiler for CSV files. Run standard checks, optionally configure "
    "column-level rules, inspect affected records, and export a report."
)

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded is None:
    st.info("Upload a CSV file to begin. You can use `sample_data/customers.csv` from the repository.")
    st.subheader("Standard checks")
    st.markdown(
        "- Missing values\n- Duplicate rows\n- Repeated values in likely identifier columns\n"
        "- Inconsistent column names\n- Potential numeric outliers (IQR)"
    )
    st.subheader("Custom rules")
    st.markdown(
        "- Required columns\n- Unique columns\n- Numeric minimum and maximum values\n"
        "- Allowed values for categorical columns"
    )
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as exc:
    st.error(f"Could not read this CSV file: {exc}")
    st.stop()

if df.empty:
    st.warning("The CSV has column headers but no data rows.")
    st.stop()

st.subheader("Configure column-level rules")
available_columns = [str(c) for c in df.columns]
with st.expander("Required columns", expanded=True):
    required_columns = st.multiselect(
        "These columns must not contain missing values",
        options=available_columns,
        help="Rows with missing values in selected columns will be reported.",
    )
with st.expander("Unique columns"):
    unique_columns = st.multiselect(
        "These columns should contain unique values",
        options=available_columns,
        help="Repeated non-empty values will be reported.",
    )
with st.expander("Numeric ranges"):
    numeric_columns = [str(c) for c in df.select_dtypes(include="number").columns]
    range_columns = st.multiselect("Select numeric columns to constrain", options=numeric_columns)
    numeric_ranges = {}
    for col in range_columns:
        c1, c2 = st.columns(2)
        min_val = c1.number_input(f"{col}: minimum", value=float(df[col].min()) if df[col].notna().any() else 0.0, key=f"min_{col}")
        max_val = c2.number_input(f"{col}: maximum", value=float(df[col].max()) if df[col].notna().any() else 100.0, key=f"max_{col}")
        numeric_ranges[col] = {"min": min_val, "max": max_val}
with st.expander("Allowed categorical values"):
    categorical_columns = [str(c) for c in df.columns if df[c].dtype == "object"]
    allowed_columns = st.multiselect("Select columns with allowed values", options=categorical_columns)
    allowed_values = {}
    for col in allowed_columns:
        raw = st.text_input(
            f"Allowed values for {col} (comma-separated)",
            placeholder="e.g. Peru, Chile, Colombia",
            key=f"allowed_{col}",
        )
        allowed_values[col] = [value.strip() for value in raw.split(",") if value.strip()]

rules = {
    "required_columns": required_columns,
    "unique_columns": unique_columns,
    "numeric_ranges": numeric_ranges,
    "allowed_values": allowed_values,
}

standard_findings, standard_details = analyze_dataframe(df)
custom_findings, custom_details = validate_with_rules(df, rules)
issues = standard_findings + custom_findings
details = {**standard_details, **custom_details}
summary = build_summary(df, issues)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{len(df.columns):,}")
col3.metric("Issue types", len(issues))
col4.metric("Total findings", sum(item["count"] for item in issues))

st.subheader("Data preview")
st.dataframe(df.head(100), use_container_width=True)

st.subheader("Quality report")
if issues:
    report_df = pd.DataFrame(issues)
    st.dataframe(report_df, use_container_width=True)
else:
    st.success("No issues were detected by the standard checks or the custom rules.")

st.subheader("Recommended next steps")
for recommendation in summary["recommendations"]:
    st.markdown(f"- {recommendation}")

if details:
    st.subheader("Affected rows / values")
    chosen = st.selectbox("Choose a finding to inspect", options=list(details.keys()))
    st.dataframe(details[chosen], use_container_width=True)

report = {
    "report_version": "1.0",
    "row_count": int(len(df)),
    "column_count": int(len(df.columns)),
    "standard_issue_count": len(standard_findings),
    "custom_issue_count": len(custom_findings),
    "total_issue_types": len(issues),
    "total_findings": int(sum(item["count"] for item in issues)),
    "rules": rules,
    "findings": issues,
    "recommendations": summary["recommendations"],
}
json_bytes = json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")
csv_buffer = io.StringIO()
pd.DataFrame(issues, columns=["issue", "column", "count", "details"]).to_csv(csv_buffer, index=False)

st.subheader("Export reports")
c1, c2 = st.columns(2)
c1.download_button(
    "Download full report (JSON)",
    data=json_bytes,
    file_name="data_quality_report.json",
    mime="application/json",
    use_container_width=True,
)
c2.download_button(
    "Download findings (CSV)",
    data=csv_buffer.getvalue(),
    file_name="data_quality_findings.csv",
    mime="text/csv",
    use_container_width=True,
)

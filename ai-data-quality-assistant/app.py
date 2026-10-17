import io
import json

import pandas as pd
import streamlit as st

from data_quality import analyze_dataframe, build_quality_status, build_summary, validate_with_rules

st.set_page_config(page_title="AI Data Quality Assistant", page_icon="🔎", layout="wide")
st.title("🔎 AI Data Quality Assistant")
st.write(
    "A lightweight data-quality profiler for CSV files. Run standard checks, configure "
    "column-level rules, inspect affected records, and export a structured report."
)

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded is None:
    st.info("Upload a CSV file to begin. You can use `sample_data/customers.csv` from the repository.")
    st.subheader("Standard checks")
    st.markdown("- Missing values\n- Duplicate rows\n- Repeated values in likely identifier columns\n- Inconsistent column names\n- Potential numeric outliers (IQR)")
    st.subheader("Custom rules")
    st.markdown("- Required columns\n- Unique columns\n- Numeric minimum/maximum ranges\n- Allowed categorical values")
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
columns = [str(c) for c in df.columns]
with st.expander("Required columns"):
    required_columns = st.multiselect("These columns must not contain missing values", columns)
with st.expander("Unique columns"):
    unique_columns = st.multiselect("These columns should contain unique values", columns)
with st.expander("Numeric ranges"):
    numeric_columns = [str(c) for c in df.select_dtypes(include="number").columns]
    range_columns = st.multiselect("Select numeric columns to constrain", numeric_columns)
    numeric_ranges = {}
    for col in range_columns:
        values = df[col].dropna()
        default_min = float(values.min()) if not values.empty else 0.0
        default_max = float(values.max()) if not values.empty else 100.0
        c1, c2 = st.columns(2)
        min_val = c1.number_input(f"{col}: minimum", value=default_min, key=f"min_{col}")
        max_val = c2.number_input(f"{col}: maximum", value=default_max, key=f"max_{col}")
        if min_val > max_val:
            st.warning(f"Minimum for {col} cannot exceed its maximum. This range will not be applied.")
        else:
            numeric_ranges[col] = {"min": min_val, "max": max_val}
with st.expander("Allowed categorical values"):
    categorical_columns = [str(c) for c in df.columns if df[c].dtype == "object"]
    allowed_columns = st.multiselect("Select columns with allowed values", categorical_columns)
    allowed_values = {}
    for col in allowed_columns:
        raw = st.text_input(f"Allowed values for {col} (comma-separated)", placeholder="e.g. Peru, Chile, Colombia", key=f"allowed_{col}")
        allowed_values[col] = [v.strip() for v in raw.split(",") if v.strip()]

rules = {
    "required_columns": required_columns,
    "unique_columns": unique_columns,
    "numeric_ranges": numeric_ranges,
    "allowed_values": allowed_values,
}
standard_findings, standard_details = analyze_dataframe(df)
custom_findings, custom_details = validate_with_rules(df, rules)
findings = standard_findings + custom_findings
details = {**standard_details, **custom_details}
summary = build_summary(df, findings)
status = build_quality_status(findings)

st.subheader("Quality status")
if status == "FAIL":
    st.error(f"FAIL — {len(findings)} finding type(s) require review.")
elif status == "PASS WITH WARNINGS":
    st.warning(f"PASS WITH WARNINGS — {len(findings)} finding type(s) detected.")
else:
    st.success("PASS — no issues detected by the configured checks.")

# Count distinct source rows represented in row-level details; metadata-only findings are excluded.
affected_indices = set()
for key, frame in details.items():
    if set(df.columns).issubset(set(frame.columns)):
        affected_indices.update(frame.index.tolist())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", f"{len(df.columns):,}")
c3.metric("Finding types", len(findings))
c4.metric("Distinct affected rows", len(affected_indices))

st.subheader("Data preview")
st.dataframe(df.head(100), use_container_width=True)
st.subheader("Quality report")
if findings:
    st.dataframe(pd.DataFrame(findings)[["finding_id", "severity", "issue", "column", "count", "details"]], use_container_width=True)
else:
    st.success("No issues were detected by the standard checks or custom rules.")

st.subheader("Recommended next steps")
for recommendation in summary["recommendations"]:
    st.markdown(f"- {recommendation}")

if details:
    st.subheader("Affected rows / values")
    chosen = st.selectbox("Choose a finding to inspect", options=list(details.keys()))
    st.dataframe(details[chosen], use_container_width=True)

report = {
    "report_version": "2.0",
    "status": status,
    "row_count": int(len(df)),
    "column_count": int(len(df.columns)),
    "standard_issue_count": len(standard_findings),
    "custom_issue_count": len(custom_findings),
    "total_issue_types": len(findings),
    "total_findings": int(sum(item["count"] for item in findings)),
    "distinct_affected_rows": len(affected_indices),
    "rules": rules,
    "findings": findings,
    "recommendations": summary["recommendations"],
}
json_data = json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")
csv_buffer = io.StringIO()
pd.DataFrame(findings, columns=["finding_id", "severity", "issue", "column", "count", "details"]).to_csv(csv_buffer, index=False)
st.subheader("Export reports")
c1, c2 = st.columns(2)
c1.download_button("Download full report (JSON)", data=json_data, file_name="data_quality_report.json", mime="application/json", use_container_width=True)
c2.download_button("Download findings (CSV)", data=csv_buffer.getvalue(), file_name="data_quality_findings.csv", mime="text/csv", use_container_width=True)

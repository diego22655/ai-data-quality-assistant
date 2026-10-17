import io
import pandas as pd
import streamlit as st
from data_quality import analyze_dataframe, build_summary

st.set_page_config(page_title="AI Data Quality Assistant", page_icon="🔎", layout="wide")
st.title("🔎 AI Data Quality Assistant")
st.write(
    "Upload a CSV file to detect common data-quality issues, review affected rows, "
    "and download a report. Checks are rule-based and reproducible; AI-generated explanations "
    "can be added as a future extension."
)

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded is None:
    st.info("No file uploaded yet. Try the sample file in the GitHub repository: `sample_data/customers.csv`.")
    st.subheader("What this tool checks")
    st.markdown("- Missing values\n- Duplicate rows\n- Duplicate values in likely identifier columns\n- Potentially inconsistent column names\n- Basic numeric outliers using the IQR rule")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as exc:
    st.error(f"Could not read this CSV file: {exc}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV has no data rows.")
    st.stop()

issues, details = analyze_dataframe(df)
summary = build_summary(df, issues)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{len(df.columns):,}")
col3.metric("Issue types", len(issues))
col4.metric("Total findings", sum(item["count"] for item in issues))

st.subheader("Data preview")
st.dataframe(df.head(100), use_container_width=True)

st.subheader("Quality summary")
st.dataframe(pd.DataFrame(issues) if issues else pd.DataFrame([{"issue": "No issues detected", "column": "—", "count": 0, "details": "The configured checks found no issues."}]), use_container_width=True)

st.subheader("Recommended next steps")
for recommendation in summary["recommendations"]:
    st.markdown(f"- {recommendation}")

if details:
    st.subheader("Affected rows / values")
    chosen = st.selectbox("Choose a finding to inspect", options=list(details.keys()))
    st.dataframe(details[chosen], use_container_width=True)

report = {
    "row_count": int(len(df)),
    "column_count": int(len(df.columns)),
    "issue_type_count": int(len(issues)),
    "findings": issues,
    "recommendations": summary["recommendations"],
}
st.download_button(
    "Download quality report (JSON)",
    data=json.dumps(report, indent=2, ensure_ascii=False),
    file_name="data_quality_report.json",
    mime="application/json",
)
csv_buffer = io.StringIO()
pd.DataFrame(issues).to_csv(csv_buffer, index=False)
st.download_button(
    "Download findings (CSV)",
    data=csv_buffer.getvalue(),
    file_name="data_quality_findings.csv",
    mime="text/csv",
)

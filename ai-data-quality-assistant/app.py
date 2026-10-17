import io
import json
import os

import pandas as pd
import streamlit as st

from data_quality import analyze_dataframe, build_summary
from ai_explainer import explain_findings

st.set_page_config(page_title="AI Data Quality Assistant", page_icon="🔎", layout="wide")
st.title("🔎 AI Data Quality Assistant")
st.write(
    "Upload a CSV file to detect common data-quality issues, inspect affected rows, "
    "and download a report. Deterministic rules identify findings; an optional AI explanation "
    "can help summarize them when an API key is configured."
)

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded is None:
    st.info("No file uploaded yet. Try `sample_data/customers.csv` from the GitHub repository.")
    st.subheader("What this tool checks")
    st.markdown(
        "- Missing values\n- Duplicate rows\n- Repeated values in likely identifier columns\n"
        "- Inconsistent column names\n- Potential numeric outliers using the IQR rule"
    )
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
quality_df = pd.DataFrame(issues) if issues else pd.DataFrame(
    [{"issue": "No issues detected", "column": "—", "count": 0,
      "details": "The configured checks found no issues."}]
)
st.dataframe(quality_df, use_container_width=True)

st.subheader("Recommended next steps")
for recommendation in summary["recommendations"]:
    st.markdown(f"- {recommendation}")

if details:
    st.subheader("Affected rows / values")
    chosen = st.selectbox("Choose a finding to inspect", options=list(details.keys()))
    st.dataframe(details[chosen], use_container_width=True)

st.subheader("AI explanation (optional)")
st.caption(
    "The rule-based findings above are the source of truth. The optional AI feature summarizes "
    "those findings; it does not replace validation. Configure OPENAI_API_KEY in Streamlit Secrets "
    "to enable it. Only the findings summary—not the uploaded rows—is sent to the model."
)
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
if api_key:
    if st.button("Explain findings with AI"):
        with st.spinner("Generating explanation..."):
            try:
                explanation = explain_findings(issues, summary["recommendations"], api_key)
                st.markdown(explanation)
            except Exception:
                st.error(
                    "The AI explanation could not be generated. Check the API key, account access, "
                    "and API usage limits in your provider dashboard."
                )
else:
    st.info("AI explanation is disabled until an API key is configured. The data-quality checks work without it.")

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

import pandas as pd
import streamlit as st

def footer_data(total_conf, num_questions, final_report):
    avg_confidence = total_conf / num_questions
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Average Confidence", f"{avg_confidence:.1f}%")
    col2.metric("Total Requirements Audited", num_questions)

    df_report = pd.DataFrame(final_report)

    csv = df_report.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Audit Report (CSV)",
        data=csv,
        file_name="compliance_audit_report.csv",
        mime="text/csv",
    )
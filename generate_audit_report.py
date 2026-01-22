import time
import streamlit as st
from run_audit_check import run_audit_check

def generate_audit_report(questions, policy_filenames):
    final_report = []
    total_conf = 0
    for i, q in enumerate(questions):
        with st.status(f"Checking Requirement {i + 1}: {q}"):
            time.sleep(2.0)
            finding = run_audit_check(
                q,
                st.session_state.vectorstore,
                st.session_state.store,
                policy_filenames
            )
            total_conf += finding.confidence
            st.write({
                "ID": i + 1,
                "Requirement": q,
                "Met": "✅" if "MET" in finding.status.upper() and "UNMET" not in finding.status.upper() else "❌",
                "Confidence": finding.confidence,
                "Evidence": finding.evidence,
                "Citations": finding.citations,
            })
            final_report.append({
                "ID": i + 1,
                "Requirement": q,
                "Met": "✅" if "MET" in finding.status.upper() and "UNMET" not in finding.status.upper() else "❌",
                "Confidence": finding.confidence,
                "Evidence": finding.evidence,
                "Citations": finding.citations,
            })
    return final_report, total_conf
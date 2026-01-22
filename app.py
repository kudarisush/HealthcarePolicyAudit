
import streamlit as st
from langchain_classic.chains import RetrievalQA

from qa_chain_prompt import QA_CHAIN_PROMPT
from footer_data import footer_data
from generate_audit_report import generate_audit_report
from load_raw_questions import load_raw_questions
from policy_file_processing import policy_file_processing
from utils import extract_questions_to_list
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Compliance Auditor", layout="wide")
st.title("Healthcare Regulatory Audit Tool")

db_exists = os.path.exists("./audit_db_storage") and os.path.exists("./parent_doc_store")

with st.sidebar:
    st.header("Setup")
    load_dotenv()
    # api_key = os.getenv("GOOGLE_API_KEY")
    api_key = st.text_input("Enter Google API Key", type="password")

    policy_pdfs = st.file_uploader(
        "Upload Policy Manuals -- NOT AUDIT QUESTIONS",
        type="pdf",
        accept_multiple_files=True
    )

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

policy_file_processing(policy_pdfs, api_key, QA_CHAIN_PROMPT)

if st.session_state.qa_chain or db_exists:
    if st.session_state.qa_chain is None:
        policy_file_processing(policy_pdfs, api_key, QA_CHAIN_PROMPT)

    st.header("Upload Requirements")
    audit_pdf = st.file_uploader("Upload the list of Audit Questions (PDF)", type="pdf")
    policy_filenames = [f.name for f in policy_pdfs]

    if audit_pdf:
        raw_audit_text = load_raw_questions(audit_pdf)
        if st.button("Analyze Questions"):
            if st.session_state.llm is None:
                st.error("Audit Engine not ready")
            questions = extract_questions_to_list(raw_audit_text, st.session_state.llm)
            if questions:
                final_report,total_conf = generate_audit_report(questions, policy_filenames)

                #display confidence and download report
                footer_data(total_conf, len(questions), final_report)
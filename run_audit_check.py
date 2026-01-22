import streamlit as st
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from auditFinding import AuditFinding

def run_audit_check(question, vectorstore, store, policy_filenames):
    all_docs = []
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=150)

    for filename in policy_filenames:
        doc_retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            search_type="mmr",
            search_kwargs={"k": 10, "filter": {"source": filename}, "fetch_k": 30},
            child_splitter = child_splitter,
            parent_splitter = parent_splitter,
        )
        all_docs.extend(doc_retriever.invoke(question))

    if "reranker" in st.session_state and all_docs:
        docs = st.session_state.reranker.compress_documents(all_docs, question)
        docs = docs[:8]
    else:
        docs = all_docs[:8]


    log_info = [f"{d.metadata.get('source')} (Pg {d.metadata.get('page')})" for d in docs]
    print(f"Audit Query: {question[:50]}... | Evidence: {log_info}")


    unique_citations = []
    seen = set()
    for d in docs:
        file_name = d.metadata.get('source', 'Unknown').split('/')[-1]
        page_num = d.metadata.get('page', 0)
        if (file_name, page_num) not in seen:
            unique_citations.append({"file_name": file_name, "page": page_num})
            seen.add((file_name, page_num))


    context = "\n\n".join([d.page_content for d in docs])
    structured_llm = st.session_state.llm.with_structured_output(AuditFinding)

    prompt = f"""You are a strict Healthcare Compliance Auditor.
    TASK: Analyze the provided POLICY CONTEXT to verify: "{question}"

    STRICT RULES:
    - IGNORE sections that only contain Table of Contents or General Definitions if a specific procedural instruction exists in the other provided sections.
    - If specific procedural details (like days, timeframes, or specific forms) are missing, score CONFIDENCE below 70.
    - If the context contains definitions but no actual "must/shall" requirement, mark as PARTIAL.
    - Use only the provided context.

    CITATIONS: {unique_citations}
    CONTEXT:
    {context}
    """

    return structured_llm.invoke(prompt)
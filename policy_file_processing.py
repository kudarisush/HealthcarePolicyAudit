import streamlit as st
import os
import tempfile
import shutil
import random
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.retrievers.multi_vector import SearchType
from langchain_classic.storage import LocalFileStore, create_kv_docstore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_classic.retrievers.document_compressors import FlashrankRerank
from flashrank import Ranker
from batch_add_document import batch_add_documents

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "audit_db_storage")
FLASH_CACHE_DIR = os.path.join(os.getcwd(), "flashrank_cache")
PARENT_STORE_DIR = os.path.join(BASE_DIR, "parent_doc_store")

if not os.path.exists(FLASH_CACHE_DIR):
    os.makedirs(FLASH_CACHE_DIR)

def policy_file_processing(policy_pdfs, api_key, QA_CHAIN_PROMPT):
    if not (policy_pdfs and api_key):
        return

    if st.session_state.llm is None:
        st.session_state.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key
        )

    if "reranker" not in st.session_state:
        flashrank_client = Ranker(model_name="ms-marco-MultiBERT-L-12", cache_dir=FLASH_CACHE_DIR)
        st.session_state.reranker = FlashrankRerank(client=flashrank_client, top_n=10)

    if not os.path.exists(PARENT_STORE_DIR):
        os.makedirs(PARENT_STORE_DIR)

    fs = LocalFileStore(PARENT_STORE_DIR)
    local_store = create_kv_docstore(fs)

    # embedding language model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        task_type="retrieval_document",
        google_api_key = api_key,
    )

    # vector database
    vectorstore = Chroma(
        collection_name="split_parents",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )

    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, add_start_index=True)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=150)

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=local_store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        search_type=SearchType.mmr,
        search_kwargs = {"k": 100, "lambda_mult": 0.25, "fetch_k": 200}
    )

    st.session_state.store = local_store
    random.shuffle(policy_pdfs)

    if st.session_state.qa_chain is None:
        with st.status("Audit Engine: Checking Database...") as status:
            existing_keys = list(local_store.yield_keys())
            st.write(existing_keys)
            if not existing_keys:
                all_docs = []
                files_processed = 0
                for uploaded_file in policy_pdfs:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name

                    loader = PyPDFLoader(tmp_path)
                    loaded_docs = loader.load()

                    for doc in loaded_docs:
                        page_num = doc.metadata.get('page', 0) + 1

                        doc.metadata["source"] = uploaded_file.name
                        doc.metadata["page"] = page_num

                        breadcrumb = f"SECTION: {uploaded_file.name} | Page {page_num}\n"
                        doc.page_content = breadcrumb + doc.page_content

                    all_docs.extend(loaded_docs)
                    os.remove(tmp_path)
                    files_processed += 1
                batch_add_documents(retriever, all_docs, batch_size=5)
                st.write(files_processed)
            else:
                status.update(label="Loaded DB", state="complete")

            st.session_state.qa_chain = RetrievalQA.from_chain_type(
                llm=st.session_state.llm,
                retriever=retriever,
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
            )
            st.session_state.vectorstore = vectorstore
            st.success("Ready!")

def reset_audit_database():
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    st.session_state.qa_chain = None
    st.session_state.vectorstore = None
    st.rerun()
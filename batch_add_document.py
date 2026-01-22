import time
import streamlit as st
import re
from collections import Counter

def batch_add_documents(retriever, docs, batch_size=10):  # Slightly larger batch for efficiency
    if not docs:
        st.warning("No documents to ingest.")
        return

    seen_pages = set()
    unique_docs = []
    for d in docs:
        page_id = f"{d.metadata.get('source')}_pg_{d.metadata.get('page')}"
        if page_id not in seen_pages:
            unique_docs.append(d)
            seen_pages.add(page_id)

    docs = unique_docs

    progress_text = "Ingesting unique policy pages..."
    my_bar = st.progress(0, text=progress_text)
    total_batches = (len(docs) + batch_size - 1) // batch_size

    page_counts = Counter([d.metadata.get('page', 0) for d in docs])
    st.write(f"Flattened Ingestion: {len(docs)} unique pages. Top page counts: {dict(list(page_counts.items())[:5])}")

    for i in range(0, len(docs), batch_size):
        batch = docs[i: i + batch_size]
        success = False
        retries = 0

        while not success and retries < 5:
            try:
                retriever.add_documents(batch)
                success = True
                time.sleep(1.5)
            except Exception as e:
                error_msg = str(e)

                if "1032" in error_msg or "readonly" in error_msg:
                    retries += 1
                    st.warning(f"Database locked. Retrying batch {i // batch_size}... ({retries}/5)")
                    time.sleep(5 * retries)
                    # Handle Gemini/Google Rate Limits
                elif "429" in error_msg:
                    retries += 1
                    wait_match = re.search(r"retry in (\d+\.?\d*)s", error_msg)
                    wait_time = float(wait_match.group(1)) + 2.0 if wait_match else (20 * retries)
                    st.warning(f"Embedding Rate limit hit. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    st.error(f"Critical Ingestion Error: {e}")
                    raise e

        current_batch = (i // batch_size) + 1
        my_bar.progress(current_batch / total_batches, text=f"Processing Batch {current_batch}/{total_batches}")

    my_bar.empty()
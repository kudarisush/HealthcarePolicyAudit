from langchain_community.document_loaders import PyPDFLoader
import tempfile

def load_raw_questions(audit_pdf) :
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(audit_pdf.getvalue())
        path = tmp.name
    loader = PyPDFLoader(path)
    raw_audit_text = "\n".join([p.page_content for p in loader.load()])

    return raw_audit_text
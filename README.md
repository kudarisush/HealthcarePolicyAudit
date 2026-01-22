# Healthcare Policy Audit System #
An AI-powered auditing tool designed to process healthcare policy documents, store them in a vector database, and perform automated checks against regulatory questions using a RAG (Retrieval-Augmented Generation) pipeline.

# Installation
Clone the repository:

```
git clone git@github.com:kudarisush/HealthcarePolicyAudit.git
cd HealthcarePolicyAudit
```

Install dependencies:
``` pip install -r requirements.txt ```

## 📋 Usage
Run:
``` streamlit run app.py ```

Data Isolation: The Public Policies folder and audit_db_storage are included in .gitignore to prevent sensitive healthcare data from being uploaded to version control.

# Key Management: #  
Never commit your .env file.
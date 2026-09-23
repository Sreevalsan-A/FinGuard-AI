from langchain_community.document_loaders import PyPDFLoader


PDF_PATH = "data/documents/finance_policy.pdf"


def load_finance_document():
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print(f"Loaded {len(documents)} pages.")

    return documents
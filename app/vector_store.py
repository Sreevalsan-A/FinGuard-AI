import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTOR_STORE_PATH = "data/vectorstore"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vector_store(chunks):
    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    vector_store.save_local(VECTOR_STORE_PATH)

    print("Vector store created and saved successfully.")

    return vector_store


def load_vector_store():
    embeddings = get_embeddings()

    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("Existing vector store loaded successfully.")

    return vector_store
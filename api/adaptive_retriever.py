from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers import ContextualCompressionRetriever

# ✅ Explicit model name to avoid deprecation
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)

def get_adaptive_retriever(query: str):
    raw_docs = vectorstore.get()["documents"]
    documents = [Document(page_content=doc, metadata={}) for doc in raw_docs]

    if not documents:
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 6

    dense = vectorstore.as_retriever(search_kwargs={"k": 6})

    hybrid = ContextualCompressionRetriever(
        base_retriever=dense,
        base_compressor=EmbeddingsFilter(
            embeddings=embedding_model,
            similarity_threshold=0.7
        )
    )

    if len(query.split()) < 4:
        return bm25
    elif "compare" in query.lower():
        return hybrid
    else:
        return dense
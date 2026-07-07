from pdf_assistant.config import (
    CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
    TOP_K,
)
from pdf_assistant.embeddings.embedding_model import EmbeddingModel
from pdf_assistant.retriever.vector_store import VectorStore


class RetrieverService:
    def __init__(self):
        self.embedding_model = EmbeddingModel(
            EMBEDDING_MODEL_NAME
        )

        self.vector_store = VectorStore()
        self.vector_store.load(
            FAISS_INDEX_PATH,
            CHUNKS_PATH,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
    ):
        embedding = self.embedding_model.encode([query])

        return self.vector_store.search(
            embedding,
            top_k,
        )
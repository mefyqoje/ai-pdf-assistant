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
        self.embedding_model = EmbeddingModel(EMBEDDING_MODEL_NAME)
        self.vector_store = None

    def _load_vector_store(self):
        if self.vector_store is None:
            vector_store = VectorStore()
            vector_store.load(
                FAISS_INDEX_PATH,
                CHUNKS_PATH,
            )
            self.vector_store = vector_store

    def reload(self):
        self.vector_store = None
        self._load_vector_store()

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
    ):
        self._load_vector_store()

        embedding = self.embedding_model.encode([query])

        return self.vector_store.search(
            embedding,
            top_k,
        )
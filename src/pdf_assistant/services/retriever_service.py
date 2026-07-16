from pdf_assistant.config import (
    CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
    RERANK_TOP_K,
    RETRIEVAL_TOP_K,
)
from pdf_assistant.embeddings.embedding_model import (
    EmbeddingModel,
)
from pdf_assistant.retriever.vector_store import (
    VectorStore,
)
from pdf_assistant.services.reranker_service import (
    RerankerService,
)


class RetrieverService:
    def __init__(self) -> None:
        self.embedding_model = EmbeddingModel(
            EMBEDDING_MODEL_NAME
        )
        self.reranker = RerankerService()
        self.vector_store = None

    def _load_vector_store(self) -> None:
        if self.vector_store is not None:
            return

        vector_store = VectorStore()

        vector_store.load(
            FAISS_INDEX_PATH,
            CHUNKS_PATH,
        )

        self.vector_store = vector_store

    def reload(self) -> None:
        self.vector_store = None
        self._load_vector_store()

    def retrieve(
        self,
        query: str,
        retrieval_top_k: int = RETRIEVAL_TOP_K,
        rerank_top_k: int = RERANK_TOP_K,
    ) -> list[dict]:
        clean_query = query.strip()

        if not clean_query:
            return []

        self._load_vector_store()

        query_embedding = self.embedding_model.encode(
            [clean_query]
        )

        candidates = self.vector_store.search(
            query_embedding,
            top_k=retrieval_top_k,
        )

        return self.reranker.rerank(
            query=clean_query,
            chunks=candidates,
            top_k=rerank_top_k,
        )
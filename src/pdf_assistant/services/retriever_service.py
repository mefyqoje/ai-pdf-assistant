from pdf_assistant.config import (
    BM25_TOP_K,
    CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
    FAISS_TOP_K,
    RERANK_TOP_K,
)
from pdf_assistant.embeddings.embedding_model import (
    EmbeddingModel,
)
from pdf_assistant.retriever.bm25_store import BM25Store
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

        self.vector_store: VectorStore | None = None
        self.bm25_store: BM25Store | None = None

    def _load_stores(self) -> None:
        if (
            self.vector_store is not None
            and self.bm25_store is not None
        ):
            return

        vector_store = VectorStore()
        vector_store.load(
            FAISS_INDEX_PATH,
            CHUNKS_PATH,
        )

        bm25_store = BM25Store()
        bm25_store.build(vector_store.chunks)

        self.vector_store = vector_store
        self.bm25_store = bm25_store

    def reload(self) -> None:
        self.vector_store = None
        self.bm25_store = None
        self._load_stores()

    @staticmethod
    def _chunk_key(chunk: dict) -> tuple:
        return (
            chunk.get("document"),
            chunk.get("page"),
            chunk.get("chunk_id"),
            chunk.get("text"),
        )

    def _merge_candidates(
        self,
        faiss_results: list[dict],
        bm25_results: list[dict],
    ) -> list[dict]:
        merged: dict[tuple, dict] = {}

        for rank, chunk in enumerate(
            faiss_results,
            start=1,
        ):
            key = self._chunk_key(chunk)

            result = chunk.copy()
            result["retrieval_score"] = float(
                chunk.get("score", 0.0)
            )
            result["faiss_rank"] = rank
            result["bm25_score"] = float(
                chunk.get("bm25_score", 0.0)
            )

            merged[key] = result

        for rank, chunk in enumerate(
            bm25_results,
            start=1,
        ):
            key = self._chunk_key(chunk)

            if key in merged:
                merged[key]["bm25_score"] = float(
                    chunk.get("bm25_score", 0.0)
                )
                merged[key]["bm25_rank"] = rank
            else:
                result = chunk.copy()
                result["retrieval_score"] = 0.0
                result["faiss_rank"] = None
                result["bm25_rank"] = rank
                result["bm25_score"] = float(
                    chunk.get("bm25_score", 0.0)
                )

                merged[key] = result

        return list(merged.values())

    def retrieve(
        self,
        query: str,
        faiss_top_k: int = FAISS_TOP_K,
        bm25_top_k: int = BM25_TOP_K,
        rerank_top_k: int = RERANK_TOP_K,
    ) -> list[dict]:
        clean_query = query.strip()

        if not clean_query:
            return []

        self._load_stores()

        if (
            self.vector_store is None
            or self.bm25_store is None
        ):
            return []

        query_embedding = self.embedding_model.encode(
            [clean_query]
        )

        faiss_results = self.vector_store.search(
            query_embedding,
            top_k=faiss_top_k,
        )

        bm25_results = self.bm25_store.search(
            clean_query,
            top_k=bm25_top_k,
        )

        candidates = self._merge_candidates(
            faiss_results=faiss_results,
            bm25_results=bm25_results,
        )

        return self.reranker.rerank(
            query=clean_query,
            chunks=candidates,
            top_k=rerank_top_k,
        )
from sentence_transformers import CrossEncoder

from pdf_assistant.config import (
    RERANK_TOP_K,
    RERANKER_MODEL_NAME,
)


class RerankerService:
    def __init__(
        self,
        model_name: str = RERANKER_MODEL_NAME,
    ) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = RERANK_TOP_K,
    ) -> list[dict]:
        if not chunks:
            return []

        pairs = [
            (
                query,
                chunk["text"],
            )
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        reranked_chunks = []

        for chunk, reranker_score in zip(
            chunks,
            scores,
        ):
            result = chunk.copy()

            # Сохраняем исходный score FAISS.
            result["retrieval_score"] = float(
                chunk.get(
                    "score",
                    0.0,
                )
            )

            # Основным score становится оценка CrossEncoder.
            result["reranker_score"] = float(
                reranker_score
            )
            result["score"] = float(
                reranker_score
            )

            reranked_chunks.append(result)

        reranked_chunks.sort(
            key=lambda item: item["reranker_score"],
            reverse=True,
        )

        actual_top_k = min(
            top_k,
            len(reranked_chunks),
        )

        return reranked_chunks[:actual_top_k]
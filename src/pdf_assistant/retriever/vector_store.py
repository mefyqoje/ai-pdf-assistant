from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(self) -> None:
        self.index = None
        self.chunks = []

    def build(self, embeddings: np.ndarray, chunks: list[dict]) -> None:
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype("float32"))

        self.chunks = chunks

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        if self.index is None:
            raise ValueError("Векторное хранилище еще не создано.")

        scores, indices = self.index.search(
            query_embedding.astype("float32"),
            top_k,
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            chunk = self.chunks[index].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        return results

    def save(self, index_path: str | Path, chunks_path: str | Path) -> None:
        index_path = Path(index_path)
        chunks_path = Path(chunks_path)

        index_path.parent.mkdir(parents=True, exist_ok=True)
        chunks_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))

        np.save(chunks_path, np.array(self.chunks, dtype=object))

    def load(self, index_path: str | Path, chunks_path: str | Path) -> None:
        index_path = Path(index_path)
        chunks_path = Path(chunks_path)

        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index не найден: {index_path}")

        if not chunks_path.exists():
            raise FileNotFoundError(f"Файл чанков не найден: {chunks_path}")

        self.index = faiss.read_index(str(index_path))
        self.chunks = np.load(chunks_path, allow_pickle=True).tolist()
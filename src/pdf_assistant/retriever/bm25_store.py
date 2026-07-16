import re

import numpy as np
from rank_bm25 import BM25Okapi


class BM25Store:
    def __init__(self) -> None:
        self.chunks: list[dict] = []
        self.tokenized_corpus: list[list[str]] = []
        self.index: BM25Okapi | None = None

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return re.findall(
            r"[a-zа-яё0-9]+",
            text.lower(),
            flags=re.IGNORECASE,
        )

    def build(self, chunks: list[dict]) -> None:
        self.chunks = list(chunks)

        self.tokenized_corpus = [
            self.tokenize(chunk.get("text", ""))
            for chunk in self.chunks
        ]

        if not self.tokenized_corpus:
            self.index = None
            return

        self.index = BM25Okapi(self.tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[dict]:
        if self.index is None or not self.chunks:
            return []

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return []

        scores = self.index.get_scores(query_tokens)

        actual_top_k = min(top_k, len(self.chunks))

        best_indices = np.argsort(scores)[::-1][
            :actual_top_k
        ]

        results = []

        for index in best_indices:
            score = float(scores[index])

            if score <= 0:
                continue

            chunk = self.chunks[index].copy()
            chunk["bm25_score"] = score

            results.append(chunk)

        return results
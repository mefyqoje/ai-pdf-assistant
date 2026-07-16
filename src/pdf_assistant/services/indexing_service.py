from pathlib import Path

from pdf_assistant.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKS_PATH,
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
)
from pdf_assistant.embeddings.embedding_model import EmbeddingModel
from pdf_assistant.loaders.pdf_loader import load_pdf_text
from pdf_assistant.retriever.vector_store import VectorStore
from pdf_assistant.splitters.text_splitter import split_pages_into_chunks


class IndexingService:
    def __init__(self) -> None:
        self.embedding_model = EmbeddingModel(
            EMBEDDING_MODEL_NAME
        )

    def index_pdf(
        self,
        pdf_path: str | Path,
    ) -> int:
        pdf_path = Path(pdf_path)

        pages = load_pdf_text(pdf_path)

        chunks = split_pages_into_chunks(
            pages,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        document_name = pdf_path.name

        for chunk in chunks:
            chunk["document"] = document_name

        texts = [chunk["text"] for chunk in chunks]

        if not texts:
            raise ValueError(
                f"В документе {document_name} не найден текст для индексации."
            )

        embeddings = self.embedding_model.encode(texts)

        vector_store = VectorStore()

        try:
            vector_store.load(
                FAISS_INDEX_PATH,
                CHUNKS_PATH,
            )
        except FileNotFoundError:
            pass

        vector_store.add(
            embeddings,
            chunks,
        )

        vector_store.save(
            FAISS_INDEX_PATH,
            CHUNKS_PATH,
        )

        return len(chunks)
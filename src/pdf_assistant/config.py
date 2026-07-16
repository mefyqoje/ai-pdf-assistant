from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"

FAISS_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
CHUNKS_PATH = VECTOR_STORE_DIR / "chunks.npy"

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

RERANKER_MODEL_NAME = (
    "cross-encoder/"
    "mmarco-mMiniLMv2-L12-H384-v1"
)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

FAISS_TOP_K = 20
BM25_TOP_K = 20
RERANK_TOP_K = 5

OLLAMA_MODEL_NAME = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"
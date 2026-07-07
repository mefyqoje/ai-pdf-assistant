from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from pdf_assistant.config import DOCUMENTS_DIR
from pdf_assistant.services.indexing_service import IndexingService
from pdf_assistant.services.qa_service import QAService


app = FastAPI(
    title="AI PDF Assistant API",
    description="API для вопросов по PDF-документу на основе RAG",
    version="1.0.0",
)

qa_service = QAService()
indexing_service = IndexingService()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "AI PDF Assistant API запущен"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Можно загружать только PDF-файлы.",
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DOCUMENTS_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    chunks_count = indexing_service.index_pdf(file_path)

    qa_service.reload_retriever()

    return {
        "message": "PDF успешно загружен и проиндексирован.",
        "filename": file.filename,
        "chunks_count": chunks_count,
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Вопрос не должен быть пустым.",
        )

    result = qa_service.answer(request.question)

    return result
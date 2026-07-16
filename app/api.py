from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from pdf_assistant.config import DOCUMENTS_DIR
from pdf_assistant.services.indexing_service import IndexingService
from pdf_assistant.services.qa_service import QAService


app = FastAPI(
    title="AI PDF Assistant API",
    description="RAG API для вопросов по PDF-документам",
    version="1.1.0",
)

qa_service = QAService()
indexing_service = IndexingService()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class QuestionRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


@app.get("/")
def root():
    return {"message": "AI PDF Assistant API запущен"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-pdf-assistant",
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Не указано имя файла.",
        )

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Можно загружать только PDF-файлы.",
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DOCUMENTS_DIR / filename

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Загруженный файл пуст.",
        )

    with open(file_path, "wb") as file_object:
        file_object.write(content)

    try:
        chunks_count = indexing_service.index_pdf(file_path)
        qa_service.reload_retriever()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка индексации документа: {error}",
        ) from error

    return {
        "message": "PDF успешно загружен и проиндексирован.",
        "filename": filename,
        "chunks_count": chunks_count,
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Вопрос не должен быть пустым.",
        )

    history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in request.history
    ]

    try:
        return qa_service.answer(
            question=question,
            history=history,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=400,
            detail=(
                "База документов еще не создана. "
                "Сначала загрузите хотя бы один PDF."
            ),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка формирования ответа: {error}",
        ) from error
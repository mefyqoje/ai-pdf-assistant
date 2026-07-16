import json
from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from pdf_assistant.config import DOCUMENTS_DIR
from pdf_assistant.services.indexing_service import IndexingService
from pdf_assistant.services.qa_service import QAService


app = FastAPI(
    title="AI PDF Assistant API",
    description="RAG API для вопросов по PDF-документам",
    version="1.2.0",
)

qa_service = QAService()
indexing_service = IndexingService()


class ChatMessage(BaseModel):
    role: str = Field(
        pattern="^(user|assistant)$"
    )
    content: str


class QuestionRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


@app.get("/")
def root():
    return {
        "message": "AI PDF Assistant API запущен"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-pdf-assistant",
    }


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
):
    filename = Path(
        file.filename or ""
    ).name

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

    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        chunks_count = indexing_service.index_pdf(
            file_path
        )
        qa_service.reload_retriever()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Ошибка индексации документа: "
                f"{error}"
            ),
        ) from error

    return {
        "message": (
            "PDF успешно загружен "
            "и проиндексирован."
        ),
        "filename": filename,
        "chunks_count": chunks_count,
    }


def convert_history(
    request: QuestionRequest,
) -> list[dict]:
    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in request.history
    ]


@app.post("/ask")
def ask_question(
    request: QuestionRequest,
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Вопрос не должен быть пустым.",
        )

    try:
        return qa_service.answer(
            question=question,
            history=convert_history(request),
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
            detail=(
                f"Ошибка формирования ответа: "
                f"{error}"
            ),
        ) from error


@app.post("/ask/stream")
def ask_question_stream(
    request: QuestionRequest,
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Вопрос не должен быть пустым.",
        )

    try:
        token_stream, sources, search_query = (
            qa_service.answer_stream(
                question=question,
                history=convert_history(request),
            )
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
            detail=(
                f"Ошибка подготовки ответа: "
                f"{error}"
            ),
        ) from error

    def event_generator():
        metadata = {
            "type": "metadata",
            "sources": sources,
            "search_query": search_query,
        }

        yield json.dumps(
            metadata,
            ensure_ascii=False,
        ) + "\n"

        for token in token_stream:
            event = {
                "type": "token",
                "content": token,
            }

            yield json.dumps(
                event,
                ensure_ascii=False,
            ) + "\n"

        yield json.dumps(
            {"type": "done"},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
    )
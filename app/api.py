from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pdf_assistant.services.qa_service import QAService


app = FastAPI(
    title="AI PDF Assistant API",
    description="API для вопросов по PDF-документу на основе RAG",
    version="1.0.0",
)

qa_service = QAService()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "AI PDF Assistant API запущен"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Вопрос не должен быть пустым.",
        )

    result = qa_service.answer(request.question)

    return result
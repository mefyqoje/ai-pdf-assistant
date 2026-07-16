from pdf_assistant.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_NAME,
)
from pdf_assistant.llm.ollama_client import OllamaClient
from pdf_assistant.services.retriever_service import (
    RetrieverService,
)


class QAService:
    def __init__(self) -> None:
        self.retriever = RetrieverService()

        self.llm = OllamaClient(
            model_name=OLLAMA_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
        )

    def reload_retriever(self) -> None:
        self.retriever.reload()

    def build_prompt(
        self,
        question: str,
        context_chunks: list[dict],
    ) -> str:
        context_parts = []

        for chunk in context_chunks:
            document = chunk.get(
                "document",
                "Неизвестный документ",
            )
            page = chunk.get("page", "неизвестна")
            text = chunk["text"]

            context_parts.append(
                (
                    f"Документ: {document}\n"
                    f"Страница: {page}\n"
                    f"Текст:\n{text}"
                )
            )

        context = "\n\n---\n\n".join(context_parts)

        return f"""
Ты — AI-ассистент по базе PDF-документов.

Правила:
- Отвечай на русском языке.
- Используй только информацию из предоставленного контекста.
- Не придумывай факты, которых нет в контексте.
- Если информации недостаточно, прямо напиши:
  "В загруженных документах нет достаточной информации для ответа."
- Если используешь сведения из контекста, укажи имя документа и страницу.
- Сформулируй ответ понятно и кратко.

Контекст:
{context}

Вопрос пользователя:
{question}

Ответ:
""".strip()

    def answer(
        self,
        question: str,
    ) -> dict:
        chunks = self.retriever.retrieve(question)

        if not chunks:
            return {
                "answer": (
                    "В загруженных документах нет достаточной "
                    "информации для ответа."
                ),
                "sources": [],
            }

        prompt = self.build_prompt(
            question,
            chunks,
        )

        answer = self.llm.generate(prompt)

        sources = []

        for chunk in chunks:
            sources.append(
                {
                    "document": chunk.get(
                        "document",
                        "Неизвестный документ",
                    ),
                    "page": chunk.get("page"),
                    "score": chunk.get("score", 0.0),
                    "text": chunk["text"][:500],
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }
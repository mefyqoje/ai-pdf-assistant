from pdf_assistant.config import OLLAMA_BASE_URL, OLLAMA_MODEL_NAME
from pdf_assistant.llm.ollama_client import OllamaClient
from pdf_assistant.services.retriever_service import RetrieverService


class QAService:
    def __init__(self) -> None:
        self.retriever = RetrieverService()
        self.llm = OllamaClient(
            model_name=OLLAMA_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
        )

    def build_prompt(self, question: str, context_chunks: list[dict]) -> str:
        context = "\n\n".join(
            [
                f"[Страница {chunk['page']}]\n{chunk['text']}"
                for chunk in context_chunks
            ]
        )

        return f"""
Ты — AI-ассистент, который отвечает только по предоставленному контексту.

Правила:
- Отвечай на русском языке.
- Используй только информацию из контекста.
- Если ответа нет в контексте, напиши: "В документе нет информации для ответа на этот вопрос."
- В конце укажи страницы, на которые ты опирался.

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""

    def answer(self, question: str) -> dict:
        chunks = self.retriever.retrieve(question)

        prompt = self.build_prompt(question, chunks)

        answer = self.llm.generate(prompt)

        sources = [
            {
                "page": chunk["page"],
                "score": chunk["score"],
                "text": chunk["text"][:300],
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }
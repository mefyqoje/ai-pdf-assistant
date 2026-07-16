from collections.abc import Iterator

from pdf_assistant.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_NAME,
)
from pdf_assistant.llm.ollama_client import OllamaClient
from pdf_assistant.services.retriever_service import RetrieverService


class QAService:
    def __init__(self) -> None:
        self.retriever = RetrieverService()

        self.llm = OllamaClient(
            model_name=OLLAMA_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
        )

    def reload_retriever(self) -> None:
        self.retriever.reload()

    @staticmethod
    def _format_history(
        history: list[dict],
        max_messages: int = 6,
    ) -> str:
        if not history:
            return "История диалога отсутствует."

        recent_messages = history[-max_messages:]
        formatted_messages = []

        role_names = {
            "user": "Пользователь",
            "assistant": "Ассистент",
        }

        for message in recent_messages:
            role = role_names.get(
                message.get("role", ""),
                "Участник",
            )

            content = str(
                message.get(
                    "content",
                    "",
                )
            ).strip()

            if content:
                formatted_messages.append(
                    f"{role}: {content}"
                )

        if not formatted_messages:
            return "История диалога отсутствует."

        return "\n".join(formatted_messages)

    def build_search_query(
        self,
        question: str,
        history: list[dict],
    ) -> str:
        if not history:
            return question

        history_text = self._format_history(
            history,
            max_messages=4,
        )

        prompt = f"""
Преобразуй последний вопрос пользователя в самостоятельный поисковый запрос.

Используй историю только для разрешения ссылок и уточнений:
- "а какие еще";
- "что насчет этого";
- "а во втором документе";
- местоимения;
- сокращенные формулировки;
- ссылки на предыдущий вопрос.

Не отвечай на вопрос.
Верни только один самостоятельный поисковый запрос без пояснений.

История:
{history_text}

Последний вопрос:
{question}

Самостоятельный запрос:
""".strip()

        rewritten_query = self.llm.generate(prompt).strip()

        return rewritten_query or question

    def build_prompt(
        self,
        question: str,
        context_chunks: list[dict],
        history: list[dict],
    ) -> str:
        context_parts = []

        for chunk in context_chunks:
            document = chunk.get(
                "document",
                "Неизвестный документ",
            )
            page = chunk.get(
                "page",
                "неизвестна",
            )
            text = chunk.get(
                "text",
                "",
            )

            context_parts.append(
                (
                    f"Документ: {document}\n"
                    f"Страница: {page}\n"
                    f"Текст:\n{text}"
                )
            )

        context = "\n\n---\n\n".join(context_parts)
        history_text = self._format_history(history)

        return f"""
Ты — AI-ассистент по базе PDF-документов.

Правила:
- Отвечай на русском языке.
- Используй факты только из предоставленного контекста.
- История диалога нужна только для понимания уточняющих вопросов.
- История диалога не является источником фактов.
- Не придумывай сведения, которых нет в контексте.
- Если информации недостаточно, напиши:
  "В загруженных документах нет достаточной информации для ответа."
- При использовании сведений указывай имя документа и страницу.
- Не утверждай, что изучил весь документ, если в контексте есть только отдельные фрагменты.
- Ответ должен быть понятным и структурированным.

История диалога:
{history_text}

Контекст из документов:
{context}

Текущий вопрос пользователя:
{question}

Ответ:
""".strip()

    @staticmethod
    def _build_sources(
        chunks: list[dict],
    ) -> list[dict]:
        sources = []

        for chunk in chunks:
            sources.append(
                {
                    "document": chunk.get(
                        "document",
                        "Неизвестный документ",
                    ),
                    "page": chunk.get(
                        "page",
                        "неизвестна",
                    ),
                    "score": float(
                        chunk.get(
                            "reranker_score",
                            chunk.get(
                                "score",
                                0.0,
                            ),
                        )
                    ),
                    "retrieval_score": float(
                        chunk.get(
                            "retrieval_score",
                            0.0,
                        )
                    ),
                    "bm25_score": float(
                        chunk.get(
                            "bm25_score",
                            0.0,
                        )
                    ),
                    "text": chunk.get(
                        "text",
                        "",
                    )[:500],
                }
            )

        return sources

    def prepare_answer(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> dict:
        history = history or []

        search_query = self.build_search_query(
            question=question,
            history=history,
        )

        chunks = self.retriever.retrieve(
            search_query
        )

        if not chunks:
            return {
                "prompt": None,
                "sources": [],
                "search_query": search_query,
                "empty_answer": (
                    "В загруженных документах нет достаточной "
                    "информации для ответа."
                ),
            }

        prompt = self.build_prompt(
            question=question,
            context_chunks=chunks,
            history=history,
        )

        return {
            "prompt": prompt,
            "sources": self._build_sources(chunks),
            "search_query": search_query,
            "empty_answer": None,
        }

    def answer(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> dict:
        prepared = self.prepare_answer(
            question=question,
            history=history,
        )

        if prepared["empty_answer"]:
            return {
                "answer": prepared["empty_answer"],
                "sources": prepared["sources"],
                "search_query": prepared["search_query"],
            }

        answer = self.llm.generate(
            prepared["prompt"]
        ).strip()

        return {
            "answer": answer,
            "sources": prepared["sources"],
            "search_query": prepared["search_query"],
        }

    def answer_stream(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> tuple[Iterator[str], list[dict], str]:
        prepared = self.prepare_answer(
            question=question,
            history=history,
        )

        if prepared["empty_answer"]:

            def empty_generator() -> Iterator[str]:
                yield prepared["empty_answer"]

            return (
                empty_generator(),
                prepared["sources"],
                prepared["search_query"],
            )

        return (
            self.llm.generate_stream(
                prepared["prompt"]
            ),
            prepared["sources"],
            prepared["search_query"],
        )
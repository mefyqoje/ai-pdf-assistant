from pdf_assistant.services.retriever_service import (
    RetrieverService,
)


def main() -> None:
    retriever = RetrieverService()

    question = input(
        "Введите поисковый запрос: "
    )

    results = retriever.retrieve(question)

    print("\nРезультаты после reranking:")

    for number, result in enumerate(
        results,
        start=1,
    ):
        print("=" * 80)
        print(f"Результат №{number}")
        print(
            f"Документ: "
            f"{result.get('document')}"
        )
        print(
            f"Страница: "
            f"{result.get('page')}"
        )
        print(
            f"FAISS score: "
            f"{result.get('retrieval_score', 0.0):.4f}"
        )
        print(
            f"Reranker score: "
            f"{result.get('reranker_score', 0.0):.4f}"
        )
        print("-" * 80)
        print(result["text"][:700])


if __name__ == "__main__":
    main()
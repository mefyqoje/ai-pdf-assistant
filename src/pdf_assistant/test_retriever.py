from pdf_assistant.services.retriever_service import RetrieverService


def main():
    retriever = RetrieverService()

    results = retriever.retrieve(
        "Что такое машинное обучение?"
    )

    print("=" * 80)

    for i, result in enumerate(results, start=1):
        print(f"\nРезультат {i}")
        print(f"Страница: {result['page']}")
        print(f"Score: {result['score']:.3f}")
        print("-" * 80)
        print(result["text"][:600])


if __name__ == "__main__":
    main()
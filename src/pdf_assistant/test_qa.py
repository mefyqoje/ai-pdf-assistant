from pdf_assistant.services.qa_service import QAService


def main():
    service = QAService()

    question = input("Введите вопрос по PDF: ")

    result = service.answer(question)

    print("\nОтвет:")
    print(result["answer"])

    print("\nИсточники:")
    for source in result["sources"]:
        print(f"- Страница {source['page']}, score={source['score']:.3f}")


if __name__ == "__main__":
    main()
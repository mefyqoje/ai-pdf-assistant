from pdf_assistant.services.indexing_service import IndexingService


def main():
    service = IndexingService()

    chunks_count = service.index_pdf("data/documents/sample.pdf")

    print(f"Документ успешно проиндексирован.")
    print(f"Количество чанков: {chunks_count}")


if __name__ == "__main__":
    main()
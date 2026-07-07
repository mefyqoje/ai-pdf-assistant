from pdf_assistant.loaders.pdf_loader import load_pdf_text
from pdf_assistant.splitters.text_splitter import split_pages_into_chunks


def main():
    pdf_path = "data/documents/sample.pdf"

    pages = load_pdf_text(pdf_path)
    chunks = split_pages_into_chunks(pages)

    print(f"Количество страниц с текстом: {len(pages)}")
    print(f"Количество чанков: {len(chunks)}")

    print("=" * 80)
    print(chunks[0]["text"][:1000])
    print(f"Страница: {chunks[0]['page']}")
    print(f"Chunk ID: {chunks[0]['chunk_id']}")


if __name__ == "__main__":
    main()
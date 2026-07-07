from pdf_assistant.loaders.pdf_loader import load_pdf_text


def main():
    pdf_path = "data/documents/sample.pdf"

    pages = load_pdf_text(pdf_path)

    print(f"Количество страниц с текстом: {len(pages)}")

    print("=" * 80)
    print(pages[0]["text"][:1000])


if __name__ == "__main__":
    main()
from pathlib import Path

import fitz


def load_pdf_text(file_path: str | Path) -> list[dict]:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF-файл не найден: {file_path}")

    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text.strip():
            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

    document.close()

    return pages
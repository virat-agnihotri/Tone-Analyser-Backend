from pathlib import Path
import pymupdf as fitz


def extract_pdf_text(pdf_path: str) -> str:
    try:
        document = fitz.open(pdf_path)
        pages = []
        for page in document:
            text = page.get_text()
            if text.strip():
                pages.append(text.strip())
        document.close()
        return "\n".join(pages)
    except Exception as e:
        print(f"PDF extraction error ({pdf_path}): {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break
        start = end - overlap

    return chunks


def ingest_pdf(pdf_path: str) -> list[str]:
    text = extract_pdf_text(pdf_path)
    return chunk_text(text)

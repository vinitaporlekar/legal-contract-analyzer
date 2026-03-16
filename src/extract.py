import fitz  # PyMuPDF
import re
from docx import Document


def clean_text(text):
    """Clean extracted text by removing noise."""
    # Remove "Page X of Y" headers
    text = re.sub(r"Page \d+ of \d+", "", text)

    # Remove excessive blank lines (more than 2 in a row)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove excessive spaces
    text = re.sub(r" {2,}", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_text_from_pdf(file_path):
    """Open a PDF and extract text from every page."""
    doc = fitz.open(file_path)

    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append({
            "page_number": page_num + 1,
            "text": clean_text(text)
        })

    doc.close()
    return pages


def extract_text_from_docx(file_path):
    """Open a DOCX and extract text paragraph by paragraph."""
    doc = Document(file_path)

    paragraphs = []
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            paragraphs.append({
                "paragraph_number": i + 1,
                "text": clean_text(para.text),
                "style": para.style.name
            })

    return paragraphs


def extract_text(file_path):
    """Auto-detect file type and extract text."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


if __name__ == "__main__":
    file_path = "data/test_contract.pdf"

    print(f"Extracting text from: {file_path}\n")

    results = extract_text(file_path)

    for item in results[:10]:
        print(item)
        print()

    print(f"Total items extracted: {len(results)}")
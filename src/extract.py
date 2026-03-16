import fitz  # PyMuPDF


def extract_text_from_pdf(file_path):
    """Open a PDF and extract text from every page."""
    doc = fitz.open(file_path)

    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append({
            "page_number": page_num + 1,
            "text": text.strip()
        })

    doc.close()
    return pages


if __name__ == "__main__":
    file_path = "data/test_contract.pdf"

    print(f"Extracting text from: {file_path}\n")

    pages = extract_text_from_pdf(file_path)

    for page in pages:
        print(f"--- PAGE {page['page_number']} ---")
        print(page["text"][:500])
        print()

    print(f"Total pages: {len(pages)}")
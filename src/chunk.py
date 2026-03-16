import re


def naive_chunk(text, chunk_size=500):
    """Split text every N characters. Simple but bad for legal docs."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def clause_aware_chunk(pages):
    """Split contract text respecting legal structure."""
    # First, combine all pages into one string
    full_text = "\n\n".join([page["text"] for page in pages])

    # Split on common legal patterns:
    # - Numbered sections like "1." or "2.1" or "(a)"
    # - All-caps headings like "CONFIDENTIAL INFORMATION"
    pattern = r'\n(?=\d+\.[\s]|[a-z]\)|[A-Z]{2,}[A-Z\s]{5,})'

    raw_chunks = re.split(pattern, full_text)

    # Build chunks with metadata
    chunks = []
    for i, text in enumerate(raw_chunks):
        text = text.strip()
        if len(text) < 20:  # skip tiny fragments
            continue

        # Try to detect the section heading
        lines = text.split("\n")
        heading = lines[0][:80] if lines else "Unknown"

        chunks.append({
            "chunk_id": i,
            "heading": heading,
            "text": text,
            "char_count": len(text)
        })

    return chunks


def add_overlap(chunks, overlap_chars=100):
    """Add overlap between chunks so context isn't lost at boundaries."""
    overlapped = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]

        # Add end of previous chunk to the start
        if i > 0:
            prev_text = chunks[i - 1]["text"]
            overlap = prev_text[-overlap_chars:]
            text = f"...{overlap}\n\n{text}"

        overlapped.append({
            "chunk_id": chunk["chunk_id"],
            "heading": chunk["heading"],
            "text": text,
            "char_count": len(text)
        })

    return overlapped


if __name__ == "__main__":
    # Import our extractor from last step
    from extract import extract_text

    file_path = "data/test_contract.pdf"
    pages = extract_text(file_path)

    # First show naive chunking (the bad way)
    full_text = "\n\n".join([p["text"] for p in pages])
    naive = naive_chunk(full_text)
    print("=== NAIVE CHUNKING ===")
    print(f"Total chunks: {len(naive)}")
    print(f"First chunk preview: {naive[0][:200]}...")
    print()

    # Now show clause-aware chunking (the good way)
    smart = clause_aware_chunk(pages)
    smart = add_overlap(smart)
    print("=== CLAUSE-AWARE CHUNKING ===")
    print(f"Total chunks: {len(smart)}")
    print()

    for chunk in smart:
        print(f"--- Chunk {chunk['chunk_id']} ({chunk['char_count']} chars) ---")
        print(f"Heading: {chunk['heading']}")
        print(f"Preview: {chunk['text'][:200]}...")
        print()
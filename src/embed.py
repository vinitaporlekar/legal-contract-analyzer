import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def get_embedding(text):
    """Turn a piece of text into a vector of numbers."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def embed_chunks(chunks):
    """Generate embeddings for a list of chunks."""
    embedded = []
    for i, chunk in enumerate(chunks):
        print(f"Embedding chunk {i + 1}/{len(chunks)}...")
        embedding = get_embedding(chunk["text"])
        chunk["embedding"] = embedding
        embedded.append(chunk)

    return embedded


def cosine_similarity(vec_a, vec_b):
    """Calculate how similar two vectors are (0 = unrelated, 1 = identical)."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = sum(a * a for a in vec_a) ** 0.5
    magnitude_b = sum(b * b for b in vec_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


if __name__ == "__main__":
    from src.extract import extract_text
    from src.chunk import clause_aware_chunk, add_overlap

    # Step 1: Extract and chunk
    pages = extract_text("data/test_contract.pdf")
    chunks = clause_aware_chunk(pages)
    chunks = add_overlap(chunks)
    print(f"Total chunks: {len(chunks)}\n")

    # Step 2: Embed first 10 chunks as a test
    test_chunks = chunks[:10]
    embedded = embed_chunks(test_chunks)

    # Step 3: See what an embedding looks like
    first = embedded[0]["embedding"]
    print(f"Embedding length: {len(first)}")
    print(f"First 10 numbers: {first[:10]}\n")

    # Step 4: Test similarity
    question = "What is confidential information?"
    q_embedding = get_embedding(question)

    print(f"Question: '{question}'\n")
    for chunk in embedded:
        score = cosine_similarity(q_embedding, chunk["embedding"])
        print(f"Chunk {chunk['chunk_id']} ({chunk['heading'][:50]})")
        print(f"  Similarity: {score:.4f}\n")
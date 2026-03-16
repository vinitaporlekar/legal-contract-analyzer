import os
import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up ChromaDB - saves to disk so you don't re-embed every time
chroma_client = chromadb.PersistentClient(path="chroma_db")


def get_embedding(text):
    """Turn text into a vector."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def get_or_create_collection(name="contracts"):
    """Get existing collection or create a new one."""
    return chroma_client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def store_chunks(chunks, contract_name="default"):
    """Embed chunks and store them in ChromaDB."""
    collection = get_or_create_collection()

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")

        chunk_id = f"{contract_name}_chunk_{i}"
        embedding = get_embedding(chunk["text"])

        ids.append(chunk_id)
        documents.append(chunk["text"])
        embeddings.append(embedding)
        metadatas.append({
            "contract": contract_name,
            "heading": chunk["heading"],
            "chunk_id": str(chunk["chunk_id"]),
            "char_count": str(chunk["char_count"])
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"\nStored {len(ids)} chunks for '{contract_name}'")
    print(f"Total chunks in database: {collection.count()}")


def search(question, n_results=5):
    """Search for chunks most relevant to a question."""
    collection = get_or_create_collection()

    q_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=n_results
    )

    # Format results into a clean list
    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "heading": results["metadatas"][0][i]["heading"],
            "contract": results["metadatas"][0][i]["contract"],
            "distance": results["distances"][0][i]
        })

    return formatted
def rerank(question, results, top_n=3):
    """Re-score results using a cross-encoder for better accuracy."""
    from sentence_transformers import CrossEncoder

    model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Create pairs of [question, chunk_text] for the model to score
    pairs = [[question, r["text"]] for r in results]
    scores = model.predict(pairs)

    # Attach scores and sort by highest first
    for i, result in enumerate(results):
        result["rerank_score"] = float(scores[i])

    reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_n]


if __name__ == "__main__":
    from src.extract import extract_text
    from src.chunk import clause_aware_chunk, add_overlap

    # Step 1: Extract, chunk, and store
    print("=== INGESTING CONTRACT ===\n")
    pages = extract_text("data/test_contract.pdf")
    chunks = clause_aware_chunk(pages)
    chunks = add_overlap(chunks)
    store_chunks(chunks, contract_name="sample_nda")

    # Step 2: Search and rerank
    print("\n=== SEARCHING WITH RERANKING ===\n")
    questions = [
        "What is confidential information?",
        "Can I terminate this agreement?",
        "What happens if there is a breach?",
    ]

    for question in questions:
        print(f"Q: {question}")
        print("-" * 50)

        # Get 10 results from ChromaDB, then rerank to top 3
        raw_results = search(question, n_results=10)
        reranked = rerank(question, raw_results, top_n=3)

        for i, r in enumerate(reranked):
            print(f"  {i + 1}. [{r['heading'][:60]}]")
            print(f"     Rerank score: {r['rerank_score']:.4f}")
            print(f"     Preview: {r['text'][:150]}...")
            print()
        print()
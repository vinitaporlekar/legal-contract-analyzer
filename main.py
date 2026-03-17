import sys
import time
from src.extract import extract_text
from src.chunk import clause_aware_chunk, add_overlap
from src.retrieve import store_chunks, search, rerank
from src.generate import generate_answer
from src.risk import scan_contract_risks


def ingest(file_path, contract_name):
    """Full ingestion pipeline: extract → chunk → embed → store → scan risks."""
    print(f"\n📄 Extracting text from {file_path}...")
    pages = extract_text(file_path)
    print(f"   Found {len(pages)} pages")

    print("✂️  Chunking into clauses...")
    chunks = clause_aware_chunk(pages)
    chunks = add_overlap(chunks)
    print(f"   Created {len(chunks)} chunks")

    print("💾 Storing embeddings in ChromaDB...")
    store_chunks(chunks, contract_name=contract_name)

    print("🔍 Scanning for risky clauses...")
    risks = scan_contract_risks(chunks)
    print(f"   Found {len(risks)} risky clauses")

    return risks


def query(question):
    """Full query pipeline: search → rerank → generate answer."""
    raw = search(question, n_results=10)
    top = rerank(question, raw, top_n=3)
    result = generate_answer(question, top)
    return result


def print_risks(risks):
    """Display risk report."""
    if not risks:
        print("\n✅ No risky clauses detected!")
        return

    print(f"\n⚠️  RISK REPORT: {len(risks)} issues found\n")
    for r in risks:
        icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r["severity"], "⚪")
        print(f"  {icon} {r['severity']} — {r['category']}")
        print(f"     {r['explanation']}")
        print()


def print_answer(result):
    """Display Q&A result."""
    print(f"\n💬 Answer:\n{result['answer']}\n")
    print("📎 Sources:")
    for i, s in enumerate(result["sources"]):
        print(f"   {i+1}. {s['heading']}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("  Legal Contract Analyzer")
    print("=" * 50)

    # Ingest
    file_path = "data/test_contract.pdf"
    contract_name = "sample_nda"

    print("\n[1/2] INGESTING CONTRACT")
    risks = ingest(file_path, contract_name)
    print_risks(risks)

    # Interactive Q&A loop
    print("[2/2] ASK QUESTIONS (type 'quit' to exit)\n")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break
        if not question:
            continue

        result = query(question)
        print_answer(result)
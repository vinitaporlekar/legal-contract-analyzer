import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """You are a legal contract analyst. Your job is to answer questions about contracts 
using ONLY the provided contract clauses below.

Rules:
1. Only use information from the provided clauses to answer
2. Cite each claim with the clause reference like [Clause 1] or [Clause 3]
3. If the answer is not in the provided clauses, say "I could not find this information in the provided contract clauses."
4. Be precise and specific - quote key phrases from the clauses when relevant
5. Keep answers clear and concise"""


def format_context(results):
    """Format retrieved chunks into a numbered context string for the LLM."""
    context = ""
    for i, r in enumerate(results):
        context += f"\n--- Clause {i + 1} (from section: {r['heading'][:60]}) ---\n"
        context += r["text"]
        context += "\n"
    return context


def generate_answer(question, results):
    """Send question + retrieved clauses to Gemini and get a cited answer."""
    context = format_context(results)

    prompt = f"""{SYSTEM_PROMPT}

Here are the relevant contract clauses:
{context}

Question: {question}

Answer the question using only the clauses above. Cite your sources."""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return {
        "question": question,
        "answer": response.text,
        "sources": [
            {
                "heading": r["heading"][:60],
                "text": r["text"][:300],
                "score": r.get("rerank_score", r.get("distance", 0))
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    from src.retrieve import search, rerank

    questions = [
        "What is considered confidential information in this agreement?",
        "What happens if there is a breach of this agreement?",
        "Can the company assign its rights under this agreement?",
        "How long do the confidentiality obligations last?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print('='*60)

        # Retrieve and rerank
        raw = search(question, n_results=10)
        top = rerank(question, raw, top_n=3)

        # Generate answer
        result = generate_answer(question, top)

        print(f"\nA: {result['answer']}")
        print(f"\n--- Sources ---")
        for i, s in enumerate(result["sources"]):
            print(f"  {i+1}. [{s['heading']}]")
            print(f"     Score: {s['score']:.4f}")
        print()
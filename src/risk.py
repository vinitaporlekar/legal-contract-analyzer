import os
import time
from dotenv import load_dotenv
from google import genai


load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

RISK_CATEGORIES = [
    "Non-compete clause",
    "Unlimited liability",
    "Automatic renewal",
    "Broad IP assignment",
    "One-sided termination",
    "Broad indemnification",
    "Non-solicitation",
    "Unrestricted data use",
    "Survival beyond termination",
]

RISK_PROMPT = """You are a legal risk analyst. Analyze the following contract clause and determine if it contains any of these risk categories:

{categories}

Clause:
{clause}

Respond in this exact format:
RISK: Yes or No
CATEGORY: The matching category (or "None")
SEVERITY: Low, Medium, or High
EXPLANATION: One sentence explaining why this is risky for the signing party.

If there is no risk, respond:
RISK: No
CATEGORY: None
SEVERITY: None
EXPLANATION: None"""


def analyze_clause_risk(clause_text):
    """Send a single clause to Gemini for risk analysis."""
    categories = "\n".join(f"- {c}" for c in RISK_CATEGORIES)
    prompt = RISK_PROMPT.format(categories=categories, clause=clause_text)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    # Parse the response
    result = {
        "risk": False,
        "category": "None",
        "severity": "None",
        "explanation": "None"
    }

    for line in response.text.strip().split("\n"):
        line = line.strip()
        if line.startswith("RISK:"):
            result["risk"] = "yes" in line.lower()
        elif line.startswith("CATEGORY:"):
            result["category"] = line.split(":", 1)[1].strip()
        elif line.startswith("SEVERITY:"):
            result["severity"] = line.split(":", 1)[1].strip()
        elif line.startswith("EXPLANATION:"):
            result["explanation"] = line.split(":", 1)[1].strip()

    return result


def scan_contract_risks(chunks):
    """Scan all chunks in a contract for risks."""
    flagged = []

    for i, chunk in enumerate(chunks):
        print(f"Scanning chunk {i + 1}/{len(chunks)}...")

        # Retry up to 3 times if rate limited
        for attempt in range(3):
            try:
                risk = analyze_clause_risk(chunk["text"])
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait = 30 * (attempt + 1)
                    print(f"  Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  Error on chunk {i+1}: {e}")
                    risk = {"risk": False}
                    break

        time.sleep(6)  # wait 6 seconds between calls

        if risk["risk"]:
            flagged.append({
                "chunk_id": chunk["chunk_id"],
                "heading": chunk["heading"],
                "text": chunk["text"][:400],
                "category": risk["category"],
                "severity": risk["severity"],
                "explanation": risk["explanation"],
            })

    return flagged

if __name__ == "__main__":
    from src.extract import extract_text
    from src.chunk import clause_aware_chunk, add_overlap

    # Extract and chunk
    pages = extract_text("data/test_contract.pdf")
    chunks = clause_aware_chunk(pages)
    chunks = add_overlap(chunks)

    print(f"Scanning {len(chunks)} clauses for risks...\n")
    risks = scan_contract_risks(chunks)

    print(f"\n{'='*60}")
    print(f"RISK REPORT: {len(risks)} risky clauses found")
    print(f"{'='*60}\n")

    for r in risks:
        severity_icon = {"High": "!!!", "Medium": "!!", "Low": "!"}.get(r["severity"], "?")
        print(f"[{severity_icon}] {r['severity']} - {r['category']}")
        print(f"    Section: {r['heading'][:60]}")
        print(f"    Why: {r['explanation']}")
        print(f"    Text: {r['text'][:150]}...")
        print()
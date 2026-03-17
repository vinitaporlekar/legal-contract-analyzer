import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.extract import extract_text
from src.chunk import clause_aware_chunk, add_overlap
from src.retrieve import store_chunks, search, rerank
from src.generate import generate_answer
from src.risk import scan_contract_risks

app = FastAPI(title="Legal Contract Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

contracts = {}


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/contracts/upload")
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files supported")

    os.makedirs("data", exist_ok=True)
    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    contract_name = file.filename.rsplit(".", 1)[0].replace(" ", "_").lower()

    pages = extract_text(file_path)
    chunks = clause_aware_chunk(pages)
    chunks = add_overlap(chunks)
    store_chunks(chunks, contract_name=contract_name)
    risks = scan_contract_risks(chunks)

    contracts[contract_name] = {
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "risks": risks,
    }

    return {
        "contract_name": contract_name,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "risks_found": len(risks),
    }


@app.post("/contracts/{contract_name}/query")
def query_contract(contract_name: str, request: QueryRequest):
    if contract_name not in contracts:
        raise HTTPException(status_code=404, detail="Contract not found")

    raw = search(request.question, n_results=10)
    top = rerank(request.question, raw, top_n=3)
    result = generate_answer(request.question, top)

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
    }


@app.get("/contracts/{contract_name}/risks")
def get_risks(contract_name: str):
    if contract_name not in contracts:
        raise HTTPException(status_code=404, detail="Contract not found")

    return {
        "contract_name": contract_name,
        "risks": contracts[contract_name]["risks"],
    }


@app.get("/contracts")
def list_contracts():
    return {"contracts": list(contracts.keys())}
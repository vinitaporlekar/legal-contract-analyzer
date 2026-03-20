# Legal Contract Analyzer

A RAG-powered legal contract analyzer that extracts, chunks, and embeds contract text to enable cited Q&A and automatic risk detection.

---

## Features

- 📄 Upload PDF or DOCX contracts
- 🔍 Clause-aware chunking with context overlap
- 🧠 Semantic search using Gemini embeddings + ChromaDB
- ⚖️ Cross-encoder reranking for more accurate retrieval
- 💬 Cited Q&A — every answer references the exact clause
- ⚠️ Automatic risk detection across 9 risk categories
- 🖥️ React frontend with chat and risk dashboard tabs

---

## Project Structure

```
legal-contract-analyzer/
├── app.py                  # FastAPI backend
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── extract.py          # PDF & DOCX text extraction
│   ├── chunk.py            # Clause-aware chunking
│   ├── embed.py            # Gemini embedding utilities
│   ├── retrieve.py         # ChromaDB storage & search + reranking
│   ├── generate.py         # Gemini answer generation
│   └── risk.py             # Risk clause detection
└── frontend/
    ├── src/
    │   ├── App.js                        # Main app with state & API calls
    │   └── components/
    │       ├── UploadScreen.jsx          # File upload UI
    │       └── RiskDashboard.jsx         # Risk report UI
    └── package.json
```

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- A [Google AI Studio](https://aistudio.google.com/) API key (free)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/legal-contract-analyzer.git
cd legal-contract-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key_here
```

> Get your free API key at https://aistudio.google.com/

### 5. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the App

### Start the backend

From the project root:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### Start the frontend

In a separate terminal, from the `frontend/` folder:

```bash
npm start
```

The app will open at `http://localhost:3000`

---

## CLI Usage

To run without the frontend, use the command-line interface:

```bash
python main.py
```

This will:
1. Ingest `data/test_contract.pdf`
2. Print a risk report
3. Start an interactive Q&A loop

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/contracts/upload` | Upload and analyze a contract |
| `POST` | `/contracts/{name}/query` | Ask a question about a contract |
| `GET` | `/contracts/{name}/risks` | Get the risk report for a contract |
| `GET` | `/contracts` | List all uploaded contracts |

---

## Risk Categories Detected

- Non-compete clause
- Unlimited liability
- Automatic renewal
- Broad IP assignment
- One-sided termination
- Broad indemnification
- Non-solicitation
- Unrestricted data use
- Survival beyond termination

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM & Embeddings | Google Gemini 2.0 Flash + Gemini Embedding 001 |
| Vector Database | ChromaDB (persistent, local) |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Backend | FastAPI + Uvicorn |
| Frontend | React |
| PDF Extraction | PyMuPDF |
| DOCX Extraction | python-docx |
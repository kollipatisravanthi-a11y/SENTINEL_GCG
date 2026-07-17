# SENTINEL

SENTINEL is a distributed complaint-management platform. It combines a FastAPI backend, a React dashboard, and independent node servers to record complaints, track their status, and detect tampering through hash and chain verification.

## Features

- Submit and track complaints
- Store complaint records in a tamper-evident chain
- Monitor distributed NGO, media, ombudsman, and public nodes
- Verify node consistency and identify tampered or out-of-sync records
- View a transparent public ledger
- Remove file metadata before processing uploads

## Project structure

```text
backend/             FastAPI application, chain logic, database, and node server
frontend/            React dashboard
tamper_evidence.py   Interactive utility for demonstrating node tampering
start_backend.bat    Windows backend startup script
requirements.txt     Python dependencies
```

## Requirements

- Python 3.10 or later
- Node.js and npm

## Run the backend

Install the Python dependencies from the repository root:

```bash
pip install -r requirements.txt
```

On Windows, start the backend with:

```bat
start_backend.bat
```

Or run the main API manually:

```bash
uvicorn backend.main:app --reload
```

The main API runs at `http://localhost:8000` by default.

## Run the frontend

```bash
cd frontend
npm install
npm start
```

The React development server uses the backend API at `http://localhost:8000`.

## Tamper-detection demo

With the main server and node servers running, use the included demo utility to tamper a selected complaint on one node and inspect that node's chain verification result:

```bash
python tamper_evidence.py
```

You can also run it non-interactively:

```bash
python tamper_evidence.py --node NGO --complaint 1 --yes
```

Available nodes are `NGO`, `MEDIA`, `OMBUDSMAN`, and `PUBLIC`.

## Tech stack

**Backend:** FastAPI, Uvicorn, Pydantic, HTTPX, SQLite, and Python  
**Frontend:** React, JavaScript, HTML, and CSS

## Main components

- `backend/main.py` — API endpoints and verification workflow
- `backend/chain.py` — hash-chain logic
- `backend/database.py` — database operations
- `backend/nodes/node_server.py` — distributed node server
- `backend/utils/` — hashing and metadata-removal utilities

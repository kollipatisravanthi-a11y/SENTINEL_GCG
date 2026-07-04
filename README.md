## Sentinel

**Sentinel** is a full-stack application consisting of a **FastAPI** backend and a **React.js** frontend. It is designed to manage and control distributed nodes, handle complaints, detect tampering, and maintain a transparent public ledger.

---

## 📂 Project Structure

```text
Sentinel/
│
├── backend/
│   ├── main.py                 # Backend entry point
│   ├── chain.py                # Blockchain logic
│   ├── database.py             # Database operations
│   ├── models.py               # Data models
│   ├── nodes/
│   │   └── node_server.py      # Node server logic
│   └── utils/
│       ├── hasher.py           # Hashing utilities
│       └── metadata_stripper.py# Metadata removal utilities
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── Dashboard
│   │   ├── NodeControl
│   │   ├── NodePanel
│   │   ├── PublicLedger
│   │   ├── SubmitComplaint
│   │   ├── TamperAlert
│   │   └── TrackComplaint
│   ├── package.json
│   └── package-lock.json
│
├── requirements.txt
├── start_backend.bat
└── FILESTRUCTURE.txt
```

---

## 🚀 Features

- 🔗 Blockchain-powered complaint storage
- 🌐 Distributed node management
- 📋 Complaint submission and tracking
- 🚨 Real-time tamper detection and alerts
- 📖 Transparent public ledger
- ⚡ FastAPI REST API backend
- 💻 Interactive React dashboard
- 🔒 Secure hashing and metadata stripping utilities

---

## 🛠️ Tech Stack

### Backend
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- Python

### Frontend
- React.js
- JavaScript
- HTML
- CSS

---

## 📦 Backend Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**requirements.txt**

- fastapi >= 0.95.0
- uvicorn >= 0.20.0
- httpx >= 0.23.0
- pydantic >= 1.10.0
- python-multipart >= 0.0.5
- Pillow >= 9.0.0
- pypdf >= 3.0.0
- mutagen >= 1.46.0

---

## ▶️ Running the Backend

### Windows

```bash
start_backend.bat
```

### Or start manually

```bash
uvicorn backend.main:app --reload
```

---

## ▶️ Running the Frontend

Navigate to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm start
```

---

## 📌 Modules

### Backend
- **main.py** – FastAPI application entry point
- **chain.py** – Blockchain implementation
- **database.py** – Database interactions
- **models.py** – Data models
- **nodes/node_server.py** – Node management server
- **utils/** – Hashing and metadata stripping utilities

### Frontend
- **Dashboard** – Main dashboard
- **NodeControl** – Node management interface
- **NodePanel** – Node monitoring
- **PublicLedger** – Blockchain ledger viewer
- **SubmitComplaint** – Complaint submission
- **TrackComplaint** – Complaint status tracking
- **TamperAlert** – Tamper detection dashboard

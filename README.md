# AgentCare – Multi-Agent Healthcare Administration System

AgentCare automates hospital administrative workflows using a **multi‑agent AI architecture**.  
It handles patient registration, department routing, appointment management, document processing, follow‑ups, and audits – **without ever making medical decisions**.

## Features

- 🧠 **6 distinct LangGraph agents** (Coordinator, Routing, Appointment, Document, Follow‑up, Safety)
- 🔒 JWT‑based authentication with Role‑Based Access Control (Patient, Staff, Admin)
- 📅 Appointment booking, rescheduling, cancellation with conflict detection
- 📄 Document upload (PDF, DOCX, images) with text extraction, checksum duplicate detection, and classification
- 🏥 Human approval workflows for escalations
- 📊 Persistent SQLite database + Alembic migrations
- 🔍 Audit logging of every critical action
- 📦 Full‑text search via local ChromaDB embeddings
- 🧪 Comprehensive test suite (pytest)
- 🌐 FastAPI + Jinja2 + Bootstrap frontend

## Technology Stack (100% Free)

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic v2, Uvicorn
- **Agents**: LangGraph, LangChain, Groq API (llama-3.3-70b-versatile)
- **Database**: SQLite (persistent), ChromaDB (vector)
- **Auth**: PyJWT, Passlib, bcrypt
- **Document Processing**: PyMuPDF, python-docx, Pillow, Sentence Transformers
- **Frontend**: Jinja2 templates, Bootstrap 5, Vanilla JS
- **Testing**: pytest, pytest‑asyncio, httpx

## Architecture Diagram

```mermaid
graph TD
    User[User Request] -->|FastAPI| Router
    Router --> Auth[Auth Middleware]
    Router --> Service[Service Layer]
    Service --> LangGraph[LangGraph Workflow]
    LangGraph --> C[Coordinator Agent]
    C --> R[Routing Agent]
    R --> A[Appointment Agent]
    A --> D[Document Agent]
    D --> F[Follow-up Agent]
    F --> S[Safety Agent]
    S --> DB[(SQLite + ChromaDB)]
    S --> Response
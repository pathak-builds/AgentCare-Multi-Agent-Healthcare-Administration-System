# AgentCare – Multi-Agent Healthcare Administration System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![Tests](https://img.shields.io/badge/Tests-36%20Passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**AgentCare** is an AI-powered **Multi-Agent Healthcare Administration System** developed for the **AgentCare Build Challenge 2026**. Built using **FastAPI**, **LangGraph**, and **Large Language Models (LLMs)**, it streamlines hospital administrative operations through a team of specialized AI agents that collaborate to understand patient requests, coordinate workflows, and automate routine administrative tasks.

The platform supports end-to-end healthcare administration, including **appointment scheduling**, **department routing**, **medical document processing**, **workflow tracking**, **reminder generation**, **audit logging**, and **human escalation** for complex or sensitive cases. Designed with security, transparency, and scalability in mind, AgentCare incorporates **JWT-based authentication**, **Role-Based Access Control (RBAC)**, and **persistent workflow state management**.

> **Note:** AgentCare is intended exclusively for **healthcare administration**. It does **not** provide medical diagnosis, clinical recommendations, or treatment advice.

# ✨ Features

AgentCare is an AI-powered healthcare administration platform built using **FastAPI**, **LangGraph**, and **Generative AI**. The system automates administrative workflows through a team of specialized AI agents while ensuring security, auditability, and human oversight.

---

## 🧠 Multi-Agent AI Architecture

The system uses **6 specialized LangGraph agents** that collaborate to understand patient requests, make decisions, and execute healthcare administrative workflows.

### AI Agents

| Agent | Responsibility |
|-------|----------------|
| 🎯 Coordinator Agent | Understands user intent and orchestrates the complete workflow |
| 🧭 Routing Agent | Routes requests to the correct hospital department or workflow |
| 📅 Appointment Agent | Books, reschedules, and cancels appointments |
| 📄 Document Agent | Processes uploaded documents, extracts text, and classifies files |
| 🔔 Follow-up Agent | Generates reminders and follow-up tasks |
| 🛡️ Safety Agent | Performs validation, policy enforcement, and human escalation |

---

## 🏗️ Multi-Agent Workflow

```text
                         User Request
                               │
                               ▼
                    ┌────────────────────┐
                    │ Coordinator Agent  │
                    └─────────┬──────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        Routing Agent   Safety Agent   Intent Analysis
                │             │
                └──────┬──────┘
                       ▼
        ┌────────────────────────────────┐
        │ Specialized AI Agents          │
        │                                │
        │ • Appointment Agent            │
        │ • Document Agent               │
        │ • Follow-up Agent              │
        └───────────────┬────────────────┘
                        │
                        ▼
               Database + Audit Logs
```

---

## 🏥 Healthcare Administration

### 📅 Appointment Management

- Book appointments
- Cancel appointments
- Reschedule appointments
- Doctor availability checking
- Appointment conflict detection
- Department-based routing
- Appointment history

### 👤 Patient Management

- Patient registration
- Secure authentication
- Patient profile management
- Workflow history
- Reminder management
- Medical document storage

### 🏥 Hospital Administration

- Department management
- Doctor management
- Appointment slot management
- Workflow monitoring
- User administration
- Audit reporting

---

## 📄 Intelligent Document Processing

Supports multiple document formats:

- PDF
- DOCX
- PNG
- JPG
- JPEG

Features include:

- OCR/Text extraction
- SHA-256 checksum duplicate detection
- Automatic document classification
- Secure document storage
- Upload history

### Document Processing Pipeline

```text
        Upload Document
               │
               ▼
      File Validation
               │
               ▼
    Duplicate Detection
               │
      ┌────────┴────────┐
      │                 │
Duplicate          New Document
      │                 │
 Reject Upload          ▼
                  Text Extraction
                         │
                         ▼
                 Classification
                         │
                         ▼
                 Store in Database
```

---

## 🔐 Authentication & Security

- JWT Authentication
- Password hashing using bcrypt
- Role-Based Access Control (RBAC)
- Secure API endpoints
- Token validation
- Session management
- Protected dashboards

### Supported Roles

- 👤 Patient
- 👨‍⚕️ Hospital Staff
- 👑 Administrator

---

## ⚙️ LangGraph Workflow Engine

Stateful AI workflows built using LangGraph.

```text
User Request
      │
      ▼
Coordinator Agent
      │
      ▼
Routing Agent
      │
      ├──────────────► Appointment Workflow
      │
      ├──────────────► Document Workflow
      │
      └──────────────► Follow-up Workflow
                    │
                    ▼
             Safety Validation
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
   Workflow Complete     Human Escalation
```

---

## 📊 Workflow Persistence

Every workflow execution stores:

- Workflow ID
- User Intent
- Current State
- Assigned Department
- Agent Decisions
- Escalation Status
- Execution Timeline
- Final Outcome

---

## 🗄️ Database

Built using **SQLite + SQLAlchemy ORM**.

### Database Models

- Users
- Patient Profiles
- Departments
- Doctors
- Appointment Slots
- Appointments
- Patient Documents
- Workflow Runs
- Reminders
- Escalations
- Audit Events

---

## 🔍 Audit Logging

Every important system event is logged.

Examples include:

- User Login
- Appointment Created
- Appointment Cancelled
- Appointment Rescheduled
- Document Uploaded
- Duplicate Document Detection
- Workflow Started
- Workflow Completed
- Human Escalation
- Administrative Actions

---

## 🔔 Reminder System

Automatically generates reminders for:

- Upcoming appointments
- Follow-up actions
- Workflow tasks
- Escalations

---

## 👨‍⚕️ Human-in-the-Loop

Critical workflows requiring manual review are automatically escalated.

Examples:

- Low-confidence AI decisions
- Ambiguous requests
- Missing information
- Policy violations
- Administrative exceptions

```text
         AI Decision
             │
             ▼
     Confidence Check
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
 High Confidence   Low Confidence
      │             │
      ▼             ▼
 Complete      Human Review
                    │
                    ▼
             Hospital Staff
```

---

## 🌐 REST API

Complete RESTful API built using FastAPI.

Available endpoints include:

- Authentication
- Users
- Departments
- Doctors
- Appointment Slots
- Appointments
- Documents
- Workflow
- Admin

Interactive API documentation available through Swagger UI.

---

## 💻 Responsive Web Interface

Built using:

- Bootstrap 5
- Jinja2 Templates
- Responsive Design
- Mobile-Friendly Layout
- Patient Dashboard
- Administrator Dashboard

---

## 🧪 Automated Testing

Comprehensive test suite covering:

- Authentication
- Authorization
- Appointment APIs
- Document APIs
- Workflow Engine
- AI Agent Routing
- Safety Validation
- Database Operations

**Current Status**

- ✅ 36+ Passing Tests
- ✅ Pytest Framework
- ✅ API Integration Tests
- ✅ Database Tests

---

## 🛠️ Technology Stack

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- SQLite

### Artificial Intelligence

- LangGraph
- LangChain
- Groq LLM
- ChromaDB (Optional)

### Authentication

- JWT
- Passlib
- bcrypt

### Frontend

- Bootstrap 5
- Jinja2

### Testing

- Pytest
- HTTPX

---

# 🏛️ Overall System Architecture

```text
                         ┌─────────────────────────┐
                         │      Web Browser        │
                         └─────────────┬───────────┘
                                       │
                                       ▼
                      ┌────────────────────────────────┐
                      │        FastAPI Backend         │
                      └───────────────┬────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             Authentication      REST APIs      LangGraph Engine
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                      ┌────────────────────────────────┐
                      │      Multi-Agent AI System     │
                      │                                │
                      │ • Coordinator Agent            │
                      │ • Routing Agent                │
                      │ • Appointment Agent            │
                      │ • Document Agent               │
                      │ • Follow-up Agent              │
                      │ • Safety Agent                 │
                      └───────────────┬────────────────┘
                                      │
               ┌──────────────────────┼──────────────────────┐
               ▼                      ▼                      ▼
         SQLite Database        ChromaDB (Optional)     Audit Logs
         SQLAlchemy ORM          Vector Store         Workflow History
```

## Architecture

``` mermaid
graph TD
    User[Patient Request] -->|FastAPI| Router
    Router --> Auth[Auth Middleware]
    Router --> Workflow[Workflow Service]
    Workflow --> Graph[LangGraph Workflow]
    Graph --> C[Coordinator Agent]
    C --> R[Routing Agent]
    R --> A[Appointment Agent]
    A --> D[Document Agent]
    D --> F[Follow-up Agent]
    F --> S[Safety Agent]
    S --> DB[(SQLite + Audit)]
    S --> Response[Final Response]
```

## Folder Structure

``` text
agentcare/
├── app/
│   ├── agents/            # 6 LangGraph agents
│   ├── api/               # REST API routers (protected)
│   ├── auth/              # JWT handling & RBAC dependencies
│   ├── database/          # Engine, session, Base
│   ├── models/            # SQLAlchemy models (10 tables)
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic
│   ├── tools/             # Agent tools (DB, file ops)
│   ├── workflow/          # LangGraph state & graph builder
│   ├── prompts/           # System prompts for each agent
│   ├── schemas/           # Pydantic request/response models
│   ├── web/               # Web routes (Jinja2 + Bootstrap)
│   ├── templates/         # HTML templates
│   ├── static/            # Static assets (CSS, JS)
│   ├── uploads/           # Document storage
│   ├── utils/             # Logging, audit helpers
│   ├── seed/              # Database seed script
│   └── config.py          # Settings (env vars)
├── tests/                 # pytest tests
├── main.py                # Application entrypoint
├── requirements.txt
├── .env.example
├── .gitignore
├── alembic.ini
└── README.md
```

## Installation

``` bash
git clone <repository-url>
cd agentcare

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

alembic upgrade head

python -m app.seed.seed_all

uvicorn main:app --reload
```

Application:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

## Demo Accounts

**Admin**

-   admin@agentcare.com
-   admin123

**Patient**

-   patient@agentcare.com
-   patient123

## Supported Workflows

-   Book appointment
-   Cancel appointment
-   Reschedule appointment
-   Upload document
-   Route patient requests
-   Reminder creation
-   Administrative escalation
-   Workflow history

## Testing

``` bash
pytest tests -v
```

Current Status:

-   **36 / 36 tests passing**

## Hackathon Requirements

-   ✅ Multi-Agent Architecture
-   ✅ LangGraph orchestration
-   ✅ Persistent workflow state
-   ✅ SQLite persistence
-   ✅ JWT Authentication
-   ✅ RBAC
-   ✅ Audit logs
-   ✅ Human escalation
-   ✅ REST API
-   ✅ Web Interface
-   ✅ Automated tests


## Future Improvements

-   Email notifications
-   SMS reminders
-   WebSocket updates
-   OCR improvements
-   Docker deployment
-   PostgreSQL support

## License

MIT License

------------------------------------------------------------------------

Built for the **AgentCare Build Challenge 2026** using a completely free
and open-source technology stack.

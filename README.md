# AgentCare -- Multi-Agent Healthcare Administration System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![Tests](https://img.shields.io/badge/Tests-36%20Passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

AgentCare is a multi-agent AI application built for the **AgentCare
Build Challenge 2026**. It automates hospital administrative workflows
such as appointment booking, department routing, document processing,
reminders, workflow tracking, and administrative escalations while
intentionally avoiding medical diagnosis or treatment.

## Features

-   Multi-agent workflow powered by LangGraph
-   Coordinator, Routing, Appointment, Document, Follow-up and Safety
    agents
-   JWT Authentication and Role-Based Access Control
-   Patient and Admin web dashboards
-   Appointment booking, cancellation and rescheduling
-   Document upload with checksum duplicate detection
-   Audit logging
-   Workflow persistence in SQLite
-   Reminder generation
-   Human escalation workflow
-   REST APIs and Bootstrap UI
-   Comprehensive automated test suite (**36 passing tests**)

## Technology Stack

  Layer            Technology
  ---------------- ------------------------------
  Backend          FastAPI, SQLAlchemy, Alembic
  AI               LangGraph, LangChain, Groq
  Database         SQLite
  Authentication   JWT, Passlib
  Frontend         Jinja2, Bootstrap 5
  Testing          pytest

## Architecture

``` mermaid
graph TD
User-->API
API-->Workflow
Workflow-->Coordinator
Coordinator-->Routing
Routing-->Appointment
Appointment-->Document
Document-->FollowUp
FollowUp-->Safety
Safety-->SQLite
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

## Screenshots

Add:

-   Home Page
-   Patient Dashboard
-   Admin Dashboard
-   Workflow Details
-   Appointment Booking
-   Document Upload

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

"""
AgentCare - Multi-Agent Healthcare Administration System

FastAPI application entry point.
"""

import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

# --------------------------------------------------
# API Routers
# --------------------------------------------------

from app.api import (
    auth,
    users,
    departments,
    doctors,
    slots,
    appointments,
    documents,
    admin,
    workflow,
)

# --------------------------------------------------
# Web Routers
# --------------------------------------------------

from app.web import (
    auth_web,
    patient_web,
    admin_web,
)

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="AgentCare",
    description="Multi-Agent Healthcare Administration System",
    version="1.0.0",
)

# --------------------------------------------------
# Templates
# --------------------------------------------------

templates = Jinja2Templates(directory="app/templates")

# Optional Jinja filter
templates.env.filters["tojson"] = json.dumps

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Static Files
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

# --------------------------------------------------
# API Routers
# --------------------------------------------------

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

app.include_router(
    departments.router,
    prefix="/departments",
    tags=["Departments"],
)

app.include_router(
    doctors.router,
    prefix="/doctors",
    tags=["Doctors"],
)

app.include_router(
    slots.router,
    prefix="/slots",
    tags=["Slots"],
)

app.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["Appointments"],
)

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin API"],
)

app.include_router(
    workflow.router,
    prefix="/workflow",
    tags=["Workflow"],
)

# --------------------------------------------------
# Web Routers
# --------------------------------------------------

app.include_router(
    auth_web.router,
    tags=["Web Authentication"],
)

app.include_router(
    patient_web.router,
    prefix="/patient",
    tags=["Patient Portal"],
)

app.include_router(
    admin_web.router,
    prefix="/admin",
    tags=["Admin Portal"],
)

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "AgentCare",
        "version": app.version,
        "environment": getattr(
            settings,
            "environment",
            "development",
        ),
    }

# --------------------------------------------------
# Error Pages
# --------------------------------------------------

@app.exception_handler(401)
async def unauthorized_handler(
    request: Request,
    exc: HTTPException,
):
    return HTMLResponse(
        content=templates.get_template(
            "error/401.html"
        ).render(
            {
                "request": request,
            }
        ),
        status_code=401,
    )


@app.exception_handler(403)
async def forbidden_handler(
    request: Request,
    exc: HTTPException,
):
    return HTMLResponse(
        content=templates.get_template(
            "error/403.html"
        ).render(
            {
                "request": request,
            }
        ),
        status_code=403,
    )


@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exc: HTTPException,
):
    return HTMLResponse(
        content=templates.get_template(
            "error/404.html"
        ).render(
            {
                "request": request,
            }
        ),
        status_code=404,
    )

# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
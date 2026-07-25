"""
AgentCare – Multi-Agent Healthcare Administration System
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, users, departments, doctors, slots, appointments, documents, admin
from app.api import workflow

app = FastAPI(
    title="AgentCare",
    description="Multi-Agent Healthcare Administration System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(departments.router, prefix="/departments", tags=["Departments"])
app.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
app.include_router(slots.router, prefix="/slots", tags=["Slots"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "AgentCare", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
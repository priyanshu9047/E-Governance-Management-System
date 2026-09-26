"""
E-Governance Service Management System — FastAPI Backend Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    auth_router,
    services_router,
    applications_router,
    documents_router,
    payments_router,
    complaints_router,
    notifications_router,
    admin_router,
)

app = FastAPI(
    title="E-Governance Service Management System",
    description=(
        "A digital platform for citizens to apply for government services, "
        "track applications, make payments, and receive notifications. "
        "Officers can review, approve/reject applications and view analytics."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(services_router.router)
app.include_router(applications_router.router)
app.include_router(documents_router.router)
app.include_router(payments_router.router)
app.include_router(complaints_router.router)
app.include_router(notifications_router.router)
app.include_router(admin_router.router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "E-Governance Service Management System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health():
    """API health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT

    uvicorn.run("backend.main:app", host=API_HOST, port=API_PORT, reload=True)

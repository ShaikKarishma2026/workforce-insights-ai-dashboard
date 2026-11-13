"""
Workforce Insights & AI Skills Analytics - FastAPI Main Application
Serves REST API routes and static enterprise React frontend.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.employees import router as employees_router, dept_router
from backend.routes.analytics import router as analytics_router
from backend.routes.predictions import router as predictions_router
from backend.routes.skill_gap import router as skill_gap_router
from backend.routes.assistant import router as assistant_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
CHARTS_DIR = BASE_DIR / "eda" / "charts"

app = FastAPI(
    title="Workforce Insights & AI-Powered Employee Skills Analytics Platform",
    description="Enterprise-grade HR Analytics, Machine Learning Predictions, and RAG-based AI Workforce Assistant API.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(employees_router)
app.include_router(dept_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(skill_gap_router)
app.include_router(assistant_router)

# Mount EDA charts for direct frontend rendering
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")

# Mount Frontend Static Assets
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Workforce Insights & AI Skills Analytics API",
        "version": "2.0.0"
    }

@app.get("/")
def serve_dashboard():
    """Serves the main single-page enterprise React dashboard."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "Workforce Insights API is running. Dashboard HTML is loading.",
        "docs_url": "/docs"
    }

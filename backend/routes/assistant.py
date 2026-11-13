"""
AI Assistant & Project Team Recommender REST API Endpoints
"""

from fastapi import APIRouter
from typing import Dict, Any

from backend.models import AIChatRequest, TeamRecommendRequest
from rag.rag_engine import get_rag_engine

router = APIRouter(prefix="/api/ai", tags=["AI Workforce Assistant"])

@router.post("/chat")
def chat_with_workforce_assistant(payload: AIChatRequest) -> Dict[str, Any]:
    """Retrieval-Augmented Generation chatbot endpoint for workforce analytics queries."""
    engine = get_rag_engine()
    response = engine.answer_query(payload.message)
    return response

@router.post("/recommend-team")
def recommend_project_team(payload: TeamRecommendRequest) -> Dict[str, Any]:
    """Finds top-matched employees for project staffing based on required skills and criteria."""
    engine = get_rag_engine()
    candidates = engine._find_employees_by_skills(payload.required_skills, limit=payload.team_size * 2)

    # Filter by minimum experience if specified
    filtered = [c for c in candidates if c["experience_years"] >= payload.min_experience_years]
    if len(filtered) < payload.team_size:
        filtered = candidates # fall back to top candidates

    selected = filtered[:payload.team_size]

    return {
        "project_name": payload.project_name,
        "required_skills": payload.required_skills,
        "team_size_requested": payload.team_size,
        "selected_candidates": selected,
        "team_readiness_score": round(sum(c["match_percentage"] for c in selected) / max(1, len(selected)), 1) if selected else 0.0
    }

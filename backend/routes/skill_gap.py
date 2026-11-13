"""
Skill Gap Analysis REST API Endpoints
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from backend.models import SkillGapRequest
from database.crud import get_employee

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARKS_PATH = BASE_DIR / "machine_learning" / "benchmarks.json"

router = APIRouter(prefix="/api/skills", tags=["Skill Gap Analysis"])

def load_benchmarks():
    if not BENCHMARKS_PATH.exists():
        return {}
    with open(BENCHMARKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/benchmarks")
def get_all_role_benchmarks():
    return load_benchmarks()

@router.post("/analyze-gap")
def analyze_skill_gap(payload: SkillGapRequest):
    benchmarks = load_benchmarks()
    target_role = payload.target_role

    if target_role not in benchmarks:
        raise HTTPException(
            status_code=400,
            detail=f"Target role '{target_role}' not found. Supported roles: {list(benchmarks.keys())}"
        )

    target_info = benchmarks[target_role]
    required_skills = target_info["required_skills"]
    optional_skills = target_info["optional_skills"]

    candidate_name = "Custom Candidate"
    current_role = "Applicant"
    exp = 3.0
    candidate_skills = []

    if payload.employee_id:
        emp = get_employee(payload.employee_id.upper())
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee {payload.employee_id} not found")
        candidate_name = emp["name"]
        current_role = emp["job_role"]
        exp = emp["experience_years"]
        candidate_skills = emp["technical_skills"]
    elif payload.current_skills:
        candidate_skills = payload.current_skills

    candidate_skills_lower = {s.strip().lower(): s for s in candidate_skills}

    matched_core = []
    missing_core = []
    for req in required_skills:
        if req.lower() in candidate_skills_lower:
            matched_core.append(req)
        else:
            missing_core.append(req)

    matched_optional = []
    missing_optional = []
    for opt in optional_skills:
        if opt.lower() in candidate_skills_lower:
            matched_optional.append(opt)
        else:
            missing_optional.append(opt)

    core_score = (len(matched_core) / max(1, len(required_skills))) * 80.0
    optional_score = (len(matched_optional) / max(1, len(optional_skills))) * 20.0
    match_percentage = round(min(100.0, core_score + optional_score), 1)

    if match_percentage >= 85:
        readiness = "Role Ready (Immediate Placement)"
        readiness_badge = "emerald"
    elif match_percentage >= 65:
        readiness = "Near Ready (Minor Upskilling Needed)"
        readiness_badge = "blue"
    elif match_percentage >= 45:
        readiness = "Developing (Targeted Training Required)"
        readiness_badge = "amber"
    else:
        readiness = "Foundational Stage (Extensive Upskilling Required)"
        readiness_badge = "rose"

    return {
        "candidate_name": candidate_name,
        "current_role": current_role,
        "target_role": target_role,
        "target_department": target_info["department"],
        "match_percentage": match_percentage,
        "readiness_status": readiness,
        "readiness_badge": readiness_badge,
        "skills_summary": {
            "current_skills": candidate_skills,
            "matched_core_skills": matched_core,
            "missing_core_skills": missing_core,
            "matched_optional_skills": matched_optional,
            "missing_optional_skills": missing_optional
        },
        "experience_check": {
            "candidate_experience": exp,
            "benchmark_min_experience": target_info["min_experience_years"],
            "meets_experience": exp >= target_info["min_experience_years"]
        },
        "recommended_trainings": target_info["recommended_trainings"]
    }

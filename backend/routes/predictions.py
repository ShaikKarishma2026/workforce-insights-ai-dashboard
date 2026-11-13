"""
Machine Learning Predictions REST API Endpoints
"""

import json
from pathlib import Path
import joblib
import numpy as np
from fastapi import APIRouter, HTTPException

from backend.models import AttritionPredictRequest
from database.crud import get_employee

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / "machine_learning"
MODEL_PATH = ML_DIR / "attrition_model.joblib"
METRICS_PATH = ML_DIR / "attrition_metrics.json"
CLUSTER_SUMMARY_PATH = ML_DIR / "cluster_summary.json"

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

DEPT_MAP = {
    "Customer Support": 0, "Data & AI": 1, "Engineering": 2,
    "Finance": 3, "Human Resources": 4, "Product": 5, "Sales & Marketing": 6
}

@router.post("/predict-attrition")
def predict_attrition(payload: AttritionPredictRequest):
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=500, detail="Attrition model is not trained yet")

    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    scaler = bundle["scaler"]

    if payload.employee_id:
        emp = get_employee(payload.employee_id.upper())
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee {payload.employee_id} not found")
        age = emp["age"]
        exp = emp["experience_years"]
        salary = emp["salary"]
        sat = emp["job_satisfaction"]
        wlb = emp["work_life_balance"]
        perf = emp["performance_rating"]
        projects = emp.get("projects_completed", int(exp * 1.5 + 2))
        ot = 1 if str(emp["overtime"]).lower() == "yes" else 0
        skills_cnt = len(emp["technical_skills"])
        has_train = 1 if emp["training_history"] else 0
        dept_code = DEPT_MAP.get(emp["department_name"], 2)
        gender_code = 1 if emp["gender"] == "Female" else (2 if emp["gender"] == "Non-Binary" else 0)
        emp_name = emp["name"]
    else:
        age = payload.age
        exp = payload.experience_years
        salary = payload.salary
        sat = payload.job_satisfaction
        wlb = payload.work_life_balance
        perf = payload.performance_rating
        projects = payload.projects_completed
        ot = 1 if str(payload.overtime).lower() == "yes" else 0
        skills_cnt = payload.skill_count
        has_train = payload.has_training
        dept_code = DEPT_MAP.get(payload.department, 2)
        gender_code = 1 if payload.gender == "Female" else (2 if payload.gender == "Non-Binary" else 0)
        emp_name = "Custom Profile"

    features = np.array([[
        age, exp, salary, sat, wlb, perf, projects,
        ot, skills_cnt, has_train, dept_code, gender_code
    ]])

    features_scaled = scaler.transform(features)
    prob = float(model.predict_proba(features_scaled)[0, 1])
    pred = int(prob >= 0.40)

    if prob >= 0.55:
        risk_level = "High Flight Risk"
        risk_color = "red"
    elif prob >= 0.28:
        risk_level = "Moderate Risk"
        risk_color = "amber"
    else:
        risk_level = "Low Flight Risk"
        risk_color = "emerald"

    drivers = []
    if ot == 1:
        drivers.append("Chronic Overtime Hours (+35% risk impact)")
    if sat <= 2:
        drivers.append("Low Job Satisfaction Rating (Score <= 2)")
    if wlb <= 2:
        drivers.append("Depressed Work-Life Balance Rating (Score <= 2)")
    if salary < (exp * 10000 + 40000):
        drivers.append("Below-Market Compensation Ratio Relative to Experience")
    if has_train == 0:
        drivers.append("No Recent Professional Training or Career Development")
    if not drivers:
        drivers.append("Healthy Work-Life Balance & Competitive Compensation")

    return {
        "employee_name": emp_name,
        "attrition_probability": round(prob * 100, 1),
        "prediction_binary": pred,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "key_risk_drivers": drivers,
        "model_inputs": {
            "age": age, "experience_years": exp, "salary": salary,
            "job_satisfaction": sat, "work_life_balance": wlb,
            "overtime": "Yes" if ot == 1 else "No",
            "performance_rating": perf
        }
    }

@router.get("/clusters")
def get_skill_clusters():
    if not CLUSTER_SUMMARY_PATH.exists():
        raise HTTPException(status_code=500, detail="Cluster summary not found")
    with open(CLUSTER_SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/metrics")
def get_model_evaluation_metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=500, detail="Metrics file not found")
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

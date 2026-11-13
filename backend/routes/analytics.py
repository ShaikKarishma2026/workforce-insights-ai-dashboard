"""
Workforce Analytics REST API Endpoints
"""

import json
import sqlite3
from pathlib import Path
from fastapi import APIRouter
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "database" / "workforce.db"
EDA_INSIGHTS_PATH = BASE_DIR / "eda" / "eda_insights.json"

router = APIRouter(prefix="/api/analytics", tags=["Workforce Analytics"])

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/overview")
def get_overview_kpis() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total_employees,
            AVG(salary) as avg_salary,
            AVG(experience_years) as avg_experience,
            AVG(performance_rating) as avg_performance,
            AVG(CASE WHEN attrition = 0 THEN 1.0 ELSE 0.0 END) * 100 as retention_rate
        FROM employees
    """)
    kpi_row = cursor.fetchone()

    cursor.execute("""
        SELECT d.name as department, COUNT(e.id) as count, AVG(e.salary) as avg_salary
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.name
        ORDER BY count DESC
    """)
    dept_rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT gender, COUNT(*) as count
        FROM employees
        GROUP BY gender
        ORDER BY count DESC
    """)
    gender_rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM employee_skills
        WHERE skill_type = 'Technical'
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 1
    """)
    top_skill_row = cursor.fetchone()
    top_skill = top_skill_row["skill_name"] if top_skill_row else "Python"

    cursor.execute("""
        SELECT tenure_tier, COUNT(*) as count
        FROM employees
        WHERE tenure_tier IS NOT NULL
        GROUP BY tenure_tier
        ORDER BY count DESC
    """)
    tenure_rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "kpis": {
            "total_employees": kpi_row["total_employees"],
            "avg_salary": round(kpi_row["avg_salary"] or 0, 0),
            "avg_experience_years": round(kpi_row["avg_experience"] or 0, 1),
            "avg_performance_rating": round(kpi_row["avg_performance"] or 0, 2),
            "retention_rate_pct": round(kpi_row["retention_rate"] or 0, 1),
            "top_technical_skill": top_skill
        },
        "department_distribution": dept_rows,
        "gender_distribution": gender_rows,
        "tenure_distribution": tenure_rows
    }

@router.get("/skills")
def get_skills_analytics() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM employee_skills
        WHERE skill_type = 'Technical'
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 15
    """)
    top_tech = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM employee_skills
        WHERE skill_type = 'Soft'
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 10
    """)
    top_soft = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT d.name as department, s.skill_name, COUNT(*) as skill_count
        FROM employee_skills s
        JOIN employees e ON s.employee_id = e.employee_id
        JOIN departments d ON e.department_id = d.id
        WHERE s.skill_type = 'Technical'
        GROUP BY d.name, s.skill_name
        ORDER BY d.name, skill_count DESC
    """)
    matrix_rows = cursor.fetchall()
    dept_matrix = {}
    for r in matrix_rows:
        dept = r["department"]
        if dept not in dept_matrix:
            dept_matrix[dept] = []
        if len(dept_matrix[dept]) < 5:
            dept_matrix[dept].append({"skill": r["skill_name"], "count": r["skill_count"]})

    conn.close()

    return {
        "top_technical_skills": top_tech,
        "top_soft_skills": top_soft,
        "department_skills_matrix": dept_matrix
    }

@router.get("/departments")
def get_department_analytics() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            d.id,
            d.name,
            d.department_code,
            d.manager_name,
            d.budget,
            COUNT(e.id) as headcount,
            ROUND(AVG(e.salary), 0) as avg_salary,
            ROUND(MIN(e.salary), 0) as min_salary,
            ROUND(MAX(e.salary), 0) as max_salary,
            ROUND(AVG(e.performance_rating), 2) as avg_performance,
            ROUND(AVG(e.experience_years), 1) as avg_experience,
            ROUND(AVG(CASE WHEN e.attrition = 1 THEN 1.0 ELSE 0.0 END) * 100, 1) as attrition_rate
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id
        ORDER BY headcount DESC
    """)
    dept_metrics = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {"departments": dept_metrics}

@router.get("/eda")
def get_eda_reports() -> Dict[str, Any]:
    if EDA_INSIGHTS_PATH.exists():
        with open(EDA_INSIGHTS_PATH, "r", encoding="utf-8") as f:
            insights = json.load(f)
    else:
        insights = {}

    charts = [
        {"id": "dept_distribution", "title": "Headcount Distribution by Department", "filename": "1_department_distribution.png"},
        {"id": "gender_distribution", "title": "Gender Diversity Breakdown", "filename": "2_gender_distribution.png"},
        {"id": "experience_distribution", "title": "Experience Years Distribution (KDE)", "filename": "3_experience_distribution.png"},
        {"id": "salary_distribution", "title": "Salary Distribution by Department", "filename": "4_salary_distribution.png"},
        {"id": "top_technical_skills", "title": "Top In-Demand Technical Skills", "filename": "5_top_technical_skills.png"},
        {"id": "dept_performance", "title": "Department Average Performance Ratings", "filename": "6_dept_performance.png"},
        {"id": "skill_gaps_dept", "title": "Average Skill Density by Department", "filename": "7_skill_gaps_dept.png"},
        {"id": "exp_vs_performance", "title": "Experience vs Performance Correlation", "filename": "8_exp_vs_performance.png"},
        {"id": "training_vs_performance", "title": "Training Completion vs Performance Lift", "filename": "9_training_vs_performance.png"},
        {"id": "correlation_heatmap", "title": "Workforce Metrics Correlation Heatmap", "filename": "10_correlation_heatmap.png"}
    ]

    return {
        "insights": insights,
        "charts": charts
    }

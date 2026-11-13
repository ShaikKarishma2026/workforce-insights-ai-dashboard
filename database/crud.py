"""
Workforce Database CRUD Module
Provides complete Create, Read, Update, Delete (CRUD) operations
and complex relational queries for employee management.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "workforce.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- CREATE -----------------
def create_employee(
    name: str,
    age: int,
    gender: str,
    department_name: str,
    job_role: str,
    experience_years: float,
    salary: float,
    education: str,
    location: str,
    technical_skills: List[str],
    soft_skills: List[str],
    performance_rating: float = 3.5,
    overtime: str = "No",
    job_satisfaction: int = 3,
    work_life_balance: int = 3,
    training_course: Optional[str] = None
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generate next employee ID
    cursor.execute("SELECT MAX(CAST(SUBSTR(employee_id, 4) AS INTEGER)) FROM employees")
    max_id = cursor.fetchone()[0] or 0
    new_emp_id = f"EMP{max_id + 1:04d}"

    # Find department ID
    cursor.execute("SELECT id FROM departments WHERE name = ?", (department_name,))
    dept_row = cursor.fetchone()
    if not dept_row:
        cursor.execute("SELECT id FROM departments LIMIT 1")
        dept_id = cursor.fetchone()[0]
    else:
        dept_id = dept_row["id"]

    # Calculate tenure & performance tiers
    tenure_tier = "Entry Level (0-2y)" if experience_years < 2 else ("Mid Level (3-5y)" if experience_years < 5 else "Senior (6-10y)")
    perf_tier = "High Performer" if performance_rating >= 3.6 else ("Meets Expectations" if performance_rating >= 2.8 else "Needs Improvement")

    cursor.execute("""
        INSERT INTO employees (
            employee_id, name, age, gender, department_id, job_role, experience_years,
            salary, education, location, overtime, job_satisfaction, work_life_balance,
            performance_rating, attrition, tenure_tier, performance_tier
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (
        new_emp_id, name, age, gender, dept_id, job_role, experience_years,
        salary, education, location, overtime, job_satisfaction, work_life_balance,
        performance_rating, tenure_tier, perf_tier
    ))

    # Insert technical skills
    for s in technical_skills:
        s_clean = s.strip()
        if s_clean:
            cursor.execute(
                "INSERT INTO employee_skills (employee_id, skill_name, skill_type, proficiency_level) VALUES (?, ?, 'Technical', 'Advanced')",
                (new_emp_id, s_clean)
            )

    # Insert soft skills
    for s in soft_skills:
        s_clean = s.strip()
        if s_clean:
            cursor.execute(
                "INSERT INTO employee_skills (employee_id, skill_name, skill_type, proficiency_level) VALUES (?, ?, 'Soft', 'Advanced')",
                (new_emp_id, s_clean)
            )

    # Insert Training
    if training_course and training_course.strip().lower() not in ["none", ""]:
        cursor.execute(
            "INSERT INTO training_records (employee_id, course_name, completion_status, score, completion_date) VALUES (?, ?, 'Completed', 90, 'Recent')",
            (new_emp_id, training_course.strip())
        )

    # Insert initial performance record
    cursor.execute(
        "INSERT INTO performance_records (employee_id, review_period, rating, goals_achieved, feedback, reviewer) VALUES (?, 'Initial Review', ?, 90, 'Initial Onboarding Review', 'HR Lead')",
        (new_emp_id, performance_rating)
    )

    # Update department head_count
    cursor.execute("UPDATE departments SET head_count = head_count + 1 WHERE id = ?", (dept_id,))

    conn.commit()
    conn.close()

    return get_employee(new_emp_id)

# ----------------- READ -----------------
def get_employee(employee_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.*, d.name AS department_name, d.department_code, d.manager_name AS department_manager
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE e.employee_id = ?
    """, (employee_id,))
    emp_row = cursor.fetchone()

    if not emp_row:
        conn.close()
        return None

    emp_dict = dict(emp_row)

    cursor.execute("SELECT skill_name, skill_type, proficiency_level FROM employee_skills WHERE employee_id = ?", (employee_id,))
    skills = cursor.fetchall()
    emp_dict["technical_skills"] = [s["skill_name"] for s in skills if s["skill_type"] == "Technical"]
    emp_dict["soft_skills"] = [s["skill_name"] for s in skills if s["skill_type"] == "Soft"]

    cursor.execute("SELECT course_name, completion_status, score, completion_date FROM training_records WHERE employee_id = ?", (employee_id,))
    trainings = cursor.fetchall()
    emp_dict["training_history"] = [dict(t) for t in trainings]

    cursor.execute("SELECT review_period, rating, goals_achieved, feedback, reviewer FROM performance_records WHERE employee_id = ?", (employee_id,))
    reviews = cursor.fetchall()
    emp_dict["performance_reviews"] = [dict(r) for r in reviews]

    conn.close()
    return emp_dict

def list_employees(
    department: Optional[str] = None,
    min_exp: Optional[float] = None,
    max_exp: Optional[float] = None,
    skill: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT e.employee_id, e.name, e.age, e.gender, d.name AS department, e.job_role,
               e.experience_years, e.salary, e.education, e.location, e.performance_rating,
               e.attrition, e.job_satisfaction, e.work_life_balance, e.overtime
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        LEFT JOIN employee_skills s ON e.employee_id = s.employee_id
        WHERE 1=1
    """
    params = []

    if department and department != "All":
        query += " AND d.name = ?"
        params.append(department)

    if min_exp is not None:
        query += " AND e.experience_years >= ?"
        params.append(min_exp)

    if max_exp is not None:
        query += " AND e.experience_years <= ?"
        params.append(max_exp)

    if skill and skill.strip():
        query += " AND LOWER(s.skill_name) LIKE ?"
        params.append(f"%{skill.strip().lower()}%")

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query += " AND (LOWER(e.name) LIKE ? OR LOWER(e.employee_id) LIKE ? OR LOWER(e.job_role) LIKE ? OR LOWER(e.location) LIKE ?)"
        params.extend([term, term, term, term])

    count_query = f"SELECT COUNT(*) FROM ({query})"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    query += " ORDER BY e.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        item = dict(r)
        cursor.execute("SELECT skill_name FROM employee_skills WHERE employee_id = ? AND skill_type = 'Technical' LIMIT 4", (item["employee_id"],))
        skills_sample = [s[0] for s in cursor.fetchall()]
        item["top_skills"] = ", ".join(skills_sample)
        results.append(item)

    conn.close()
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "employees": results
    }

# ----------------- UPDATE -----------------
def update_employee(employee_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    allowed_fields = [
        "name", "age", "gender", "job_role", "experience_years", "salary",
        "education", "location", "overtime", "job_satisfaction", "work_life_balance",
        "performance_rating", "attrition"
    ]

    set_clauses = []
    values = []

    for k in allowed_fields:
        if k in updates and updates[k] is not None:
            set_clauses.append(f"{k} = ?")
            values.append(updates[k])

    if "department" in updates and updates["department"]:
        cursor.execute("SELECT id FROM departments WHERE name = ?", (updates["department"],))
        dept_row = cursor.fetchone()
        if dept_row:
            set_clauses.append("department_id = ?")
            values.append(dept_row["id"])

    if set_clauses:
        values.append(employee_id)
        update_sql = f"UPDATE employees SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE employee_id = ?"
        cursor.execute(update_sql, values)

    if "technical_skills" in updates and isinstance(updates["technical_skills"], list):
        cursor.execute("DELETE FROM employee_skills WHERE employee_id = ? AND skill_type = 'Technical'", (employee_id,))
        for s in updates["technical_skills"]:
            if str(s).strip():
                cursor.execute(
                    "INSERT INTO employee_skills (employee_id, skill_name, skill_type, proficiency_level) VALUES (?, ?, 'Technical', 'Advanced')",
                    (employee_id, str(s).strip())
                )

    conn.commit()
    conn.close()

    return get_employee(employee_id)

# ----------------- DELETE -----------------
def delete_employee(employee_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT department_id FROM employees WHERE employee_id = ?", (employee_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    dept_id = row["department_id"]

    cursor.execute("DELETE FROM employee_skills WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM performance_records WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM training_records WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
    cursor.execute("UPDATE departments SET head_count = MAX(0, head_count - 1) WHERE id = ?", (dept_id,))

    conn.commit()
    conn.close()
    return True

# ----------------- DEPARTMENTS -----------------
def get_all_departments() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

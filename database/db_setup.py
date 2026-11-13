"""
Database Initialization & Seeding Module
Initializes relational database using SQLAlchemy and executes schema.sql.
Populates:
- departments
- employees
- employee_skills
- performance_records
- training_records
"""

import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "workforce.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
CLEANED_CSV = BASE_DIR / "dataset" / "dataset_cleaned.csv"

DATABASE_URL = f"sqlite:///{DB_PATH}"

def get_engine():
    return create_engine(DATABASE_URL, echo=False)

def initialize_database():
    print("=" * 60)
    print("INITIALIZING WORKFORCE RELATIONAL DATABASE")
    print("=" * 60)

    # 1. Read SQL DDL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    # 2. Execute DDL via sqlite3 script
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(ddl_script)
    conn.commit()
    print("[1/3] Created relational tables & indexes successfully.")

    # 3. Load Cleaned Dataset
    df = pd.read_csv(CLEANED_CSV)
    print(f"[2/3] Loaded {len(df)} cleaned employee records for ingestion.")

    # 4. Insert Departments
    dept_managers = {
        "Engineering": "Marcus Vance",
        "Data & AI": "Dr. Sarah Chen",
        "Product": "Rachel Bennett",
        "Human Resources": "Devon Hayes",
        "Sales & Marketing": "Carlos Mendez",
        "Finance": "Audrey Ross",
        "Customer Support": "Liam O'Connor"
    }

    dept_budgets = {
        "Engineering": 3500000.00,
        "Data & AI": 2800000.00,
        "Product": 1800000.00,
        "Human Resources": 950000.00,
        "Sales & Marketing": 2200000.00,
        "Finance": 1400000.00,
        "Customer Support": 900000.00
    }

    unique_depts = sorted(df["Department"].unique())
    dept_id_map = {}

    cursor.execute("DELETE FROM employee_skills")
    cursor.execute("DELETE FROM performance_records")
    cursor.execute("DELETE FROM training_records")
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM departments")
    conn.commit()

    for idx, d_name in enumerate(unique_depts, start=1):
        code = d_name[:3].upper() if len(d_name) >= 3 else "GEN"
        manager = dept_managers.get(d_name, "Senior Director")
        budget = dept_budgets.get(d_name, 1000000.00)
        h_count = int((df["Department"] == d_name).sum())
        
        cursor.execute(
            "INSERT INTO departments (id, department_code, name, budget, head_count, manager_name) VALUES (?, ?, ?, ?, ?, ?)",
            (idx, f"DPT-{code}", d_name, budget, h_count, manager)
        )
        dept_id_map[d_name] = idx

    conn.commit()

    # 5. Insert Employees, Skills, Performance, and Training
    emp_skill_rows = []
    perf_rows = []
    training_rows = []

    for _, row in df.iterrows():
        emp_id = row["Employee_ID"]
        dept_id = dept_id_map[row["Department"]]

        cursor.execute("""
            INSERT INTO employees (
                employee_id, name, age, gender, department_id, job_role, experience_years,
                salary, education, location, overtime, job_satisfaction, work_life_balance,
                performance_rating, attrition, tenure_tier, performance_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_id, row["Name"], int(row["Age"]), row["Gender"], dept_id, row["Job_Role"],
            float(row["Experience_Years"]), float(row["Salary"]), row["Education"], row["Location"],
            row["Overtime"], int(row["Job_Satisfaction"]), int(row["Work_Life_Balance"]),
            float(row["Performance_Rating"]), int(row["Attrition"]), row["Tenure_Tier"], row["Performance_Tier"]
        ))

        tech_skills = [s.strip() for s in str(row["Technical_Skills"]).split(",") if s.strip()]
        for s in tech_skills:
            prof = "Expert" if row["Experience_Years"] >= 10 else ("Advanced" if row["Experience_Years"] >= 5 else "Intermediate")
            emp_skill_rows.append((emp_id, s, "Technical", prof))

        soft_skills = [s.strip() for s in str(row["Soft_Skills"]).split(",") if s.strip()]
        for s in soft_skills:
            emp_skill_rows.append((emp_id, s, "Soft", "Advanced"))

        perf_rows.append((
            emp_id, "FY2025-Annual", float(row["Performance_Rating"]),
            int(min(100, max(60, row["Performance_Rating"] * 20))),
            f"Consistently demonstrated key competencies in {row['Job_Role']}.",
            dept_managers.get(row["Department"], "Department Lead")
        ))

        training_course = str(row["Training_History"]).strip()
        if training_course and training_course.lower() not in ["none", "not enrolled"]:
            training_rows.append((emp_id, training_course, "Completed", 88, "2025-Q3"))

    cursor.executemany("INSERT INTO employee_skills (employee_id, skill_name, skill_type, proficiency_level) VALUES (?, ?, ?, ?)", emp_skill_rows)
    cursor.executemany("INSERT INTO performance_records (employee_id, review_period, rating, goals_achieved, feedback, reviewer) VALUES (?, ?, ?, ?, ?, ?)", perf_rows)
    cursor.executemany("INSERT INTO training_records (employee_id, course_name, completion_status, score, completion_date) VALUES (?, ?, ?, ?, ?)", training_rows)

    conn.commit()
    conn.close()

    print(f"[3/3] Successfully inserted:")
    print(f"      - {len(unique_depts)} Departments")
    print(f"      - {len(df)} Employees")
    print(f"      - {len(emp_skill_rows)} Normalized Skill entries")
    print(f"      - {len(perf_rows)} Performance evaluations")
    print(f"      - {len(training_rows)} Training certifications")
    print(f"Database ready at: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    initialize_database()

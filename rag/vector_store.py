"""
Vector Store & Knowledge Base for Workforce RAG
Constructs a comprehensive workforce knowledge base from database records
and builds a TF-IDF semantic vector indexing engine with cosine similarity search.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "workforce.db"
BENCHMARKS_PATH = BASE_DIR / "machine_learning" / "benchmarks.json"
KB_PATH = BASE_DIR / "rag" / "knowledge_base.json"

class WorkforceVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer = None
        self.doc_vectors = None
        self._build_or_load_knowledge_base()

    def _build_or_load_knowledge_base(self):
        docs = []

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Employee Documents
        cursor.execute("""
            SELECT e.employee_id, e.name, e.job_role, d.name AS department, e.experience_years,
                   e.salary, e.performance_rating, e.location, e.overtime, e.job_satisfaction,
                   e.work_life_balance, e.attrition
            FROM employees e
            JOIN departments d ON e.department_id = d.id
        """)
        emps = cursor.fetchall()

        for emp in emps:
            e_id = emp["employee_id"]
            cursor.execute("SELECT skill_name, skill_type FROM employee_skills WHERE employee_id = ?", (e_id,))
            skill_rows = cursor.fetchall()
            tech_skills = [s["skill_name"] for s in skill_rows if s["skill_type"] == "Technical"]
            soft_skills = [s["skill_name"] for s in skill_rows if s["skill_type"] == "Soft"]

            cursor.execute("SELECT course_name FROM training_records WHERE employee_id = ?", (e_id,))
            trainings = [t["course_name"] for t in cursor.fetchall()]

            text_content = (
                f"Employee ID: {e_id}. Name: {emp['name']}. Job Role: {emp['job_role']}. "
                f"Department: {emp['department']}. Experience: {emp['experience_years']} years. "
                f"Location: {emp['location']}. Performance Rating: {emp['performance_rating']}/5.0. "
                f"Salary: ${emp['salary']:,.0f}. Overtime: {emp['overtime']}. "
                f"Technical Skills: {', '.join(tech_skills)}. Soft Skills: {', '.join(soft_skills)}. "
                f"Training & Certifications: {', '.join(trainings) if trainings else 'None'}. "
                f"Flight Risk / Attrition Status: {'High Attrition' if emp['attrition'] == 1 else 'Retained / Low Risk'}."
            )

            docs.append({
                "doc_id": f"emp_{e_id}",
                "category": "employee",
                "title": f"{emp['name']} ({emp['job_role']})",
                "text": text_content,
                "metadata": {
                    "employee_id": e_id,
                    "name": emp["name"],
                    "role": emp["job_role"],
                    "department": emp["department"],
                    "experience": emp["experience_years"],
                    "performance": emp["performance_rating"],
                    "technical_skills": tech_skills,
                    "soft_skills": soft_skills,
                    "location": emp["location"]
                }
            })

        # 2. Department Overview Documents
        cursor.execute("SELECT * FROM departments")
        depts = cursor.fetchall()
        for d in depts:
            d_name = d["name"]
            cursor.execute("""
                SELECT COUNT(*), AVG(e.experience_years), AVG(e.salary), AVG(e.performance_rating)
                FROM employees e WHERE e.department_id = ?
            """, (d["id"],))
            stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT s.skill_name, COUNT(*) as cnt
                FROM employee_skills s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE e.department_id = ? AND s.skill_type = 'Technical'
                GROUP BY s.skill_name ORDER BY cnt DESC LIMIT 8
            """, (d["id"],))
            top_dept_skills = [f"{r['skill_name']} ({r['cnt']})" for r in cursor.fetchall()]

            d_text = (
                f"Department: {d_name} (Code: {d['department_code']}). "
                f"Department Leader / Manager: {d['manager_name']}. Total Headcount: {stats[0]} employees. "
                f"Annual Allocated Budget: ${d['budget']:,.2f}. "
                f"Average Experience: {stats[1]:.1f} years. Average Salary: ${stats[2]:,.0f}. "
                f"Average Performance Rating: {stats[3]:.2f}/5.0. "
                f"Most Prominent Technical Skills: {', '.join(top_dept_skills)}."
            )

            docs.append({
                "doc_id": f"dept_{d['id']}",
                "category": "department",
                "title": f"Department Profile: {d_name}",
                "text": d_text,
                "metadata": {
                    "department_id": d["id"],
                    "department_name": d_name,
                    "manager": d["manager_name"],
                    "headcount": stats[0],
                    "budget": d["budget"]
                }
            })

        conn.close()

        # 3. Role Benchmark Documents
        if BENCHMARKS_PATH.exists():
            with open(BENCHMARKS_PATH, "r", encoding="utf-8") as f:
                benchmarks = json.load(f)
            for role_name, b_info in benchmarks.items():
                b_text = (
                    f"Job Role Benchmark: {role_name}. Department: {b_info['department']}. "
                    f"Minimum Recommended Experience: {b_info['min_experience_years']} years. "
                    f"Core Required Technical Skills: {', '.join(b_info['required_skills'])}. "
                    f"Optional & Complementary Skills: {', '.join(b_info['optional_skills'])}. "
                    f"Key Soft Skills: {', '.join(b_info['soft_skills'])}. "
                    f"Recommended Training Certifications: {', '.join(b_info['recommended_trainings'])}."
                )
                docs.append({
                    "doc_id": f"role_{role_name.replace(' ', '_').lower()}",
                    "category": "role_benchmark",
                    "title": f"Skill Benchmark: {role_name}",
                    "text": b_text,
                    "metadata": {
                        "role": role_name,
                        "department": b_info["department"],
                        "required_skills": b_info["required_skills"],
                        "recommended_trainings": b_info["recommended_trainings"]
                    }
                })

        # 4. Training Courses Catalog
        course_catalog = [
            ("AWS Certified Solutions Architect", "Comprehensive cloud architecture certification covering VPCs, IAM, EC2, Lambda, S3, ECS, fault tolerance, and high availability."),
            ("Advanced Machine Learning & Deep Learning", "Hands-on specialization in PyTorch, neural networks, computer vision, transformers, NLP, model optimization, and deployment."),
            ("Full-Stack Web Development Bootcamp", "Modern web engineering covering React 18, TypeScript, Node.js, Express, PostgreSQL, REST APIs, and authentication workflows."),
            ("Agile Leadership & Scrum Master Certification", "Coaching team velocity, sprint roadmapping, stakeholder management, Kanban, and modern servant leadership."),
            ("Executive Data Analytics & Storytelling", "Transforming raw data into actionable boardroom visualizations using SQL, Power BI, Tableau, and statistical storytelling."),
            ("DevOps, Docker & Kubernetes in Production", "CI/CD automation, Docker containerization, Kubernetes helm charts, Prometheus monitoring, and zero-downtime deployments."),
            ("Financial Modeling & Valuation Analyst (FMVA)", "Advanced corporate finance, 3-statement modeling, DCF valuation, variance analysis, and M&A simulations."),
            ("AI Ethics & Responsible Generative AI", "Governance, bias detection in ML pipelines, compliance frameworks, prompt engineering safety, and model auditing.")
        ]
        for c_title, c_desc in course_catalog:
            docs.append({
                "doc_id": f"course_{c_title.replace(' ', '_').lower()}",
                "category": "training_course",
                "title": f"Course: {c_title}",
                "text": f"Training Course: {c_title}. Curriculum: {c_desc}",
                "metadata": {"course_name": c_title}
            })

        self.documents = docs

        KB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(KB_PATH, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)

        corpus = [d["text"] for d in docs]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
        self.doc_vectors = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5, category: str = None) -> List[Dict[str, Any]]:
        if not self.vectorizer or self.doc_vectors is None:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_vectors).flatten()

        ranked_indices = np.argsort(sims)[::-1]
        results = []

        for idx in ranked_indices:
            score = float(sims[idx])
            if score <= 0.01:
                continue

            doc = self.documents[idx]
            if category and doc["category"] != category:
                continue

            results.append({
                "score": round(score, 4),
                "doc_id": doc["doc_id"],
                "category": doc["category"],
                "title": doc["title"],
                "text": doc["text"],
                "metadata": doc["metadata"]
            })

            if len(results) >= top_k:
                break

        return results

_store_instance = None

def get_vector_store() -> WorkforceVectorStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = WorkforceVectorStore()
    return _store_instance

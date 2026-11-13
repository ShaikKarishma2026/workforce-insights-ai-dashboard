"""
Machine Learning Training Module
Trains:
1. Employee Attrition Classifier (Random Forest + Evaluation Metrics)
2. K-Means Employee Skill Clustering (Feature vectorization + Persona identification)
3. Job-Role Benchmark Skill Gap Engine
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_CSV = BASE_DIR / "dataset" / "dataset_cleaned.csv"
ML_DIR = BASE_DIR / "machine_learning"
ML_DIR.mkdir(parents=True, exist_ok=True)

# ----------------- 1. ATTRITION PREDICTION -----------------
def train_attrition_model(df: pd.DataFrame):
    print("\n--- [A] Training Employee Attrition Prediction Model ---")
    
    feature_cols = [
        "Age", "Experience_Years", "Salary", "Job_Satisfaction",
        "Work_Life_Balance", "Performance_Rating", "Projects_Completed",
        "Overtime_Code", "Skill_Count", "Has_Training", "Department_Code", "Gender_Code"
    ]
    
    X = df[feature_cols].copy()
    y = df["Attrition"].copy()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    clf = RandomForestClassifier(
        n_estimators=120, max_depth=6, random_state=42, class_weight="balanced"
    )
    clf.fit(X_train_scaled, y_train)
    
    y_pred = clf.predict(X_test_scaled)
    y_prob = clf.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print(f"Attrition Model Performance:")
    print(f"  - Accuracy:  {acc * 100:.2f}%")
    print(f"  - Precision: {prec * 100:.2f}%")
    print(f"  - Recall:    {rec * 100:.2f}%")
    print(f"  - F1-Score:  {f1 * 100:.2f}%")
    print(f"  - ROC-AUC:   {auc:.3f}")
    
    importances = dict(zip(feature_cols, clf.feature_importances_))
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    
    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": cm,
        "feature_importances": {k: round(v, 4) for k, v in sorted_importances.items()},
        "feature_cols": feature_cols
    }
    
    joblib.dump({"model": clf, "scaler": scaler, "features": feature_cols}, ML_DIR / "attrition_model.joblib")
    with open(ML_DIR / "attrition_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Saved attrition model to {ML_DIR / 'attrition_model.joblib'}")
    return metrics

# ----------------- 2. EMPLOYEE SKILL CLUSTERING -----------------
def train_skill_clustering(df: pd.DataFrame):
    print("\n--- [B] Training Employee Skill Clustering (K-Means) ---")
    
    tfidf = TfidfVectorizer(max_features=25, token_pattern=r"(?u)\b[\w\+\-\./#]+\b")
    skill_vectors = tfidf.fit_transform(df["Technical_Skills"]).toarray()
    
    num_scaler = StandardScaler()
    num_features = num_scaler.fit_transform(df[["Experience_Years", "Performance_Rating", "Skill_Count"]])
    
    X_cluster = np.hstack([skill_vectors * 2.0, num_features])
    
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_cluster)
    df["Cluster"] = cluster_labels
    
    cluster_summaries = []
    
    cluster_persona_titles = {
        0: "Full-Stack & Cloud System Architects",
        1: "Data, Analytics & AI Specialists",
        2: "Senior Technical & Domain Leaders",
        3: "Agile Practitioners & Operational Specialists"
    }
    
    for c_id in range(k):
        sub_df = df[df["Cluster"] == c_id]
        avg_exp = float(sub_df["Experience_Years"].mean())
        avg_sal = float(sub_df["Salary"].mean())
        avg_perf = float(sub_df["Performance_Rating"].mean())
        dept_mode = sub_df["Department"].mode().iloc[0] if not sub_df["Department"].empty else "Engineering"
        
        sub_skills = []
        for s in sub_df["Technical_Skills"]:
            for item in str(s).split(","):
                clean = item.strip()
                if clean:
                    sub_skills.append(clean)
        top_skills = pd.Series(sub_skills).value_counts().head(5).to_dict()
        
        summary = {
            "cluster_id": c_id,
            "title": cluster_persona_titles.get(c_id, f"Cluster {c_id}"),
            "employee_count": len(sub_df),
            "percentage": round(len(sub_df) / len(df) * 100, 1),
            "avg_experience_years": round(avg_exp, 1),
            "avg_salary": round(avg_sal, 0),
            "avg_performance": round(avg_perf, 2),
            "dominant_department": dept_mode,
            "top_skills": top_skills,
            "description": f"Group of {len(sub_df)} professionals averaging {avg_exp:.1f} years of experience and ${avg_sal:,.0f} median compensation, primarily skilled in {', '.join(list(top_skills.keys())[:3])}."
        }
        cluster_summaries.append(summary)
        
    joblib.dump({"kmeans": kmeans, "tfidf": tfidf, "num_scaler": num_scaler}, ML_DIR / "cluster_model.joblib")
    with open(ML_DIR / "cluster_summary.json", "w", encoding="utf-8") as f:
        json.dump(cluster_summaries, f, indent=2)
        
    print(f"Saved clustering model to {ML_DIR / 'cluster_model.joblib'}")
    return cluster_summaries

# ----------------- 3. JOB ROLE SKILL BENCHMARKS -----------------
def create_role_benchmarks():
    print("\n--- [C] Establishing Job-Role Skill Benchmarks ---")
    
    benchmarks = {
        "Data Scientist": {
            "department": "Data & AI",
            "required_skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn", "Statistics"],
            "optional_skills": ["Deep Learning", "AWS", "BigQuery", "PyTorch"],
            "soft_skills": ["Problem Solving", "Critical Thinking", "Communication"],
            "min_experience_years": 2.0,
            "recommended_trainings": [
                "Advanced Machine Learning & Deep Learning",
                "Executive Data Analytics & Storytelling"
            ]
        },
        "Senior Data Scientist": {
            "department": "Data & AI",
            "required_skills": ["Python", "SQL", "Machine Learning", "Deep Learning", "PyTorch", "Statistics", "AWS"],
            "optional_skills": ["Spark", "TensorFlow", "Data Modeling", "BigQuery"],
            "soft_skills": ["Leadership", "Mentorship", "Problem Solving", "Communication"],
            "min_experience_years": 5.0,
            "recommended_trainings": [
                "AI Ethics & Responsible Generative AI",
                "Executive Data Analytics & Storytelling"
            ]
        },
        "Machine Learning Engineer": {
            "department": "Data & AI",
            "required_skills": ["Python", "Machine Learning", "Docker", "AWS", "Scikit-Learn", "REST APIs"],
            "optional_skills": ["PyTorch", "Kubernetes", "CI/CD", "Spark"],
            "soft_skills": ["Problem Solving", "Teamwork", "Adaptability"],
            "min_experience_years": 3.0,
            "recommended_trainings": [
                "DevOps, Docker & Kubernetes in Production",
                "Advanced Machine Learning & Deep Learning"
            ]
        },
        "Data Analyst": {
            "department": "Data & AI",
            "required_skills": ["SQL", "Python", "Tableau", "Power BI", "Statistics"],
            "optional_skills": ["Pandas", "Excel", "BigQuery"],
            "soft_skills": ["Communication", "Attention to Detail", "Critical Thinking"],
            "min_experience_years": 1.0,
            "recommended_trainings": [
                "Executive Data Analytics & Storytelling"
            ]
        },
        "Software Engineer": {
            "department": "Engineering",
            "required_skills": ["JavaScript", "React", "Node.js", "Git", "REST APIs"],
            "optional_skills": ["Docker", "PostgreSQL", "CI/CD", "AWS"],
            "soft_skills": ["Teamwork", "Problem Solving", "Collaboration"],
            "min_experience_years": 1.5,
            "recommended_trainings": [
                "Full-Stack Web Development Bootcamp",
                "DevOps, Docker & Kubernetes in Production"
            ]
        },
        "Senior Software Engineer": {
            "department": "Engineering",
            "required_skills": ["JavaScript", "React", "Node.js", "Docker", "Microservices", "REST APIs", "Git"],
            "optional_skills": ["Kubernetes", "AWS", "PostgreSQL", "CI/CD", "Java"],
            "soft_skills": ["Leadership", "Mentorship", "Problem Solving"],
            "min_experience_years": 5.0,
            "recommended_trainings": [
                "DevOps, Docker & Kubernetes in Production",
                "Agile Leadership & Scrum Master Certification"
            ]
        },
        "Cloud Architect": {
            "department": "Engineering",
            "required_skills": ["AWS", "Docker", "Kubernetes", "Linux", "Microservices", "CI/CD"],
            "optional_skills": ["Python", "Go", "PostgreSQL", "REST APIs"],
            "soft_skills": ["Leadership", "Strategic Thinking", "Communication"],
            "min_experience_years": 7.0,
            "recommended_trainings": [
                "AWS Certified Solutions Architect",
                "DevOps, Docker & Kubernetes in Production"
            ]
        },
        "DevOps Engineer": {
            "department": "Engineering",
            "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"],
            "optional_skills": ["Python", "Go", "Microservices"],
            "soft_skills": ["Problem Solving", "Time Management", "Collaboration"],
            "min_experience_years": 2.5,
            "recommended_trainings": [
                "DevOps, Docker & Kubernetes in Production",
                "AWS Certified Solutions Architect"
            ]
        },
        "Product Manager": {
            "department": "Product",
            "required_skills": ["Product Strategy", "Agile/Scrum", "Roadmapping", "Jira", "A/B Testing"],
            "optional_skills": ["Figma", "SQL", "Data Analysis", "User Research"],
            "soft_skills": ["Leadership", "Communication", "Negotiation", "Problem Solving"],
            "min_experience_years": 3.0,
            "recommended_trainings": [
                "Agile Leadership & Scrum Master Certification",
                "Executive Data Analytics & Storytelling"
            ]
        },
        "HR Business Partner": {
            "department": "Human Resources",
            "required_skills": ["Employee Relations", "Performance Management", "HRIS", "Labor Law", "People Analytics"],
            "optional_skills": ["Talent Acquisition", "Conflict Resolution", "Compensation & Benefits"],
            "soft_skills": ["Communication", "Emotional Intelligence", "Negotiation"],
            "min_experience_years": 4.0,
            "recommended_trainings": [
                "Strategic HR Management Masterclass"
            ]
        },
        "Financial Analyst": {
            "department": "Finance",
            "required_skills": ["Financial Modeling", "Excel", "Budgeting", "Forecasting", "SQL"],
            "optional_skills": ["Power BI", "QuickBooks", "Variance Analysis"],
            "soft_skills": ["Critical Thinking", "Problem Solving", "Time Management"],
            "min_experience_years": 2.0,
            "recommended_trainings": [
                "Financial Modeling & Valuation Analyst (FMVA)"
            ]
        }
    }
    
    with open(ML_DIR / "benchmarks.json", "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2)
        
    print(f"Created {len(benchmarks)} job-role benchmarks at {ML_DIR / 'benchmarks.json'}")
    return benchmarks

def run_all_ml_training():
    print("=" * 60)
    print("STARTING MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 60)
    df = pd.read_csv(CLEANED_CSV)
    train_attrition_model(df)
    train_skill_clustering(df)
    create_role_benchmarks()
    print("\n[SUCCESS] All Machine Learning models and benchmarks ready!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_ml_training()

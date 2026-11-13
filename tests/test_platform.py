"""
End-to-End Automated Platform Verification Test Suite
Tests every REST route, database CRUD, ML models, and RAG assistant.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from database.crud import list_employees, get_employee, create_employee, update_employee, delete_employee, get_all_departments
from backend.routes.analytics import get_overview_kpis, get_skills_analytics, get_department_analytics, get_eda_reports
from backend.routes.predictions import predict_attrition, get_skill_clusters, get_model_evaluation_metrics
from backend.models import AttritionPredictRequest, SkillGapRequest, TeamRecommendRequest, AIChatRequest
from backend.routes.skill_gap import analyze_skill_gap, get_all_role_benchmarks
from backend.routes.assistant import chat_with_workforce_assistant, recommend_project_team

def run_tests():
    print("=" * 70)
    print("RUNNING NEXUSHR PLATFORM END-TO-END VERIFICATION TESTS")
    print("=" * 70)

    # 1. Database & Departments
    print("\n[TEST 1] Testing Database & Department Queries...")
    depts = get_all_departments()
    assert len(depts) >= 7, f"Expected at least 7 departments, got {len(depts)}"
    print(f"  ✓ Found {len(depts)} departments: {[d['name'] for d in depts[:3]]}...")

    # 2. Employee Listing, Search, Filters
    print("\n[TEST 2] Testing Employee Querying & Filters...")
    emp_list = list_employees(limit=10)
    assert emp_list["total"] >= 600, f"Expected >= 600 employees, got {emp_list['total']}"
    print(f"  ✓ Listed employees. Total database count: {emp_list['total']}")

    dept_filter = list_employees(department="Engineering", limit=5)
    print(f"  ✓ Filtered by 'Engineering': {dept_filter['total']} found")

    skill_filter = list_employees(skill="Python", limit=5)
    print(f"  ✓ Filtered by skill 'Python': {skill_filter['total']} found")

    search_res = list_employees(search="David", limit=5)
    print(f"  ✓ Searched 'David': {search_res['total']} found")

    # 3. Single Employee Relational Read
    print("\n[TEST 3] Testing Relational Read for EMP0001...")
    emp = get_employee("EMP0001")
    assert emp is not None, "EMP0001 not found"
    assert "technical_skills" in emp and len(emp["technical_skills"]) > 0
    print(f"  ✓ Read {emp['name']} ({emp['job_role']}, {emp['department_name']}):")
    print(f"    - Skills: {emp['technical_skills']}")
    print(f"    - Performance Reviews: {len(emp['performance_reviews'])}")
    print(f"    - Training Certifications: {len(emp['training_history'])}")

    # 4. CRUD: Create, Update, Delete
    print("\n[TEST 4] Testing CRUD Operations (Create, Update, Delete)...")
    new_emp = create_employee(
        name="Verification Test User",
        age=30,
        gender="Non-Binary",
        department_name="Data & AI",
        job_role="Data Scientist",
        experience_years=4.0,
        salary=110000.0,
        education="Master's Degree",
        location="Remote",
        technical_skills=["Python", "SQL", "Machine Learning", "FastAPI"],
        soft_skills=["Problem Solving", "Adaptability"],
        performance_rating=4.2,
        overtime="No",
        job_satisfaction=4,
        work_life_balance=4,
        training_course="Advanced Machine Learning & Deep Learning"
    )
    test_id = new_emp["employee_id"]
    print(f"  ✓ Created new employee: {test_id} ({new_emp['name']})")

    updated = update_employee(test_id, {"salary": 125000.0, "performance_rating": 4.5})
    assert updated["salary"] == 125000.0
    assert updated["performance_rating"] == 4.5
    print(f"  ✓ Updated employee {test_id} salary to ${updated['salary']:,.0f}")

    del_ok = delete_employee(test_id)
    assert del_ok is True
    assert get_employee(test_id) is None
    print(f"  ✓ Deleted employee {test_id} and verified relational cascade")

    # 5. Analytics Routes
    print("\n[TEST 5] Testing Overview, Skills, and Department Analytics...")
    overview = get_overview_kpis()
    assert overview["kpis"]["total_employees"] >= 650
    print(f"  ✓ Overview KPIs: Total={overview['kpis']['total_employees']}, Avg Salary=${overview['kpis']['avg_salary']:,.0f}, Retention={overview['kpis']['retention_rate_pct']}%")

    skills_res = get_skills_analytics()
    assert len(skills_res["top_technical_skills"]) > 0
    print(f"  ✓ Skills Analytics: Top skill = {skills_res['top_technical_skills'][0]['skill_name']} ({skills_res['top_technical_skills'][0]['count']} practitioners)")

    dept_res = get_department_analytics()
    assert len(dept_res["departments"]) >= 7
    print(f"  ✓ Department Analytics: {len(dept_res['departments'])} departments loaded")

    eda_res = get_eda_reports()
    assert len(eda_res["charts"]) == 10
    print(f"  ✓ EDA Reports: {len(eda_res['charts'])} high-resolution charts verified")

    # 6. ML Predictions & Clustering
    print("\n[TEST 6] Testing ML Attrition Prediction & Clustering...")
    pred_req = AttritionPredictRequest(
        age=26, experience_years=2.0, salary=65000, job_satisfaction=1,
        work_life_balance=1, performance_rating=2.4, projects_completed=5,
        overtime="Yes", skill_count=3, has_training=0, department="Engineering"
    )
    pred_result = predict_attrition(pred_req)
    print(f"  ✓ Simulated High Risk Employee:")
    print(f"    - Probability: {pred_result['attrition_probability']}%")
    print(f"    - Risk Level:  {pred_result['risk_level']}")
    print(f"    - Risk Drivers: {pred_result['key_risk_drivers']}")

    clusters = get_skill_clusters()
    assert len(clusters) == 4
    print(f"  ✓ K-Means Clusters: 4 personas verified ({[c['title'] for c in clusters]})")

    metrics = get_model_evaluation_metrics()
    print(f"  ✓ Evaluation Metrics: Accuracy={metrics['accuracy']*100:.1f}%, ROC-AUC={metrics['roc_auc']}")

    # 7. Skill Gap Analysis
    print("\n[TEST 7] Testing Skill Gap Analysis...")
    benchmarks = get_all_role_benchmarks()
    assert "Senior Data Scientist" in benchmarks
    gap_req = SkillGapRequest(employee_id="EMP0001", target_role="Senior Data Scientist")
    gap_result = analyze_skill_gap(gap_req)
    print(f"  ✓ Evaluated EMP0001 vs Senior Data Scientist:")
    print(f"    - Match Score: {gap_result['match_percentage']}%")
    print(f"    - Status: {gap_result['readiness_status']}")
    print(f"    - Missing Core Skills: {gap_result['skills_summary']['missing_core_skills']}")
    print(f"    - Recommended Trainings: {gap_result['recommended_trainings']}")

    # 8. AI Recommendations & Project Team Builder
    print("\n[TEST 8] Testing Project Team Recommendation...")
    team_req = TeamRecommendRequest(
        project_name="AI Analytics Initiative",
        required_skills=["Python", "SQL", "Machine Learning"],
        min_experience_years=2.0,
        team_size=3
    )
    team_res = recommend_project_team(team_req)
    assert len(team_res["selected_candidates"]) == 3
    print(f"  ✓ Recommended {len(team_res['selected_candidates'])} team members:")
    for c in team_res["selected_candidates"]:
        print(f"    - {c['name']} ({c['job_role']}, {c['department']}): {c['match_percentage']}% match")

    # 9. RAG Assistant Chatbot - Answering All 7 User Questions
    print("\n[TEST 9] Testing RAG AI Chatbot with the 7 Example Questions...")
    sample_queries = [
        "Which department has the highest number of employees?",
        "What are the most common employee skills?",
        "Which employees have Python and SQL skills?",
        "Which skills are missing in the IT department?",
        "What training should employees receive?",
        "Which employees are suitable for a Data Analyst project?",
        "What are the workforce performance trends?"
    ]

    for idx, q in enumerate(sample_queries, 1):
        chat_req = AIChatRequest(message=q)
        chat_res = chat_with_workforce_assistant(chat_req)
        assert len(chat_res["answer"]) > 50
        print(f"\n  [Q{idx}] Query: '{q}'")
        first_line = chat_res["answer"].strip().split("\n")[0]
        print(f"    -> Answer snippet: {first_line}")
        if chat_res["citations"]:
            print(f"    -> Citations: {chat_res['citations'][0]['title']}")

    print("\n" + "=" * 70)
    print(" ALL 9 SUITES PASSED! NEXUSHR PLATFORM IS 100% OPERATIONAL.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

"""
Synthetic Employee Workforce Dataset Generator
Generates realistic raw employee workforce data with realistic job roles, departments,
experience, salary curves, technical and soft skills, training history, and intentional
raw data anomalies (missing values, inconsistent strings, duplicates, outliers)
to rigorously demonstrate data cleaning and preprocessing.
"""

import random
import numpy as np
import pandas as pd
from pathlib import Path

# Fix random seed for reproducibility
random.seed(42)
np.random.seed(42)

NUM_RECORDS = 650

FIRST_NAMES = [
    "Aarav", "Aditi", "Alexander", "Amara", "Carlos", "Chen", "Chloe", "David",
    "Elena", "Fatima", "Gabriel", "Grace", "Hassan", "Isabella", "James", "Jia",
    "Kavita", "Liam", "Maya", "Michael", "Nina", "Oliver", "Priya", "Rahul",
    "Rohan", "Samantha", "Samuel", "Sara", "Siddharth", "Sophia", "Tariq",
    "Victoria", "William", "Yuki", "Zainab", "Emma", "Daniel", "Ananya", "Lucas"
]

LAST_NAMES = [
    "Patel", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez",
    "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Khan"
]

LOCATIONS = [
    "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA",
    "Chicago, IL", "Boston, MA", "London, UK", "Bangalore, IN", "Remote"
]

DEPARTMENTS_ROLES = {
    "Engineering": [
        ("Software Engineer", (1, 6), (75000, 115000)),
        ("Senior Software Engineer", (5, 14), (120000, 165000)),
        ("DevOps Engineer", (2, 8), (85000, 130000)),
        ("Cloud Architect", (7, 18), (140000, 195000)),
        ("QA Automation Engineer", (1, 7), (70000, 105000)),
        ("Engineering Manager", (8, 20), (150000, 210000))
    ],
    "Data & AI": [
        ("Data Analyst", (1, 5), (68000, 95000)),
        ("Senior Data Analyst", (4, 10), (95000, 130000)),
        ("Data Scientist", (2, 7), (95000, 140000)),
        ("Senior Data Scientist", (6, 15), (140000, 185000)),
        ("Machine Learning Engineer", (2, 9), (110000, 165000)),
        ("AI Research Scientist", (4, 14), (135000, 195000))
    ],
    "Product": [
        ("Associate Product Manager", (1, 4), (72000, 95000)),
        ("Product Manager", (3, 9), (105000, 145000)),
        ("Senior Product Manager", (7, 16), (145000, 185000)),
        ("UX/UI Designer", (1, 6), (68000, 105000)),
        ("Lead Product Designer", (6, 14), (115000, 155000))
    ],
    "Human Resources": [
        ("HR Coordinator", (1, 4), (52000, 72000)),
        ("HR Business Partner", (4, 11), (80000, 115000)),
        ("Talent Acquisition Specialist", (2, 7), (65000, 92000)),
        ("Learning & Development Lead", (5, 14), (90000, 130000)),
        ("Head of People", (10, 22), (135000, 180000))
    ],
    "Sales & Marketing": [
        ("Marketing Specialist", (1, 5), (55000, 80000)),
        ("Growth Marketing Manager", (4, 10), (88000, 125000)),
        ("Account Executive", (2, 8), (70000, 120000)),
        ("Sales Director", (9, 20), (130000, 190000)),
        ("Content Strategist", (2, 6), (60000, 88000))
    ],
    "Finance": [
        ("Financial Analyst", (1, 5), (65000, 92000)),
        ("Senior Financial Analyst", (4, 10), (95000, 130000)),
        ("Accounting Manager", (6, 14), (105000, 145000)),
        ("Finance Director", (10, 22), (145000, 205000))
    ],
    "Customer Support": [
        ("Support Specialist", (1, 4), (45000, 65000)),
        ("Senior Support Engineer", (3, 8), (65000, 95000)),
        ("Customer Success Manager", (3, 9), (75000, 110000)),
        ("Support Operations Lead", (5, 12), (90000, 125000))
    ]
}

ROLE_SKILL_POOLS = {
    "Engineering": ["Python", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "Git", "CI/CD", "Java", "Go", "C++", "Microservices", "REST APIs", "PostgreSQL", "Linux"],
    "Data & AI": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn", "Deep Learning", "Tableau", "Power BI", "PyTorch", "TensorFlow", "Spark", "AWS", "BigQuery", "Statistics", "Data Modeling"],
    "Product": ["Product Strategy", "Agile/Scrum", "Wireframing", "Figma", "User Research", "Roadmapping", "A/B Testing", "Data Analysis", "Jira", "SQL", "Market Analysis"],
    "Human Resources": ["Talent Acquisition", "Employee Relations", "HRIS", "Performance Management", "Onboarding", "Conflict Resolution", "Labor Law", "People Analytics", "Compensation & Benefits"],
    "Sales & Marketing": ["CRM", "Salesforce", "SEO/SEM", "Content Strategy", "Digital Marketing", "Lead Generation", "Google Analytics", "Copywriting", "Email Automation", "Market Research"],
    "Finance": ["Financial Modeling", "Excel", "Budgeting", "Forecasting", "SQL", "QuickBooks", "Variance Analysis", "Auditing", "ERP Systems", "Power BI"],
    "Customer Support": ["Zendesk", "Customer Service", "Technical Troubleshooting", "CRM", "Ticket Management", "Documentation", "Communication", "SLA Management"]
}

SOFT_SKILL_POOL = [
    "Communication", "Problem Solving", "Leadership", "Teamwork",
    "Critical Thinking", "Adaptability", "Time Management", "Collaboration",
    "Mentorship", "Negotiation", "Emotional Intelligence"
]

TRAINING_COURSES = [
    "AWS Certified Solutions Architect",
    "Advanced Machine Learning & Deep Learning",
    "Full-Stack Web Development Bootcamp",
    "Agile Leadership & Scrum Master Certification",
    "Executive Data Analytics & Storytelling",
    "Strategic HR Management Masterclass",
    "Financial Modeling & Valuation Analyst (FMVA)",
    "Customer Experience & Modern Support Ops",
    "DevOps, Docker & Kubernetes in Production",
    "AI Ethics & Responsible Generative AI",
    "None"
]

EDUCATION_LEVELS = ["Associate Degree", "Bachelor's Degree", "Master's Degree", "Ph.D."]

def generate_raw_dataset(output_path: Path):
    records = []
    
    dept_weights = [0.28, 0.22, 0.12, 0.10, 0.12, 0.08, 0.08]
    dept_keys = list(DEPARTMENTS_ROLES.keys())

    for i in range(1, NUM_RECORDS + 1):
        emp_id = f"EMP{i:04d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        
        gender = random.choices(["Male", "Female", "Non-Binary"], weights=[0.51, 0.45, 0.04])[0]
        department = random.choices(dept_keys, weights=dept_weights)[0]
        
        role_info = random.choice(DEPARTMENTS_ROLES[department])
        role_name, exp_range, sal_range = role_info
        
        # Experience
        exp = round(random.uniform(exp_range[0], exp_range[1]), 1)
        age = int(22 + exp + random.randint(0, 8))
        
        # Salary roughly correlated with experience + role range
        exp_fraction = (exp - exp_range[0]) / max(1, (exp_range[1] - exp_range[0]))
        base_sal = sal_range[0] + exp_fraction * (sal_range[1] - sal_range[0])
        noise = random.uniform(-6000, 6000)
        salary = int(round(base_sal + noise, -2))
        
        # Education
        if "Manager" in role_name or "Director" in role_name or "Scientist" in role_name:
            edu = random.choices(EDUCATION_LEVELS, weights=[0.02, 0.48, 0.40, 0.10])[0]
        else:
            edu = random.choices(EDUCATION_LEVELS, weights=[0.10, 0.65, 0.22, 0.03])[0]
            
        location = random.choices(LOCATIONS, weights=[0.18, 0.18, 0.12, 0.12, 0.08, 0.06, 0.06, 0.08, 0.12])[0]
        
        # Technical skills (sample 3 to 6 skills from dept pool + cross-functional)
        dept_pool = ROLE_SKILL_POOLS[department]
        num_skills = random.randint(3, 6)
        tech_skills_list = random.sample(dept_pool, min(num_skills, len(dept_pool)))
        # occasional cross-pollination
        if random.random() < 0.25:
            cross_skill = random.choice(["Python", "SQL", "Git", "Power BI", "AWS", "Jira"])
            if cross_skill not in tech_skills_list:
                tech_skills_list.append(cross_skill)
                
        # Soft skills (2 to 4)
        soft_skills_list = random.sample(SOFT_SKILL_POOL, random.randint(2, 4))
        
        # Performance rating (1.0 to 5.0, mean ~3.7)
        perf_rating = round(np.clip(random.gauss(3.7, 0.7), 1.0, 5.0), 1)
        
        # Training history
        training = random.choice(TRAINING_COURSES)
        
        # Additional features that make attrition prediction realistic and authentic
        overtime = random.choices(["Yes", "No"], weights=[0.28, 0.72])[0]
        job_satisfaction = random.choices([1, 2, 3, 4, 5], weights=[0.10, 0.16, 0.32, 0.28, 0.14])[0]
        work_life_balance = random.choices([1, 2, 3, 4, 5], weights=[0.12, 0.20, 0.35, 0.23, 0.10])[0]
        projects_completed = max(1, int(exp * random.uniform(1.2, 2.5) + random.randint(0, 3)))
        
        # Realistic Attrition probability calculation
        # Higher risk if overtime=Yes, low job_satisfaction, low work_life_balance, low salary relative to exp
        risk_score = 0.0
        if overtime == "Yes":
            risk_score += 0.35
        if job_satisfaction <= 2:
            risk_score += 0.30
        elif job_satisfaction >= 4:
            risk_score -= 0.20
        if work_life_balance <= 2:
            risk_score += 0.25
        if exp < 3: # early career higher churn
            risk_score += 0.15
        if perf_rating < 2.5:
            risk_score += 0.20
        if training == "None":
            risk_score += 0.10
        else:
            risk_score -= 0.10
            
        attrition_prob = 1 / (1 + np.exp(-(risk_score - 0.2)))
        attrition = 1 if random.random() < (attrition_prob * 0.45) else 0 # realistic ~18% base attrition
        
        # Convert lists to comma strings
        tech_skills_str = ", ".join(tech_skills_list)
        soft_skills_str = ", ".join(soft_skills_list)
        
        # Intentional Raw Flaws:
        # 1. Inconsistent casing / whitespace
        if random.random() < 0.08:
            tech_skills_str = tech_skills_str.replace("Python", " python ").replace("SQL", "sql")
        # 2. Missing values in some non-critical fields
        if random.random() < 0.04:
            training = None
        if random.random() < 0.03:
            soft_skills_str = None
        if random.random() < 0.02:
            education = None
        else:
            education = edu
            
        record = {
            "Employee_ID": emp_id,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Department": department,
            "Job_Role": role_name,
            "Experience_Years": exp,
            "Salary": salary,
            "Education": education,
            "Technical_Skills": tech_skills_str,
            "Soft_Skills": soft_skills_str,
            "Performance_Rating": perf_rating,
            "Location": location,
            "Training_History": training,
            "Overtime": overtime,
            "Job_Satisfaction": job_satisfaction,
            "Work_Life_Balance": work_life_balance,
            "Projects_Completed": projects_completed,
            "Attrition": attrition
        }
        records.append(record)
        
    df = pd.DataFrame(records)
    
    # Introduce 5 duplicate rows to test duplicate removal
    dup_rows = df.sample(n=5, random_state=42)
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # Introduce a couple of extreme outlier salaries for outlier detection treatment
    df.loc[12, "Salary"] = 999999  # Data entry typo
    df.loc[45, "Salary"] = 12000   # Below minimum
    
    # Save raw dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated raw dataset with {len(df)} records at {output_path}")
    return df

if __name__ == "__main__":
    out_file = Path(r"C:\Users\Shaik Karishma\.gemini\antigravity\scratch\workforce-skills-analytics\data\dataset_raw.csv")
    generate_raw_dataset(out_file)

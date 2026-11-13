"""
Workforce Data Cleaning and Preprocessing Pipeline
Performs rigorous end-to-end data sanitization:
1. Missing value detection and intelligent imputation
2. Duplicate row detection and elimination
3. Data type conversions
4. Inconsistent text & skill token standardization
5. Outlier detection using the IQR method and median adjustment
6. Feature engineering (Skill_Count, Salary_Per_Exp, Tenure_Tier, Performance_Tier, Has_Training)
7. Categorical encoding
8. Exporting cleaned dataset and diagnostic report
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV_DEFAULT = BASE_DIR / "dataset" / "dataset_raw.csv"
CLEANED_CSV_DEFAULT = BASE_DIR / "dataset" / "dataset_cleaned.csv"
REPORT_JSON_DEFAULT = BASE_DIR / "dataset" / "cleaning_report.json"

def clean_and_preprocess_workforce_data(raw_csv_path: Path = RAW_CSV_DEFAULT, cleaned_csv_path: Path = CLEANED_CSV_DEFAULT, report_path: Path = REPORT_JSON_DEFAULT):
    print("=" * 60)
    print("STARTING WORKFORCE DATA CLEANING & PREPROCESSING PIPELINE")
    print("=" * 60)

    df = pd.read_csv(raw_csv_path)
    initial_rows = len(df)
    print(f"Loaded raw dataset with {initial_rows} records and {len(df.columns)} columns.")

    cleaning_report = {
        "initial_record_count": initial_rows,
        "initial_missing_values": df.isnull().sum().to_dict(),
        "duplicates_removed": 0,
        "outliers_treated": [],
        "imputations": {},
        "engineered_features": []
    }

    # Duplicate Removal
    dup_mask = df.duplicated(subset=["Employee_ID"], keep="first")
    num_dups = int(dup_mask.sum())
    df = df[~dup_mask].copy()
    cleaning_report["duplicates_removed"] = num_dups
    print(f"[1/7] Removed {num_dups} duplicate records. Current rows: {len(df)}")

    # String Standardization
    for str_col in ["Employee_ID", "Name", "Department", "Job_Role", "Location", "Overtime"]:
        if str_col in df.columns:
            df[str_col] = df[str_col].astype(str).str.strip()

    def standardize_skills(skills_str):
        if pd.isna(skills_str) or not str(skills_str).strip():
            return "General IT"
        tokens = [s.strip() for s in str(skills_str).split(",") if s.strip()]
        normalized = []
        for t in tokens:
            tl = t.lower()
            if tl == "python":
                normalized.append("Python")
            elif tl == "sql":
                normalized.append("SQL")
            elif tl == "aws":
                normalized.append("AWS")
            elif tl in ["react", "react.js"]:
                normalized.append("React")
            elif tl in ["node", "node.js"]:
                normalized.append("Node.js")
            elif tl in ["ci/cd", "cicd"]:
                normalized.append("CI/CD")
            else:
                normalized.append(t.title() if len(t) > 3 else t.upper())
        seen = set()
        clean_tokens = [x for x in normalized if not (x in seen or seen.add(x))]
        return ", ".join(clean_tokens)

    df["Technical_Skills"] = df["Technical_Skills"].apply(standardize_skills)

    def standardize_soft_skills(skills_str):
        if pd.isna(skills_str) or not str(skills_str).strip():
            return "Communication, Problem Solving"
        tokens = [s.strip().title() for s in str(skills_str).split(",") if s.strip()]
        seen = set()
        clean_tokens = [x for x in tokens if not (x in seen or seen.add(x))]
        return ", ".join(clean_tokens)

    df["Soft_Skills"] = df["Soft_Skills"].apply(standardize_soft_skills)
    print("[2/7] Standardized strings and cleaned technical & soft skill tokens.")

    # Imputation
    edu_mode_per_dept = df.groupby("Department")["Education"].apply(lambda s: s.mode().iloc[0] if not s.mode().empty else "Bachelor's Degree").to_dict()
    null_edu_count = int(df["Education"].isnull().sum())
    for dept, mode_val in edu_mode_per_dept.items():
        mask = (df["Department"] == dept) & (df["Education"].isnull())
        df.loc[mask, "Education"] = mode_val
    df["Education"] = df["Education"].fillna("Bachelor's Degree")
    cleaning_report["imputations"]["Education_imputed"] = null_edu_count

    null_training = int(df["Training_History"].isnull().sum())
    df["Training_History"] = df["Training_History"].fillna("None")
    cleaning_report["imputations"]["Training_History_imputed"] = null_training
    print(f"[3/7] Imputed missing values ({null_edu_count} Education, {null_training} Training_History).")

    # Outliers
    Q1 = df["Salary"].quantile(0.25)
    Q3 = df["Salary"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df["Salary"] < lower_bound) | (df["Salary"] > upper_bound)]
    print(f"[4/7] Detected {len(outliers)} salary outliers using IQR (Bounds: ${lower_bound:,.0f} - ${upper_bound:,.0f}).")
    
    role_salary_median = df.groupby("Job_Role")["Salary"].median().to_dict()
    for idx, row in outliers.iterrows():
        old_sal = row["Salary"]
        new_sal = role_salary_median.get(row["Job_Role"], df["Salary"].median())
        df.loc[idx, "Salary"] = round(new_sal, -2)
        cleaning_report["outliers_treated"].append({
            "Employee_ID": row["Employee_ID"],
            "Role": row["Job_Role"],
            "Old_Salary": float(old_sal),
            "Cleaned_Salary": float(round(new_sal, -2))
        })

    # Types
    df["Age"] = df["Age"].astype(int)
    df["Experience_Years"] = df["Experience_Years"].astype(float).round(1)
    df["Salary"] = df["Salary"].astype(float).round(2)
    df["Performance_Rating"] = df["Performance_Rating"].astype(float).round(1)
    df["Job_Satisfaction"] = df["Job_Satisfaction"].astype(int)
    df["Work_Life_Balance"] = df["Work_Life_Balance"].astype(int)
    df["Projects_Completed"] = df["Projects_Completed"].astype(int)
    df["Attrition"] = df["Attrition"].astype(int)
    print("[5/7] Converted column data types to optimal schemas.")

    # Feature Engineering
    df["Skill_Count"] = df["Technical_Skills"].apply(lambda s: len([x for x in str(s).split(",") if x.strip()]))
    df["Salary_Per_Exp"] = (df["Salary"] / df["Experience_Years"].apply(lambda e: max(1.0, e))).round(2)
    
    def get_tenure_tier(exp):
        if exp < 2.0:
            return "Entry Level (0-2y)"
        elif exp < 5.0:
            return "Mid Level (3-5y)"
        elif exp < 10.0:
            return "Senior (6-10y)"
        elif exp < 15.0:
            return "Staff/Lead (11-15y)"
        else:
            return "Principal/Exec (16y+)"
            
    df["Tenure_Tier"] = df["Experience_Years"].apply(get_tenure_tier)
    
    def get_perf_tier(score):
        if score < 2.8:
            return "Needs Improvement"
        elif score < 3.8:
            return "Meets Expectations"
        elif score < 4.6:
            return "High Performer"
        else:
            return "Top Performer"
            
    df["Performance_Tier"] = df["Performance_Rating"].apply(get_perf_tier)
    df["Has_Training"] = df["Training_History"].apply(lambda t: 0 if t.strip().lower() in ["none", "not enrolled"] else 1)

    cleaning_report["engineered_features"] = [
        "Skill_Count", "Salary_Per_Exp", "Tenure_Tier", "Performance_Tier", "Has_Training"
    ]
    print("[6/7] Successfully engineered 5 domain-specific analytics features.")

    # Encodings
    df["Overtime_Code"] = df["Overtime"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    gender_map = {"Male": 0, "Female": 1, "Non-Binary": 2}
    df["Gender_Code"] = df["Gender"].map(gender_map).fillna(0).astype(int)
    dept_map = {name: idx for idx, name in enumerate(sorted(df["Department"].unique()))}
    df["Department_Code"] = df["Department"].map(dept_map).astype(int)

    cleaning_report["final_record_count"] = len(df)
    cleaning_report["final_missing_values"] = df.isnull().sum().to_dict()
    
    cleaned_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cleaned_csv_path, index=False)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(cleaning_report, f, indent=2)

    print(f"[7/7] Cleaned dataset saved to: {cleaned_csv_path}")
    print(f"Cleaning audit report saved to: {report_path}")
    print("=" * 60)
    return df

if __name__ == "__main__":
    clean_and_preprocess_workforce_data()

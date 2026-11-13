"""
Exploratory Data Analysis (EDA) Module
Uses Pandas, NumPy, Matplotlib, and Seaborn to generate 10 comprehensive
visualizations and structured analytical insights for workforce intelligence.
"""

import os
import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd

os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp()
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_CSV = BASE_DIR / "dataset" / "dataset_cleaned.csv"
CHARTS_DIR = BASE_DIR / "eda" / "charts"
INSIGHTS_JSON = BASE_DIR / "eda" / "eda_insights.json"
REPORT_MD = BASE_DIR / "eda" / "eda_report.md"

sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "figure.autolayout": True,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "semibold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 200
})

PALETTE_PRIMARY = "#2563eb"
PALETTE_ACCENT = "#0d9488"
PALETTE_WARM = "#f59e0b"
PALETTE_ROSE = "#e11d48"

def run_eda():
    print("=" * 60)
    print("STARTING WORKFORCE EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)
    
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CLEANED_CSV)
    insights = {}

    # 1. Department Distribution
    print("[1/10] Generating Department Distribution Chart...")
    plt.figure(figsize=(10, 5))
    dept_counts = df["Department"].value_counts()
    ax = sns.barplot(x=dept_counts.values, y=dept_counts.index, hue=dept_counts.index, palette="Blues_r", legend=False)
    plt.title("Workforce Headcount Distribution by Department")
    plt.xlabel("Number of Employees")
    plt.ylabel("Department")
    for i, v in enumerate(dept_counts.values):
        ax.text(v + 2, i, f"{v} ({v/len(df)*100:.1f}%)", va="center", fontweight="bold", color="#1e293b")
    plt.tight_layout()
    chart1_path = CHARTS_DIR / "1_department_distribution.png"
    plt.savefig(chart1_path)
    plt.close()
    
    insights["department_distribution"] = {
        "largest_department": dept_counts.index[0],
        "largest_count": int(dept_counts.iloc[0]),
        "largest_pct": round(dept_counts.iloc[0] / len(df) * 100, 1),
        "smallest_department": dept_counts.index[-1],
        "smallest_count": int(dept_counts.iloc[-1]),
        "total_departments": len(dept_counts),
        "key_insight": f"{dept_counts.index[0]} and {dept_counts.index[1]} constitute {round((dept_counts.iloc[0]+dept_counts.iloc[1])/len(df)*100, 1)}% of total enterprise headcount."
    }

    # 2. Gender Distribution
    print("[2/10] Generating Gender Distribution Chart...")
    plt.figure(figsize=(7, 7))
    gender_counts = df["Gender"].value_counts()
    colors = ["#3b82f6", "#ec4899", "#8b5cf6"]
    plt.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=140,
            colors=colors[:len(gender_counts)], wedgeprops=dict(width=0.4, edgecolor='w'))
    plt.title("Workforce Gender Diversity Breakdown")
    plt.tight_layout()
    chart2_path = CHARTS_DIR / "2_gender_distribution.png"
    plt.savefig(chart2_path)
    plt.close()

    insights["gender_distribution"] = {
        "breakdown": {k: int(v) for k, v in gender_counts.items()},
        "female_percentage": round(gender_counts.get("Female", 0) / len(df) * 100, 1),
        "male_percentage": round(gender_counts.get("Male", 0) / len(df) * 100, 1),
        "non_binary_percentage": round(gender_counts.get("Non-Binary", 0) / len(df) * 100, 1),
        "key_insight": f"Female representation stands at {round(gender_counts.get('Female', 0) / len(df) * 100, 1)}%, demonstrating strong gender diversity balance across technical and business functions."
    }

    # 3. Experience Analysis
    print("[3/10] Generating Experience Distribution Chart...")
    plt.figure(figsize=(10, 5))
    sns.histplot(df["Experience_Years"], kde=True, color=PALETTE_PRIMARY, bins=20)
    plt.axvline(df["Experience_Years"].mean(), color=PALETTE_ROSE, linestyle="--", linewidth=2, label=f"Mean: {df['Experience_Years'].mean():.1f} yrs")
    plt.axvline(df["Experience_Years"].median(), color=PALETTE_WARM, linestyle="-.", linewidth=2, label=f"Median: {df['Experience_Years'].median():.1f} yrs")
    plt.title("Distribution of Professional Experience (Years)")
    plt.xlabel("Years of Industry Experience")
    plt.ylabel("Employee Count")
    plt.legend()
    plt.tight_layout()
    chart3_path = CHARTS_DIR / "3_experience_distribution.png"
    plt.savefig(chart3_path)
    plt.close()

    insights["experience_analysis"] = {
        "mean_experience": round(float(df["Experience_Years"].mean()), 1),
        "median_experience": round(float(df["Experience_Years"].median()), 1),
        "min_experience": round(float(df["Experience_Years"].min()), 1),
        "max_experience": round(float(df["Experience_Years"].max()), 1),
        "key_insight": f"The workforce has an average experience of {df['Experience_Years'].mean():.1f} years, with a healthy distribution from entry-level apprentices to veteran technical leads."
    }

    # 4. Salary Distribution by Department
    print("[4/10] Generating Salary Distribution Chart...")
    plt.figure(figsize=(12, 6))
    order = df.groupby("Department")["Salary"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="Department", y="Salary", order=order, hue="Department", palette="Spectral", legend=False)
    plt.title("Salary Distribution Across Departments (USD)")
    plt.ylabel("Annual Salary ($)")
    plt.xlabel("Department")
    plt.xticks(rotation=20, ha="right")
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${int(x):,}"))
    plt.tight_layout()
    chart4_path = CHARTS_DIR / "4_salary_distribution.png"
    plt.savefig(chart4_path)
    plt.close()

    dept_sal = df.groupby("Department")["Salary"].agg(["median", "mean"]).to_dict()
    insights["salary_analysis"] = {
        "highest_paying_dept": order[0],
        "highest_paying_median": float(round(dept_sal["median"][order[0]], 0)),
        "overall_median_salary": float(round(df["Salary"].median(), 0)),
        "overall_mean_salary": float(round(df["Salary"].mean(), 0)),
        "key_insight": f"{order[0]} commands the highest median compensation (${dept_sal['median'][order[0]]:,.0f}), reflecting high market premiums for deep engineering and AI specialization."
    }

    # 5. Technical Skills
    print("[5/10] Generating Technical Skills Chart...")
    all_skills = []
    for s_str in df["Technical_Skills"]:
        for s in str(s_str).split(","):
            s_clean = s.strip()
            if s_clean:
                all_skills.append(s_clean)
    skill_series = pd.Series(all_skills).value_counts().head(12)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=skill_series.values, y=skill_series.index, hue=skill_series.index, palette="viridis", legend=False)
    plt.title("Top 12 In-Demand Technical Skills Across Organization")
    plt.xlabel("Number of Skilled Employees")
    plt.ylabel("Technical Competency")
    for i, v in enumerate(skill_series.values):
        plt.text(v + 1, i, str(v), va="center", fontweight="bold")
    plt.tight_layout()
    chart5_path = CHARTS_DIR / "5_top_technical_skills.png"
    plt.savefig(chart5_path)
    plt.close()

    insights["top_technical_skills"] = {
        "top_skill": skill_series.index[0],
        "top_skill_count": int(skill_series.iloc[0]),
        "top_skills_ranked": skill_series.to_dict(),
        "key_insight": f"{skill_series.index[0]} ({skill_series.iloc[0]} practitioners) and {skill_series.index[1]} ({skill_series.iloc[1]} practitioners) form the organizational foundational technology stack."
    }

    # 6. Department Performance
    print("[6/10] Generating Department Performance Chart...")
    plt.figure(figsize=(10, 5))
    dept_perf = df.groupby("Department")["Performance_Rating"].mean().sort_values(ascending=False)
    ax = sns.barplot(x=dept_perf.index, y=dept_perf.values, hue=dept_perf.index, palette="mako", legend=False)
    plt.title("Average Performance Rating by Department (1.0 - 5.0)")
    plt.ylabel("Mean Performance Rating")
    plt.xlabel("Department")
    plt.ylim(0, 5.0)
    plt.xticks(rotation=20, ha="right")
    for i, v in enumerate(dept_perf.values):
        ax.text(i, v + 0.1, f"{v:.2f}", ha="center", fontweight="bold")
    plt.tight_layout()
    chart6_path = CHARTS_DIR / "6_dept_performance.png"
    plt.savefig(chart6_path)
    plt.close()

    insights["department_performance"] = {
        "highest_performing_dept": dept_perf.index[0],
        "highest_avg_rating": round(float(dept_perf.iloc[0]), 2),
        "overall_avg_rating": round(float(df["Performance_Rating"].mean()), 2),
        "key_insight": f"{dept_perf.index[0]} leads company performance with an average appraisal score of {dept_perf.iloc[0]:.2f} / 5.0."
    }

    # 7. Employee Skill Gaps
    print("[7/10] Generating Skill Gap Density Chart...")
    plt.figure(figsize=(10, 5))
    dept_skill_count = df.groupby("Department")["Skill_Count"].mean().sort_values(ascending=False)
    ax = sns.barplot(x=dept_skill_count.index, y=dept_skill_count.values, hue=dept_skill_count.index, palette="coolwarm", legend=False)
    plt.title("Average Number of Verified Technical Skills per Employee by Department")
    plt.ylabel("Average Skill Count")
    plt.xlabel("Department")
    plt.xticks(rotation=20, ha="right")
    for i, v in enumerate(dept_skill_count.values):
        ax.text(i, v + 0.1, f"{v:.1f}", ha="center", fontweight="bold")
    plt.tight_layout()
    chart7_path = CHARTS_DIR / "7_skill_gaps_dept.png"
    plt.savefig(chart7_path)
    plt.close()

    insights["skill_gap_analysis"] = {
        "highest_skill_density": dept_skill_count.index[0],
        "highest_avg_skills": round(float(dept_skill_count.iloc[0]), 1),
        "lowest_skill_density": dept_skill_count.index[-1],
        "lowest_avg_skills": round(float(dept_skill_count.iloc[-1]), 1),
        "key_insight": f"{dept_skill_count.index[-1]} displays lower average technical skill inventory ({dept_skill_count.iloc[-1]:.1f} skills/person), highlighting prime candidates for targeted cross-functional upskilling."
    }

    # 8. Experience vs Performance
    print("[8/10] Generating Experience vs Performance Chart...")
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x="Experience_Years", y="Performance_Rating",
                scatter_kws={"alpha": 0.5, "color": PALETTE_PRIMARY},
                line_kws={"color": PALETTE_ROSE, "linewidth": 2})
    plt.title("Correlation Analysis: Experience Years vs Performance Rating")
    plt.xlabel("Experience (Years)")
    plt.ylabel("Performance Rating (1.0 - 5.0)")
    plt.tight_layout()
    chart8_path = CHARTS_DIR / "8_exp_vs_performance.png"
    plt.savefig(chart8_path)
    plt.close()

    corr_exp_perf = float(df["Experience_Years"].corr(df["Performance_Rating"]))
    insights["exp_vs_perf"] = {
        "correlation_coefficient": round(corr_exp_perf, 3),
        "key_insight": f"Correlation between experience and performance rating is {corr_exp_perf:.2f}, demonstrating that high performance occurs across both newer agile talent and tenured leaders."
    }

    # 9. Training and Performance
    print("[9/10] Generating Training Impact on Performance Chart...")
    plt.figure(figsize=(9, 5))
    df_trained_label = df.copy()
    df_trained_label["Training_Status"] = df_trained_label["Has_Training"].map({1: "Completed Training / Cert", 0: "No Recent Training"})
    sns.boxplot(data=df_trained_label, x="Training_Status", y="Performance_Rating", hue="Training_Status", palette=["#10b981", "#94a3b8"], legend=False)
    plt.title("Impact of Professional Training on Performance Appraisal Ratings")
    plt.xlabel("Training Participation")
    plt.ylabel("Performance Rating")
    plt.tight_layout()
    chart9_path = CHARTS_DIR / "9_training_vs_performance.png"
    plt.savefig(chart9_path)
    plt.close()

    perf_by_training = df_trained_label.groupby("Training_Status")["Performance_Rating"].mean().to_dict()
    diff = perf_by_training.get("Completed Training / Cert", 0) - perf_by_training.get("No Recent Training", 0)
    insights["training_impact"] = {
        "trained_avg_performance": round(float(perf_by_training.get("Completed Training / Cert", 0)), 2),
        "untrained_avg_performance": round(float(perf_by_training.get("No Recent Training", 0)), 2),
        "performance_lift": round(float(diff), 2),
        "key_insight": f"Employees who completed corporate certifications achieve a +{diff:.2f} higher average performance appraisal score compared to untrained peers."
    }

    # 10. Correlation Analysis Heatmap
    print("[10/10] Generating Correlation Heatmap...")
    numeric_cols = [
        "Age", "Experience_Years", "Salary", "Performance_Rating",
        "Job_Satisfaction", "Work_Life_Balance", "Projects_Completed", "Attrition"
    ]
    corr_matrix = df[numeric_cols].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5)
    plt.title("Workforce Metrics Correlation Heatmap")
    plt.tight_layout()
    chart10_path = CHARTS_DIR / "10_correlation_heatmap.png"
    plt.savefig(chart10_path)
    plt.close()

    insights["correlation_findings"] = {
        "salary_experience_corr": round(float(corr_matrix.loc["Salary", "Experience_Years"]), 2),
        "satisfaction_attrition_corr": round(float(corr_matrix.loc["Job_Satisfaction", "Attrition"]), 2),
        "balance_attrition_corr": round(float(corr_matrix.loc["Work_Life_Balance", "Attrition"]), 2),
        "key_insight": f"Job Satisfaction ({corr_matrix.loc['Job_Satisfaction', 'Attrition']:.2f}) and Work-Life Balance ({corr_matrix.loc['Work_Life_Balance', 'Attrition']:.2f}) show strong negative correlations with Attrition, signaling retention sensitivity to workplace well-being."
    }

    with open(INSIGHTS_JSON, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2)

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# Enterprise Workforce Exploratory Data Analysis (EDA) Report\n\n")
        f.write("## Executive Summary\n")
        f.write(f"Comprehensive analysis conducted on {len(df)} active enterprise employee records across 7 organizational divisions.\n\n")
        f.write("### Key Analytical Insights\n")
        for section, data in insights.items():
            f.write(f"#### {section.replace('_', ' ').title()}\n")
            f.write(f"- **Finding:** {data.get('key_insight', '')}\n")
            for k, v in data.items():
                if k != 'key_insight' and not isinstance(v, dict):
                    f.write(f"- *{k.replace('_', ' ').title()}:* {v}\n")
            f.write("\n")

    print("[SUCCESS] All 10 EDA visualizations and structured insights generated successfully.")
    print(f"Visualizations saved to: {CHARTS_DIR}")
    print(f"Insights saved to: {INSIGHTS_JSON}")
    print("=" * 60)
    return insights

if __name__ == "__main__":
    run_eda()

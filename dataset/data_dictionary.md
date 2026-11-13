# Workforce Analytics Data Dictionary

This document explains the schema and semantic meaning of all fields in the raw and processed employee datasets.

## Dataset Overview
- **Total Records:** 655 raw records (650 unique employees + 5 duplicate validation rows)
- **Domain:** Enterprise Workforce Insights & AI Skills Analytics
- **File:** `dataset_raw.csv` and `dataset_cleaned.csv`

---

## Column Descriptions

| Column Name | Data Type (Raw) | Target Type | Nullable? | Description & Business Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **`Employee_ID`** | String | String | No | Unique alphanumeric employee identifier (e.g., `EMP0001`). Used as primary key. |
| **`Name`** | String | String | No | Full legal name of the employee. |
| **`Age`** | Integer | Integer | No | Age in completed years (range: 22 - 62). |
| **`Gender`** | String | Category | No | Self-reported gender identity (`Male`, `Female`, `Non-Binary`). |
| **`Department`** | String | Category | No | Organizational functional unit: `Engineering`, `Data & AI`, `Product`, `Human Resources`, `Sales & Marketing`, `Finance`, `Customer Support`. |
| **`Job_Role`** | String | Category | No | Specific organizational title/position (e.g., `Data Scientist`, `Cloud Architect`). |
| **`Experience_Years`** | Float | Float | No | Professional industry experience in years (range: 0.5 - 25.0). |
| **`Salary`** | Float/Int | Float | No | Annual base compensation in USD (cleaned: $45,000 - $210,000). |
| **`Education`** | String | Category | Yes (Imputed) | Highest achieved educational credential (`Associate Degree`, `Bachelor's Degree`, `Master's Degree`, `Ph.D.`). |
| **`Technical_Skills`** | String | List/Text | No | Comma-delimited list of proven technical proficiencies (e.g., `Python, SQL, React, AWS, Docker`). |
| **`Soft_Skills`** | String | List/Text | Yes (Imputed) | Comma-delimited list of interpersonal proficiencies (e.g., `Problem Solving, Leadership, Teamwork`). |
| **`Performance_Rating`**| Float | Float | No | Most recent annual appraisal score on a standard 1.0 - 5.0 scale (3.0 = Meets Expectations, 5.0 = Exceptional). |
| **`Location`** | String | Category | No | Primary office base or employment arrangement (e.g., `San Francisco, CA`, `Remote`, `Bangalore, IN`). |
| **`Training_History`** | String | String | Yes (Imputed) | Most recently completed corporate learning program or professional certification. |
| **`Overtime`** | String | Boolean/Int | No | Whether the employee frequently clocks mandatory or voluntary overtime hours (`Yes` / `No`). |
| **`Job_Satisfaction`** | Integer | Integer | No | Standardized survey score from 1 (Very Dissatisfied) to 5 (Very Satisfied). |
| **`Work_Life_Balance`**| Integer | Integer | No | Employee rating of balance between personal life and work demands (1 - 5). |
| **`Projects_Completed`**| Integer | Integer | No | Cumulative number of enterprise initiatives/projects delivered. |
| **`Attrition`** | Integer | Binary (0/1) | No | Target indicator: `1` if employee has signaled departure or high flight risk; `0` if actively retained. |

---

## Engineered Features (Added During Preprocessing)

1. **`Skill_Count`**: Total count of validated technical skills possessed by the employee.
2. **`Salary_Per_Exp`**: Ratio of annual compensation to years of experience (`Salary / max(1, Experience_Years)`).
3. **`Tenure_Tier`**: Categorical career tier: `Entry Level (0-2y)`, `Mid Level (3-5y)`, `Senior (6-10y)`, `Staff/Lead (11-15y)`, `Principal/Exec (16y+)`.
4. **`Performance_Tier`**: Qualitative performance bracket: `Needs Improvement (<2.5)`, `Meets Expectations (2.5-3.5)`, `High Performer (3.6-4.4)`, `Top Performer (4.5+)`.
5. **`Has_Training`**: Binary flag indicating whether the employee has attended professional training programs within the cycle.

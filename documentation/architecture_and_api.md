# NexusHR: Architecture & API Specifications

This document outlines the system architecture, component interactions, database schema relationships, and REST API contracts for the **Workforce Insights & AI-Powered Employee Skills Analytics Dashboard**.

---

## 1. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                      |
|   React 18 Single-Page Dashboard (Tailwind CSS, Lucide Icons, Chart.js, Marked)   |
|   10 Enterprise Views: Overview, Demographics, Skills, EDA, ML, Gap, RAG, CRUD   |
+------------------------------------------+----------------------------------------+
                                           | HTTP / JSON REST APIs
+------------------------------------------v----------------------------------------+
|                                 BACKEND LAYER                                     |
|                       FastAPI Asynchronous Micro-Framework                        |
|                                                                                   |
|  +--------------------+  +--------------------+  +--------------------+           |
|  | Analytics Engine   |  | ML Inference Engine|  | RAG Synthesizer    |           |
|  | - KPI Aggregators  |  | - Random Forest    |  | - TF-IDF Vector    |           |
|  | - EDA Endpoints    |  | - K-Means Clusters |  |   Index (676 docs) |           |
|  | - Skills Matrix    |  | - Gap Benchmarking |  | - Grounded Answers |           |
|  +--------------------+  +--------------------+  +--------------------+           |
+------------------------------------------+----------------------------------------+
                                           | SQLAlchemy / Raw SQL
+------------------------------------------v----------------------------------------+
|                                 DATABASE LAYER                                    |
|   Relational SQLite / PostgreSQL Database (workforce.db)                          |
|   - departments (7 divisions, budgets, managers)                                  |
|   - employees (650 profiles, demographics, salaries, performance)                 |
|   - employee_skills (5,024 normalized technical & soft proficiencies)             |
|   - performance_records (appraisal reviews, goals, scores)                        |
|   - training_records (certifications, completion statuses)                         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Relational Database Schema

### Table: `departments`
- `id` (INTEGER, Primary Key, Auto-increment)
- `department_code` (VARCHAR(10), Unique)
- `name` (VARCHAR(100), Unique)
- `budget` (DECIMAL(15,2))
- `head_count` (INTEGER)
- `manager_name` (VARCHAR(100))

### Table: `employees`
- `id` (INTEGER, Primary Key, Auto-increment)
- `employee_id` (VARCHAR(20), Unique, Indexed)
- `name` (VARCHAR(100))
- `age` (INTEGER)
- `gender` (VARCHAR(20))
- `department_id` (INTEGER, Foreign Key -> `departments.id`)
- `job_role` (VARCHAR(100))
- `experience_years` (DECIMAL(4,1))
- `salary` (DECIMAL(12,2))
- `education` (VARCHAR(50))
- `location` (VARCHAR(100))
- `overtime` (VARCHAR(5))
- `job_satisfaction` (INTEGER)
- `work_life_balance` (INTEGER)
- `performance_rating` (DECIMAL(3,1))
- `attrition` (INTEGER)
- `tenure_tier` (VARCHAR(50))
- `performance_tier` (VARCHAR(50))

### Table: `employee_skills`
- `id` (INTEGER, Primary Key)
- `employee_id` (VARCHAR(20), Foreign Key -> `employees.employee_id` ON DELETE CASCADE)
- `skill_name` (VARCHAR(100), Indexed)
- `skill_type` (VARCHAR(20), CHECK `Technical` or `Soft`)
- `proficiency_level` (VARCHAR(30))

### Table: `performance_records`
- `id` (INTEGER, Primary Key)
- `employee_id` (VARCHAR(20), Foreign Key -> `employees.employee_id` ON DELETE CASCADE)
- `review_period` (VARCHAR(50))
- `rating` (DECIMAL(3,1))
- `goals_achieved` (INTEGER)
- `feedback` (TEXT)
- `reviewer` (VARCHAR(100))

### Table: `training_records`
- `id` (INTEGER, Primary Key)
- `employee_id` (VARCHAR(20), Foreign Key -> `employees.employee_id` ON DELETE CASCADE)
- `course_name` (VARCHAR(150))
- `completion_status` (VARCHAR(30))
- `score` (INTEGER)
- `completion_date` (VARCHAR(50))

---

## 3. Core REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status. |
| `GET` | `/api/analytics/overview` | Executive workforce KPIs, department distribution, gender breakdown. |
| `GET` | `/api/analytics/skills` | Top 15 technical skills, top soft skills, department competency matrix. |
| `GET` | `/api/analytics/departments` | Financial budgets, headcounts, average salaries, attrition rates. |
| `GET` | `/api/analytics/eda` | Pre-calculated statistical findings and URLs to 10 visual charts. |
| `GET` | `/api/employees` | Filterable, paginated employee list (search, department, experience, skill). |
| `GET` | `/api/employees/{id}` | Detailed employee profile with normalized skills, training, and reviews. |
| `POST` | `/api/employees` | Creates employee and normalized skill entries. |
| `PUT` | `/api/employees/{id}` | Updates existing employee attributes and skill sets. |
| `DELETE`| `/api/employees/{id}` | Cascading deletion of employee and related records. |
| `GET` | `/api/employees/export/csv` | Streams database export as downloadable CSV file. |
| `POST` | `/api/ml/predict-attrition` | Random Forest flight risk scoring, probability %, and risk drivers. |
| `GET` | `/api/ml/clusters` | 4 K-Means workforce persona clusters and centroids. |
| `GET` | `/api/skills/benchmarks` | Benchmark competency requirements across 11 major organizational roles. |
| `POST` | `/api/skills/analyze-gap` | Evaluates employee skill fit % vs benchmark and recommends training courses. |
| `POST` | `/api/ai/recommend-team` | Optimization matcher staffing projects based on skills and experience. |
| `POST` | `/api/ai/chat` | RAG chatbot endpoint answering workforce questions with citations. |

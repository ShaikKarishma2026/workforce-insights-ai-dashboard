-- Workforce Insights Relational Database Schema
-- Compatible with PostgreSQL, MySQL, and SQLite (Standard ANSI SQL DDL)

-- 1. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    budget DECIMAL(15, 2) NOT NULL DEFAULT 500000.00,
    head_count INTEGER DEFAULT 0,
    manager_name VARCHAR(100)
);

-- 2. Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    department_id INTEGER NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    experience_years DECIMAL(4, 1) NOT NULL,
    salary DECIMAL(12, 2) NOT NULL,
    education VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    overtime VARCHAR(5) DEFAULT 'No',
    job_satisfaction INTEGER NOT NULL,
    work_life_balance INTEGER NOT NULL,
    performance_rating DECIMAL(3, 1) NOT NULL,
    attrition INTEGER DEFAULT 0,
    tenure_tier VARCHAR(50),
    performance_tier VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
);

-- 3. Employee Skills Table (Relational Normalized Multi-Value Storage)
CREATE TABLE IF NOT EXISTS employee_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    skill_type VARCHAR(20) NOT NULL CHECK (skill_type IN ('Technical', 'Soft')),
    proficiency_level VARCHAR(30) DEFAULT 'Intermediate',
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 4. Performance Records Table
CREATE TABLE IF NOT EXISTS performance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) NOT NULL,
    review_period VARCHAR(50) NOT NULL,
    rating DECIMAL(3, 1) NOT NULL,
    goals_achieved INTEGER DEFAULT 90,
    feedback TEXT,
    reviewer VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 5. Training Records Table
CREATE TABLE IF NOT EXISTS training_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20) NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    completion_status VARCHAR(30) DEFAULT 'Completed',
    score INTEGER DEFAULT 85,
    completion_date VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Indexes for lightning fast analytics and searching
CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_emp_role ON employees(job_role);
CREATE INDEX IF NOT EXISTS idx_emp_skills ON employee_skills(skill_name);
CREATE INDEX IF NOT EXISTS idx_emp_attrition ON employees(attrition);

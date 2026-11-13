"""
Pydantic Data Models and Schemas for REST API Endpoints
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Employee Schemas
class EmployeeCreateSchema(BaseModel):
    name: str = Field(..., example="Elena Rostova")
    age: int = Field(..., ge=18, le=75, example=29)
    gender: str = Field("Female", example="Female")
    department_name: str = Field("Data & AI", example="Data & AI")
    job_role: str = Field("Data Scientist", example="Data Scientist")
    experience_years: float = Field(..., ge=0, le=40, example=4.5)
    salary: float = Field(..., ge=20000, le=400000, example=115000.0)
    education: str = Field("Master's Degree", example="Master's Degree")
    location: str = Field("San Francisco, CA", example="San Francisco, CA")
    technical_skills: List[str] = Field(..., example=["Python", "SQL", "Machine Learning", "Pandas"])
    soft_skills: List[str] = Field(["Problem Solving", "Communication"], example=["Problem Solving", "Communication"])
    performance_rating: float = Field(3.8, ge=1.0, le=5.0, example=4.0)
    overtime: str = Field("No", example="No")
    job_satisfaction: int = Field(4, ge=1, le=5, example=4)
    work_life_balance: int = Field(4, ge=1, le=5, example=4)
    training_course: Optional[str] = Field(None, example="Advanced Machine Learning & Deep Learning")

class EmployeeUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    experience_years: Optional[float] = None
    salary: Optional[float] = None
    education: Optional[str] = None
    location: Optional[str] = None
    overtime: Optional[str] = None
    job_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    performance_rating: Optional[float] = None
    attrition: Optional[int] = None
    technical_skills: Optional[List[str]] = None

# ML Prediction Schemas
class AttritionPredictRequest(BaseModel):
    employee_id: Optional[str] = None
    age: int = 32
    experience_years: float = 5.0
    salary: float = 95000.0
    job_satisfaction: int = 3
    work_life_balance: int = 3
    performance_rating: float = 3.8
    projects_completed: int = 12
    overtime: str = "No"
    skill_count: int = 5
    has_training: int = 1
    department: str = "Engineering"
    gender: str = "Female"

# Skill Gap Analysis Schemas
class SkillGapRequest(BaseModel):
    employee_id: Optional[str] = None
    current_skills: Optional[List[str]] = None
    target_role: str = Field(..., example="Senior Data Scientist")

# Project Team Recommendation Schemas
class TeamRecommendRequest(BaseModel):
    project_name: str = "AI Analytics Initiative"
    required_skills: List[str] = Field(..., example=["Python", "SQL", "Machine Learning"])
    min_experience_years: float = 2.0
    team_size: int = 4

# AI Chat Schemas
class AIChatRequest(BaseModel):
    message: str = Field(..., example="Which department has the highest number of employees?")

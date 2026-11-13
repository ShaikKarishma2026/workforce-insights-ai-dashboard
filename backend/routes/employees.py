"""
Employee Management REST API Endpoints
"""

import csv
import io
from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional, List

from database.crud import (
    create_employee, get_employee, list_employees,
    update_employee, delete_employee, get_all_departments
)
from backend.models import EmployeeCreateSchema, EmployeeUpdateSchema

router = APIRouter(prefix="/api/employees", tags=["Employee Management"])

@router.get("")
def get_employees_list(
    department: Optional[str] = Query(None, description="Filter by department name"),
    min_exp: Optional[float] = Query(None, description="Minimum years of experience"),
    max_exp: Optional[float] = Query(None, description="Maximum years of experience"),
    skill: Optional[str] = Query(None, description="Filter by skill substring"),
    search: Optional[str] = Query(None, description="Search term for name, ID, or role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200)
):
    """Retrieve filtered, paginated list of employees."""
    return list_employees(
        department=department,
        min_exp=min_exp,
        max_exp=max_exp,
        skill=skill,
        search=search,
        skip=skip,
        limit=limit
    )

@router.get("/export/csv")
def export_employees_csv():
    """Download the complete employee workforce dataset as a CSV file."""
    data = list_employees(limit=1000)
    employees = data["employees"]
    
    output = io.StringIO()
    if employees:
        writer = csv.DictWriter(output, fieldnames=employees[0].keys())
        writer.writeheader()
        writer.writerows(employees)
    else:
        output.write("No employee data available\n")
        
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=workforce_employees_export.csv"}
    )

@router.get("/{employee_id}")
def get_single_employee(employee_id: str):
    """Retrieve detailed employee record including skills, reviews, and training history."""
    emp = get_employee(employee_id.upper())
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return emp

@router.post("", status_code=201)
def add_new_employee(payload: EmployeeCreateSchema):
    """Create a new employee record and populate relational skills."""
    created = create_employee(
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        department_name=payload.department_name,
        job_role=payload.job_role,
        experience_years=payload.experience_years,
        salary=payload.salary,
        education=payload.education,
        location=payload.location,
        technical_skills=payload.technical_skills,
        soft_skills=payload.soft_skills,
        performance_rating=payload.performance_rating,
        overtime=payload.overtime,
        job_satisfaction=payload.job_satisfaction,
        work_life_balance=payload.work_life_balance,
        training_course=payload.training_course
    )
    return {"message": "Employee created successfully", "employee": created}

@router.put("/{employee_id}")
def update_existing_employee(employee_id: str, payload: EmployeeUpdateSchema):
    """Update existing employee details and skills."""
    updates = payload.model_dump(exclude_unset=True)
    updated = update_employee(employee_id.upper(), updates)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return {"message": "Employee updated successfully", "employee": updated}

@router.delete("/{employee_id}")
def remove_employee(employee_id: str):
    """Delete an employee and cascade delete all relational skill and performance records."""
    success = delete_employee(employee_id.upper())
    if not success:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return {"message": f"Employee {employee_id} deleted successfully"}

# Additional Department API
dept_router = APIRouter(prefix="/api/departments", tags=["Departments"])

@dept_router.get("")
def list_departments():
    """List all corporate departments with allocated budgets and headcounts."""
    return get_all_departments()

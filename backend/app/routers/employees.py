"""
Employee management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_manager_or_admin, require_admin
from ..core.audit import log_action, AuditAction
from ..models.employee import Employee
from ..models.user import User
from ..schemas.employee import EmployeeCreate, EmployeeUpdate, Employee as EmployeeSchema, EmployeeList

router = APIRouter()


@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
async def create_employee(
    request: Request,
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """Create a new employee (Requires MANAGER or ADMIN role)"""
    # Check if badge code already exists
    existing = db.query(Employee).filter(Employee.badge_code == employee_data.badge_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with badge code {employee_data.badge_code} already exists"
        )

    # Create employee
    db_employee = Employee(**employee_data.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    # Log creation
    log_action(
        db=db,
        action=AuditAction.CREATE_EMPLOYEE,
        user=current_user,
        resource_type="employee",
        resource_id=db_employee.id,
        details={
            "name": db_employee.name,
            "surname": db_employee.surname,
            "badge_code": db_employee.badge_code,
            "role": db_employee.role
        },
        request=request
    )

    return db_employee


@router.get("/", response_model=EmployeeList)
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List employees with optional filtering"""
    query = db.query(Employee)

    # Filter by active status
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    # Search by name, surname, or badge code
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Employee.name.ilike(search_term)) |
            (Employee.surname.ilike(search_term)) |
            (Employee.badge_code.ilike(search_term))
        )

    total = query.count()
    employees = query.offset(skip).limit(limit).all()

    return {"total": total, "employees": employees}


@router.get("/{employee_id}", response_model=EmployeeSchema)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get employee by ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """Update employee (Requires MANAGER or ADMIN role)"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Check badge code uniqueness if updating
    if employee_data.badge_code and employee_data.badge_code != employee.badge_code:
        existing = db.query(Employee).filter(Employee.badge_code == employee_data.badge_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with badge code {employee_data.badge_code} already exists"
            )

    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    old_values = {}
    for field, value in update_data.items():
        old_values[field] = getattr(employee, field)
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    # Log update
    log_action(
        db=db,
        action=AuditAction.UPDATE_EMPLOYEE,
        user=current_user,
        resource_type="employee",
        resource_id=employee.id,
        details={
            "updated_fields": list(update_data.keys()),
            "old_values": old_values,
            "new_values": update_data
        },
        request=request
    )

    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete employee (Requires ADMIN role)"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Store data for audit log before deletion
    employee_data = {
        "name": employee.name,
        "surname": employee.surname,
        "badge_code": employee.badge_code,
        "role": employee.role
    }

    db.delete(employee)
    db.commit()

    # Log deletion
    log_action(
        db=db,
        action=AuditAction.DELETE_EMPLOYEE,
        user=current_user,
        resource_type="employee",
        resource_id=employee_id,
        details=employee_data,
        request=request
    )

    return None

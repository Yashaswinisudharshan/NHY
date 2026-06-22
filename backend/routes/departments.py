from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Department
from schemas import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentResponse)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    new_dept = Department(**dept.model_dump())
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@router.get("/", response_model=list[DepartmentResponse])
def get_all_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()
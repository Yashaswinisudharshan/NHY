from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    priority_score = Column(Float, default=5.0)
    annual_budget_limit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, nullable=False)
    allocated_amount = Column(Float, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=func.now())
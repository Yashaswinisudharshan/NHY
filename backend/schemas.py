from pydantic import BaseModel
from typing import Optional

GOVERNMENT_SCHEMES = [
    "PM Awas Yojana",
    "MGNREGA",
    "PM Kisan Samman Nidhi",
    "Ayushman Bharat",
    "Mid Day Meal Scheme",
    "Swachh Bharat Mission",
    "PM Gram Sadak Yojana",
    "National Health Mission",
    "Samagra Shiksha Abhiyan",
    "PM Ujjwala Yojana",
    "Digital India",
    "Smart Cities Mission",
    "Atal Mission for Rejuvenation and Urban Transformation",
    "National Rural Livelihood Mission",
    "Pradhan Mantri Fasal Bima Yojana"
]

class DepartmentCreate(BaseModel):
    name: str
    priority_score: float
    annual_budget_limit: float

class DepartmentResponse(DepartmentCreate):
    id: int
    class Config:
        from_attributes = True

class BudgetRequestSchema(BaseModel):
    department_id: int
    requested_amount: float
    fiscal_year: int
    amount_allocated_last_year: float
    amount_utilized_last_year: float
    justification: str                    # now required, not optional
    scheme_name: str                      # must be from GOVERNMENT_SCHEMES list
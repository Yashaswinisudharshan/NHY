from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr

class User(BaseModel):
    user_id: Optional[int] = None
    full_name: str
    age: int
    caste: str
    state: str
    district: str
    aadhaar_number: str
    email: EmailStr
    password_hash: str
    created_at: Optional[datetime] = None

class Contractor(BaseModel):
    contractor_id: Optional[int] = None
    contractor_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    previous_projects: Optional[int] = 0
    avg_delay_days: Optional[Decimal] = 0
    avg_budget_overrun: Optional[Decimal] = 0
    fraud_rate: Optional[Decimal] = 0
    blacklist_flag: Optional[int] = 0
    approval_status: Optional[str] = "APPROVED"
    created_at: Optional[datetime] = None

class InspectionOfficer(BaseModel):
    officer_id: Optional[int] = None
    officer_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    approval_status: Optional[str] = "APPROVED"
    created_at: Optional[datetime] = None

class Project(BaseModel):
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    department: Optional[str] = None
    state_name: Optional[str] = None
    district: Optional[str] = None
    budget: Optional[Decimal] = None
    approved_work_quantity: Optional[Decimal] = None
    expected_completion_days: Optional[int] = None
    contractor_id: Optional[int] = None
    action_state: Optional[str] = None
    fraud_score: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    officer_id: Optional[int]=None
    
class Invoice(BaseModel):
    invoice_id: Optional[int] = None
    project_id: Optional[int] = None
    contractor_id: Optional[int] = None
    vendor_id: Optional[int] = None
    invoice_amount: Optional[Decimal] = None
    invoice_date: Optional[date] = None
    work_quantity_claimed: Optional[Decimal] = None
    status: Optional[str] = "PENDING"
    created_at: Optional[datetime] = None

class Inspection(BaseModel):
    inspection_id: Optional[int] = None
    project_id: Optional[int] = None
    officer_id: Optional[int] = None
    inspection_date: Optional[date] = None
    verified_work_quantity: Optional[Decimal] = None
    inspection_status: Optional[str] = "PENDING"
    geo_tagged_proof_submitted: Optional[int] = 0
    proof_document_count: Optional[int] = 0
    created_at: Optional[datetime] = None

class ProjectReport(BaseModel):
    report_id: Optional[int] = None
    project_id: Optional[int] = None
    amount_claimed: Optional[Decimal] = None
    amount_released: Optional[Decimal] = None
    work_completion_percent: Optional[Decimal] = None
    claimed_work_quantity: Optional[Decimal] = None
    actual_days_since_start: Optional[int] = None
    submitted_by: Optional[str] = None
    submission_date: Optional[date] = None
    created_at: Optional[datetime] = None

class Complaint(BaseModel):
    complaint_id: Optional[int] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    complaint_text: Optional[str] = None
    complaint_date: Optional[date] = None
    status: Optional[str] = "OPEN"
    created_at: Optional[datetime] = None

class Scheme(BaseModel):
    scheme_id: Optional[int] = None
    scheme_name: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    caste: Optional[str] = None
    money_per_person: Optional[int] = None
    budget_crores: Optional[Decimal] = None
    state: Optional[str] = None
    district: Optional[str] = None

class OfficialReport(BaseModel):
    report_id: Optional[int] = None
    scheme_id: Optional[int] = None
    scheme_name: Optional[str] = None
    district: Optional[str] = None
    report_month: Optional[date] = None
    reported_beneficiaries: Optional[int] = None
    reported_amount_spent: Optional[int] = None
    submitted_by: Optional[str] = None
    submitted_at: Optional[datetime] = None

class PaymentRecord(BaseModel):
    payment_id: Optional[int] = None
    scheme_id: Optional[int] = None
    beneficiary_id: Optional[str] = None
    state_name: Optional[str] = None
    district: Optional[str] = None
    payment_month: Optional[date] = None
    amount: Optional[int] = None
    payment_status: Optional[str] = None

class FraudResult(BaseModel):
    fraud_id: Optional[int] = None
    scheme_id: int
    scheme_name: str
    district: str
    report_month: date
    reported_beneficiaries: Optional[int] = 0
    actual_paid_beneficiaries: Optional[int] = 0
    beneficiary_difference: Optional[int] = 0
    reported_amount_spent: Optional[int] = 0
    actual_amount_paid: Optional[int] = 0
    amount_difference: Optional[int] = 0
    fraud_risk_level: Optional[str] = None
    fraud_reason: Optional[str] = None
    checked_at: Optional[datetime] = None
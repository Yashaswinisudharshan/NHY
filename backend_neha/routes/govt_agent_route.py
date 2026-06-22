from fastapi import APIRouter, Depends, HTTPException
from database.connection import get_db_cursor
from fastapi import UploadFile,File
from services.project_fraud_predict import predict_fraud
from services.project_report_service import submit_project_report

from pydantic import BaseModel, EmailStr

from auth.jwt_handler import require_role
from services.contractor_service import (
    create_contractor,
    get_contractor_by_id,
)
from services.scheme_fraud import (
    OfficialReportNotFoundError,
    calculate_overall_fraud,
    calculate_all_district_fraud,
)

from services.inspection_officer_service import (
    create_inspection_officer,
    get_inspection_officer_by_id,
    
)
from services.project_service import (
    create_project,
    get_project_by_id,
)
from services.scheme_uploads import (
    process_report_file,
    import_payment_csv,
)

router = APIRouter(prefix="/govt_agent", tags=["Govt_agent"])

class ProjectCreateRequest(BaseModel):
    project_name: str
    project_type: str
    department: str
    state_name: str
    district: str
    budget: float
    approved_work_quantity: float
    expected_completion_days: int
    contractor_id: int | None = None
    action_state: str = "CREATED"
    officer_id: int | None = None

@router.post("/project/create")
def create_project_route(
    payload: ProjectCreateRequest,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        project_id = create_project(payload.model_dump())

        return {
            "message": "Project created successfully",
            "project_id": project_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get("/project/{project_id}/get")
def get_project_route(
    project_id: int,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.get("/project/get_all")
def get_projects_govt(
    _current_user=Depends(require_role("GOV_AGENT"))
):
    with get_db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("SELECT * FROM projects")
        results = cursor.fetchall()

    return results


class ContractorCreateRequest(BaseModel):
    contractor_name: str
    email: EmailStr
    password: str
    previous_projects: int = 0
    avg_delay_days: float = 0
    avg_budget_overrun: float = 0
    fraud_rate: float = 0
    blacklist_flag: int = 0


@router.post("/contractor/create")
def add_contractor(
    payload: ContractorCreateRequest,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        contractor_id = create_contractor(payload.model_dump())

        return {
            "message": "Contractor registered successfully. Waiting for government approval.",
            "contractor_id": contractor_id,
        }

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



@router.get("/contractor/{contractor_id}/get")
def contractor_details(
    contractor_id: int,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    contractor = get_contractor_by_id(contractor_id)

    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return contractor



class InspectionOfficerCreateRequest(BaseModel):
    officer_name: str
    email: EmailStr
    password: str


@router.post("/inspection_officer/create")
def Add_inspection_officer(
    payload: InspectionOfficerCreateRequest,
   _current_user=Depends(require_role("GOV_AGENT"))    
 ):
    try:
        officer_id = create_inspection_officer(payload.model_dump())

        return {
            "message": "Inspection officer registered successfully. Waiting for government approval.",
            "officer_id": officer_id,
        }

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/inspection_officer/{officer_id}/get")
def inspection_officer_details(
    officer_id: int,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    officer = get_inspection_officer_by_id(officer_id)

    if not officer:
        raise HTTPException(
            status_code=404,
            detail="Inspection officer not found"
        )

    return officer



@router.get("/project/{project_id}/get_fraud")
def get_project_fraud_prediction(
    project_id: int,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        return predict_fraud(project_id)

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Fraud model file not found"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
    
class ProjectReportRequest(BaseModel):
    project_id: int
    amount_claimed: float
    amount_released: float
    work_completion_percent: float
    claimed_work_quantity: float
    actual_days_since_start: int
    submitted_by: str
    submission_date: str


@router.post("/project/submit_report")
def submit_report(
    payload: ProjectReportRequest,
    _current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        report_id = submit_project_report(payload.model_dump())

        return {
            "message": "Project report submitted successfully",
            "report_id": report_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
class SchemeCreateRequest(BaseModel):
    scheme_name: str
    min_age: int
    max_age: int | None = None
    caste: str
    money_per_person: int
    budget_crores: float
    state: str | None = None
    district: str | None = None
    
@router.post("/scheme/add")
def add_scheme(
    payload: SchemeCreateRequest,
    current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        query = """
        INSERT INTO schemes (
            scheme_name, min_age, max_age, caste,
            money_per_person, budget_crores, state, district
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            payload.scheme_name,
            payload.min_age,
            payload.max_age,
            payload.caste,
            payload.money_per_person,
            payload.budget_crores,
            payload.state or "all",
            payload.district or "all",
        )

        with get_db_cursor() as (_, cursor):
            cursor.execute(query, values)

        return {
            "success": True,
            "message": "Scheme added successfully",
            "scheme_id": cursor.lastrowid,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@router.get("/scheme/get_all")
def get_schemes(
    current_user=Depends(require_role("GOV_AGENT"))
):
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute("SELECT * FROM schemes")
        results = cursor.fetchall()

    return results

@router.get("/scheme/get_fraud")
def overall_fraud_for_selected_scheme(
    scheme_id: int,
    month: str,
    current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        result = calculate_overall_fraud(
            scheme_id,
            month,
        )

        return result

    except OfficialReportNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/scheme/district_fraud")
def get_all_district_fraud(
    scheme_id: int,
    month: str,
    current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        results = calculate_all_district_fraud(
            scheme_id,
            month,
        )

        return {
            "report_month": month,
            "district_count": len(results),
            "fraud_results": results,
        }

    except OfficialReportNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/scheme/upload_report")
def upload_reports(
    file: UploadFile = File(...),
    current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        process_report_file(file)

        return {
            "message": "Report uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scheme/upload_records")
def upload_csv(
    file: UploadFile = File(...),
    current_user=Depends(require_role("GOV_AGENT"))
):
    try:
        import_payment_csv(file)

        return {
            "message": "CSV data uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
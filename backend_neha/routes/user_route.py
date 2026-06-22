from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.jwt_handler import require_role
from services.complaint_service import add_complaint
from database.connection import get_db_cursor
from services.eligible_schemes import get_eligible_schemes_for_user

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


class ComplaintCreateRequest(BaseModel):
    project_id: int
    complaint_text: str
    complaint_date: str
    status: str = "OPEN"


@router.post("/complaints")
def add_complaint_route(
    payload: ComplaintCreateRequest,
    current_user=Depends(require_role("CITIZEN"))
):
    try:
        complaint_id = add_complaint(
            payload.model_dump(),
            current_user["id"]   # user_id from JWT
        )

        return {
            "message": "Complaint submitted successfully",
            "complaint_id": complaint_id
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
    
@router.get("/user_projects")
def get_projects_citizen_route(
    state: str,
    district: str,
    _current_user=Depends(require_role("CITIZEN"))
):
    with get_db_cursor(dictionary=True) as (conn, cursor):

        cursor.execute("""
            SELECT *
            FROM projects
            WHERE state_name = %s
            AND district = %s
        """, (state, district))

        projects = cursor.fetchall()

    return projects

@router.get("/eligible_schemes")
def eligible_schemes(current_user=Depends(require_role("CITIZEN"))):
    return get_eligible_schemes_for_user(current_user["id"])

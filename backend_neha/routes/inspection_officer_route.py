from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.jwt_handler import require_role
from services.inspection_service import add_inspection,get_invoices_for_officer,update_invoice_status

router = APIRouter(
    prefix="/inspection-officer",
    tags=["Inspection Officer"]
)


class InspectionCreateRequest(BaseModel):
    project_id: int
    inspection_date: str
    verified_work_quantity: float
    inspection_status: str = "PENDING"
    geo_tagged_proof_submitted: int = 0
    proof_document_count: int = 0


@router.post("/add_inspections")
def add_inspection_route(
    payload: InspectionCreateRequest,
    current_user=Depends(require_role("INSPECTION_OFFICER"))
):
    try:
        inspection_id = add_inspection(
            payload.model_dump(),
            current_user["id"]      # officer_id from JWT
        )

        return {
            "message": "Inspection submitted successfully",
            "inspection_id": inspection_id
        }

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
    
@router.get("/get_invoices")
def get_invoices_route(
    current_user=Depends(require_role("INSPECTION_OFFICER"))
):
    return get_invoices_for_officer(current_user["id"])

class InvoiceStatusUpdateRequest(BaseModel):
    status: str

@router.put("/invoices/{invoice_id}/status")
def update_invoice_status_route(
    invoice_id: int,
    payload: InvoiceStatusUpdateRequest,
    current_user=Depends(require_role("INSPECTION_OFFICER"))
):
    try:
        updated = update_invoice_status(
            invoice_id,
            payload.status,
            current_user["id"]
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Invoice not found or not assigned to this officer"
            )

        return {
            "message": "Invoice status updated successfully",
            "invoice_id": invoice_id,
            "status": payload.status
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
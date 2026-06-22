from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from auth.jwt_handler import require_role
from services.invoice_service import add_invoice

router = APIRouter(
    prefix="/contractor",
    tags=["Contractor"]
)


class InvoiceCreateRequest(BaseModel):
    project_id: int
    vendor_id: int
    invoice_amount: float
    invoice_date: date
    work_quantity_claimed: float
    status: str = "PENDING"


@router.post("/add_invoices")
def add_invoice_route(
    payload: InvoiceCreateRequest,
    current_user=Depends(require_role("CONTRACTOR"))
):
    try:
        invoice_id = add_invoice(
            payload.model_dump(),
            current_user["id"]      # contractor_id from JWT
        )

        return {
            "message": "Invoice submitted successfully",
            "invoice_id": invoice_id
        }

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, mongo_db
from models import Department, BudgetAllocation
from schemas import BudgetRequestSchema, GOVERNMENT_SCHEMES
from services.allocator import calculate_allocation, generate_ai_recommendation
from services.inflation import get_india_inflation_rate
from services.justification import validate_justification
from datetime import datetime
import traceback

router = APIRouter(prefix="/budget", tags=["Budget"])

@router.get("/schemes")
def get_schemes():
    """
    Returns list of valid government schemes.
    Frontend will use this to show a dropdown — 
    no hardcoded list needed on the frontend side.
    """
    return {"schemes": GOVERNMENT_SCHEMES}

@router.post("/request")
def submit_budget_request(request: BudgetRequestSchema, db: Session = Depends(get_db)):
    try:
        # 1. Validate scheme name
        if request.scheme_name not in GOVERNMENT_SCHEMES:
            return {
                "error": f"Invalid scheme. Choose from: {GOVERNMENT_SCHEMES}"
            }

        # 2. AI Justification check — before doing anything else
        justification_check = validate_justification(
            justification=request.justification,
            scheme_name=request.scheme_name
        )
        
        # If justification is vague, reject the request early
        if not justification_check["is_valid"]:
            return {
                "error": "Budget request rejected",
                "reason": justification_check["reason"],
                "confidence": justification_check["confidence"],
                "tip": "Provide specific details: locations, beneficiary count, objectives"
            }

        # 3. Get department from PostgreSQL
        dept = db.query(Department).filter(
            Department.id == request.department_id
        ).first()
        if not dept:
            return {"error": "Department not found"}

        # 4. Auto fetch inflation rate
        inflation_rate = get_india_inflation_rate()

        # 5. Run smart allocation formula
        result = calculate_allocation(
            requested_amount=request.requested_amount,
            priority_score=dept.priority_score,
            annual_budget_limit=dept.annual_budget_limit,
            amount_allocated_last_year=request.amount_allocated_last_year,
            amount_utilized_last_year=request.amount_utilized_last_year,
            inflation_rate=inflation_rate
        )

        # 6. Generate AI policy recommendation
        recommendation = generate_ai_recommendation(
            dept_name=dept.name,
            requested=request.requested_amount,
            final_allocation=result["final_allocation"],
            inflation_rate=inflation_rate,
            efficiency_score=result["efficiency_score"],
            priority_score=dept.priority_score
        )

        # 7. Save to PostgreSQL
        allocation = BudgetAllocation(
            department_id=request.department_id,
            allocated_amount=result["final_allocation"],
            fiscal_year=request.fiscal_year,
            status="pending"
        )
        db.add(allocation)
        db.commit()
        db.refresh(allocation)

        # 8. Log everything to MongoDB
        mongo_db["budget_requests"].insert_one({
            "department_id": request.department_id,
            "department_name": dept.name,
            "scheme_name": request.scheme_name,
            "requested": request.requested_amount,
            "allocated": result["final_allocation"],
            "inflation_rate": inflation_rate,
            "efficiency_score": result["efficiency_score"],
            "priority_weight": result["priority_weight"],
            "breakdown": result["breakdown"],
            "recommendation": recommendation,
            "justification": request.justification,
            "justification_check": justification_check,
            "fiscal_year": request.fiscal_year,
            "timestamp": datetime.utcnow()
        })

        return {
            "department": dept.name,
            "scheme": request.scheme_name,
            "requested": request.requested_amount,
            "allocated": result["final_allocation"],
            "inflation_rate_used": inflation_rate,
            "breakdown": result["breakdown"],
            "factors": {
                "inflation_multiplier": result["inflation_multiplier"],
                "efficiency_score": result["efficiency_score"],
                "priority_weight": result["priority_weight"]
            },
            "justification_check": justification_check,
            "ai_recommendation": recommendation
        }

    except Exception as e:
        print(f"ERROR IN BUDGET REQUEST: {e}")
        traceback.print_exc()
        return {"error": str(e)}


@router.get("/allocations")
def get_all_allocations(db: Session = Depends(get_db)):
    return db.query(BudgetAllocation).all()


@router.get("/history")
def get_budget_history():
    records = list(mongo_db["budget_requests"].find(
        {}, {"_id": 0}
    ))
    return records
@router.delete("/history/clear")
def clear_history():
    mongo_db["budget_requests"].delete_many({})
    return {"message": "History cleared"}

@router.delete("/allocations/clear")
def clear_allocations(db: Session = Depends(get_db)):
    db.query(BudgetAllocation).delete()
    db.commit()
    return {"message": "Allocations cleared"}
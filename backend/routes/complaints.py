from fastapi import APIRouter, UploadFile, File, Form, Header
from database import mongo_db
from services.translator import detect_and_translate
from services.image_classifier import classify_complaint_image
from services.auth import verify_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/complaints", tags=["Complaints"])

COMPLAINT_STAGES = [
    "Submitted",
    "Under Review",
    "In Progress",
    "Resolved"
]


def classify_from_text(translated_text: str) -> dict:
    text = translated_text.lower()
    if any(w in text for w in ["pothole", "road", "street", "highway", "crack", "pit"]):
        return {"category": "road damage or pothole", "department": "Infrastructure"}
    elif any(w in text for w in ["garbage", "waste", "trash", "dump", "litter"]):
        return {"category": "garbage or waste dumping", "department": "Sanitation"}
    elif any(w in text for w in ["flood", "water", "drain", "waterlog"]):
        return {"category": "flooding or waterlogging", "department": "Infrastructure"}
    elif any(w in text for w in ["light", "lamp", "dark", "streetlight"]):
        return {"category": "broken streetlight", "department": "Electricity"}
    elif any(w in text for w in ["sewage", "sewer", "smell", "drainage"]):
        return {"category": "sewage overflow", "department": "Sanitation"}
    elif any(w in text for w in ["construct", "building", "illegal"]):
        return {"category": "illegal construction", "department": "Urban Development"}
    elif any(w in text for w in ["water supply", "tap", "pipe", "no water"]):
        return {"category": "water supply issue", "department": "Water Supply"}
    else:
        return {"category": "public property damage", "department": "Municipal"}


def require_admin(authorization: str):
    """
    Helper that checks if the request has a valid admin token.
    Call this at the start of any admin-only route.
    """
    if not authorization:
        raise ValueError("No token provided")
    token = authorization.replace("Bearer ", "")
    return verify_token(token)


@router.post("/submit")
async def submit_complaint(
    description: str = Form(...),
    location: str = Form(...),
    citizen_name: str = Form(...),
    image: UploadFile = File(None)
):
    # Step 1: Translate
    translation = detect_and_translate(description)
    translated = translation["translated_text"]

    # Step 2: Text classification
    text_classification = classify_from_text(translated)

    # Step 3: Image classification
    image_classification = None
    if image:
        image_bytes = await image.read()
        image_classification = classify_complaint_image(image_bytes)

    # Step 4: Final category decision
    if image_classification and image_classification.get("confidence", 0) > 0.3:
        final_category = image_classification["category"]
        final_department = image_classification["department"]
        classification_source = "image_ai"
    else:
        final_category = text_classification["category"]
        final_department = text_classification["department"]
        classification_source = "text_keywords"

    complaint_id = f"CMP-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

    complaint = {
        "complaint_id": complaint_id,
        "citizen_name": citizen_name,
        "location": location,
        "original_description": description,
        "detected_language": translation["detected_language"],
        "translated_description": translated,
        "category": final_category,
        "assigned_department": final_department,
        "classification_source": classification_source,
        "image_confidence": image_classification.get("confidence") if image_classification else None,
        "status": "Submitted",
        "stage_history": [
            {
                "stage": "Submitted",
                "timestamp": datetime.utcnow(),
                "note": "Complaint received and registered"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    mongo_db["complaints"].insert_one(complaint)

    return {
        "complaint_id": complaint_id,
        "message": f"Complaint registered! Track with ID: {complaint_id}",
        "category": final_category,
        "assigned_to": final_department,
        "classification_source": classification_source,
        "status": "Submitted",
        "translation": translation
    }


@router.get("/track/{complaint_id}")
def track_complaint(complaint_id: str):
    """Public — anyone can track with their ID"""
    complaint = mongo_db["complaints"].find_one(
        {"complaint_id": complaint_id},
        {"_id": 0}
    )
    if not complaint:
        return {"error": "Complaint not found"}
    return complaint


@router.get("/all")
def get_all_complaints(authorization: str = Header(None)):
    """Admin only — requires token"""
    try:
        require_admin(authorization)
    except:
        return {"error": "Unauthorized. Admin login required."}
    complaints = list(mongo_db["complaints"].find({}, {"_id": 0}))
    return complaints


@router.get("/stats")
def get_complaint_stats(authorization: str = Header(None)):
    """Admin only — requires token"""
    try:
        require_admin(authorization)
    except:
        return {"error": "Unauthorized. Admin login required."}

    total = mongo_db["complaints"].count_documents({})
    by_status = {}
    for stage in COMPLAINT_STAGES:
        by_status[stage] = mongo_db["complaints"].count_documents({"status": stage})

    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    by_category = {
        doc["_id"]: doc["count"]
        for doc in mongo_db["complaints"].aggregate(pipeline)
    }

    return {"total": total, "by_status": by_status, "by_category": by_category}


@router.put("/update-stage/{complaint_id}")
def update_complaint_stage(
    complaint_id: str,
    stage: str,
    note: str = "",
    authorization: str = Header(None)
):
    """Admin only — requires token"""
    try:
        require_admin(authorization)
    except:
        return {"error": "Unauthorized. Admin login required."}

    if stage not in COMPLAINT_STAGES:
        return {"error": f"Invalid stage. Must be one of: {COMPLAINT_STAGES}"}

    complaint = mongo_db["complaints"].find_one({"complaint_id": complaint_id})
    if not complaint:
        return {"error": "Complaint not found"}

    stage_entry = {
        "stage": stage,
        "timestamp": datetime.utcnow(),
        "note": note or f"Status updated to {stage}"
    }

    mongo_db["complaints"].update_one(
        {"complaint_id": complaint_id},
        {
            "$set": {"status": stage, "updated_at": datetime.utcnow()},
            "$push": {"stage_history": stage_entry}
        }
    )

    return {"complaint_id": complaint_id, "new_status": stage}


@router.get("/by-department/{department}")
def get_complaints_by_department(
    department: str,
    authorization: str = Header(None)
):
    """Admin only"""
    try:
        require_admin(authorization)
    except:
        return {"error": "Unauthorized. Admin login required."}

    complaints = list(mongo_db["complaints"].find(
        {"assigned_department": department}, {"_id": 0}
    ))
    return complaints
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from services.auth_service import (
    register_user,
    login_user,
    login_gov_agent,
    login_contractor,
    login_inspection_officer,
)
from auth.jwt_handler import get_current_user, require_role


router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    full_name: str
    age: int
    caste: str
    state: str
    district: str
    aadhaar_number: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GovAgentLoginRequest(BaseModel):
    password: str


@router.post("/register")
def register(payload: RegisterRequest):
    try:
        user_id = register_user(payload.model_dump())

        return {
            "message": "Registration successful",
            "user_id": user_id,
        }

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
def login(payload: LoginRequest):
    try:
        return login_user(payload.email.lower(), payload.password)

    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    except Exception:
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/gov-agent-login")
def gov_login(payload: GovAgentLoginRequest):
    try:
        return login_gov_agent(payload.password)

    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/contractor-login")
def contractor_login(payload: LoginRequest):
    try:
        return login_contractor(payload.email.lower(), payload.password)

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/inspection-officer-login")
def inspection_officer_login(payload: LoginRequest):
    try:
        return login_inspection_officer(payload.email.lower(), payload.password)

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/citizen-only")
def citizen_only(current_user=Depends(require_role("CITIZEN"))):
    return {
        "message": "Citizen access granted",
        "user": current_user,
    }


@router.get("/gov-only")
def gov_only(current_user=Depends(require_role("GOV_AGENT"))):
    return {
        "message": "Government agent access granted",
        "user": current_user,
    }
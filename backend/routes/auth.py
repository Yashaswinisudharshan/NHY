from fastapi import APIRouter, Header
from services.auth import authenticate_user, create_access_token, verify_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    """
    Admin login endpoint.
    Returns a JWT token if credentials are correct.
    Frontend stores this token and sends it with admin requests.
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        return {"error": "Invalid username or password"}
    
    token = create_access_token(request.username)
    return {
        "token": token,
        "username": request.username,
        "role": "admin",
        "message": "Login successful"
    }

@router.get("/verify")
def verify(authorization: str = Header(None)):
    """
    Verifies if a token is still valid.
    Frontend calls this on page load to check if still logged in.
    """
    if not authorization:
        return {"valid": False}
    try:
        token = authorization.replace("Bearer ", "")
        username = verify_token(token)
        return {"valid": True, "username": username}
    except:
        return {"valid": False}
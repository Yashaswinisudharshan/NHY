from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = "govtai_secret_key_2025"  
# In production this would be in .env, for now hardcoded is fine

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hardcoded admin credentials
# In production these would be in a database
ADMIN_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": pwd_context.hash("admin123"),
        "role": "admin"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if the entered password matches the stored hash.
    We never store plain passwords — only bcrypt hashes.
    bcrypt is a one-way hash — you can't reverse it to get the original.
    """
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """
    Checks if username exists and password is correct.
    Returns user dict if valid, None if invalid.
    """
    user = ADMIN_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

def create_access_token(username: str) -> str:
    """
    Creates a JWT token for the logged-in admin.
    
    What is JWT?
    JSON Web Token — a signed string that proves who you are.
    It contains: username + expiry time, signed with SECRET_KEY.
    The frontend stores this and sends it with every admin request.
    Server verifies the signature to confirm it's genuine.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expire,
        "role": "admin"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    """
    Verifies the JWT token and returns the username.
    Raises exception if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token")
        return username
    except JWTError:
        raise ValueError("Invalid or expired token")
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.connection import get_db_cursor

security = HTTPBearer()


def _jwt_secret():
    secret = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is required")
    return secret


def _load_principal(user_id: int, role: str):
    table_by_role = {
        "CITIZEN": ("users", "user_id", "full_name", None),
        "CONTRACTOR": ("contractors", "contractor_id", "contractor_name", "approval_status"),
        "INSPECTION_OFFICER": ("inspection_officers", "officer_id", "officer_name", "approval_status"),
    }
    if role == "GOV_AGENT":
        return {"id": user_id, "full_name": "Government Agent", "role": role}
    if role not in table_by_role:
        raise HTTPException(status_code=401, detail="Invalid token role")

    table, id_col, name_col, status_col = table_by_role[role]
    status_select = f", {status_col}" if status_col else ""
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            f"SELECT {id_col} AS id, {name_col} AS full_name{status_select} FROM {table} WHERE {id_col} = %s",
            (user_id,),
        )
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    if status_col and row[status_col] != "APPROVED":
        raise HTTPException(status_code=403, detail="Account is not approved")
    return {"id": row["id"], "full_name": row["full_name"], "role": role}


def generate_token(user):
    now = datetime.now(timezone.utc)
    expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    user_id = user.get("id") or user.get("user_id") or user.get("govt_agent_id")

    if user_id is None:
        raise ValueError("User ID missing while generating token")

    payload = {
        "sub": str(user_id),
        "full_name": user.get("full_name") or user.get("name") or user.get("email"),
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(hours=expiration_hours),
    }

    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")




def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])

        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None or user_id == "None":
            raise HTTPException(status_code=401, detail="Invalid token: user id missing")

        return _load_principal(int(user_id), role)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_role: str):
    def checker(current_user=Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"{required_role} access required"
            )
        return current_user

    return checker
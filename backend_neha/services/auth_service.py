import os
from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_db_cursor
from auth.jwt_handler import generate_token
from dotenv import load_dotenv

load_dotenv()

def register_user(data):
    with get_db_cursor(dictionary=True) as (_, cursor):

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s OR aadhaar_number = %s
            """,
            (data["email"], data["aadhaar_number"]),
        )

        if cursor.fetchone():
            raise ValueError("User already exists")

        password_hash = generate_password_hash(data["password"])

        cursor.execute(
            """
            INSERT INTO users (
                full_name, age, caste, state, district,
                aadhaar_number, email, password_hash
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data["full_name"],
                data["age"],
                data["caste"],
                data["state"],
                data["district"],
                data["aadhaar_number"],
                data["email"],
                password_hash,
            ),
        )

        return cursor.lastrowid


def login_user(email, password):
    with get_db_cursor(dictionary=True) as (_, cursor):

        cursor.execute(
            """
            SELECT user_id, full_name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

        user = cursor.fetchone()

    if not user or not check_password_hash(
        user["password_hash"],
        password
    ):
        raise ValueError("Invalid email or password")

    token_user = {
        "id": user["user_id"],
        "full_name": user["full_name"],
        "role": "CITIZEN",
    }

    token = generate_token(token_user)

    return {
        "token": token,
        "user_id": user["user_id"],
        "full_name": user["full_name"],
        "role": "CITIZEN",
    }


def login_gov_agent(password):
    correct_password = os.getenv("GOV_AGENT_PASSWORD")

    if password != correct_password:
        raise ValueError("Invalid government agent password")

    gov_user = {
        "id": 1,
        "full_name": "Government Agent",
        "role": "GOV_AGENT",
    }

    token = generate_token(gov_user)

    return {
        "message": "Government agent login successful",
        "token": token,
        "role": "GOV_AGENT",
        "full_name": "Government Agent",
    }


def login_contractor(email, password):
    with get_db_cursor(dictionary=True) as (_, cursor):

        cursor.execute(
            """
            SELECT contractor_id,
                   contractor_name,
                   email,
                   password_hash,
                   approval_status
            FROM contractors
            WHERE email = %s
            """,
            (email,),
        )

        contractor = cursor.fetchone()

    if not contractor or not check_password_hash(
        contractor["password_hash"],
        password
    ):
        raise ValueError("Invalid email or password")

    if contractor["approval_status"] != "APPROVED":
        raise PermissionError(
            "Contractor account is not approved yet"
        )

    token_user = {
        "id": contractor["contractor_id"],
        "full_name": contractor["contractor_name"],
        "role": "CONTRACTOR",
    }

    token = generate_token(token_user)

    return {
        "token": token,
        "contractor_id": contractor["contractor_id"],
        "full_name": contractor["contractor_name"],
        "role": "CONTRACTOR",
    }


def login_inspection_officer(email, password):
    with get_db_cursor(dictionary=True) as (_, cursor):

        cursor.execute(
            """
            SELECT officer_id,
                   officer_name,
                   email,
                   password_hash,
                   approval_status
            FROM inspection_officers
            WHERE email = %s
            """,
            (email,),
        )

        officer = cursor.fetchone()

    if not officer or not check_password_hash(
        officer["password_hash"],
        password
    ):
        raise ValueError("Invalid email or password")

    if officer["approval_status"] != "APPROVED":
        raise PermissionError(
            "Inspection officer account is not approved yet"
        )

    token_user = {
        "id": officer["officer_id"],
        "full_name": officer["officer_name"],
        "role": "INSPECTION_OFFICER",
    }

    token = generate_token(token_user)

    return {
        "token": token,
        "officer_id": officer["officer_id"],
        "full_name": officer["officer_name"],
        "role": "INSPECTION_OFFICER",
    }
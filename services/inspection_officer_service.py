from mysql.connector import Error as MySQLError
from werkzeug.security import generate_password_hash

from database.connection import get_db_cursor
from services.contractor_service import ApprovalError


def create_inspection_officer(data):
    try:
        with get_db_cursor() as (_, cursor):
            cursor.execute(
                """
                INSERT INTO inspection_officers (officer_name, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (
                    data["officer_name"],
                    data["email"].lower(),
                    generate_password_hash(data["password"]),
                ),
            )
            return cursor.lastrowid
    except MySQLError as exc:
        if exc.errno == 1062:
            raise ValueError("Inspection officer email is already registered") from exc
        raise


def approve_inspection_officer(officer_id):
    return _update_officer_status(officer_id, "APPROVED")


def reject_inspection_officer(officer_id):
    return _update_officer_status(officer_id, "REJECTED")


def _update_officer_status(officer_id, status):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            "UPDATE inspection_officers SET approval_status = %s WHERE officer_id = %s",
            (status, officer_id),
        )
        if cursor.rowcount == 0:
            raise LookupError("Inspection officer not found")
    return get_inspection_officer_by_id(officer_id)



def get_inspection_officer_by_id(officer_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT officer_id, officer_name, email, approval_status, created_at
            FROM inspection_officers
            WHERE officer_id = %s
            """,
            (officer_id,),
        )
        return cursor.fetchone()


def get_pending_inspection_officers():
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT officer_id, officer_name, email, approval_status, created_at
            FROM inspection_officers
            WHERE approval_status = 'PENDING'
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()



from mysql.connector import Error as MySQLError
from werkzeug.security import generate_password_hash

from database.connection import get_db_cursor


class ApprovalError(Exception):
    pass


def create_contractor(data):
    try:
        with get_db_cursor() as (_, cursor):
            cursor.execute(
                """
                INSERT INTO contractors (
                    contractor_name, email, password_hash, previous_projects,
                    avg_delay_days, avg_budget_overrun, fraud_rate, blacklist_flag
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["contractor_name"],
                    data["email"].lower(),
                    generate_password_hash(data["password"]),
                    data.get("previous_projects", 0),
                    data.get("avg_delay_days", 0),
                    data.get("avg_budget_overrun", 0),
                    data.get("fraud_rate", 0),
                    data.get("blacklist_flag", 0),
                ),
            )
            contractor_id = cursor.lastrowid

            if contractor_id is None:
                raise RuntimeError("Failed to generate contractor ID")

            return contractor_id
    except MySQLError as exc:
        if exc.errno == 1062:
            raise ValueError("Contractor email is already registered") from exc
        raise


def approve_contractor(contractor_id):
    return _update_contractor_status(contractor_id, "APPROVED")


def reject_contractor(contractor_id):
    return _update_contractor_status(contractor_id, "REJECTED")


def _update_contractor_status(contractor_id, status):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            "UPDATE contractors SET approval_status = %s WHERE contractor_id = %s",
            (status, contractor_id),
        )
        if cursor.rowcount == 0:
            raise LookupError("Contractor not found")
    return get_contractor_by_id(contractor_id)




def get_contractor_by_id(contractor_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT contractor_id, contractor_name, email, previous_projects,
                   avg_delay_days, avg_budget_overrun, fraud_rate,
                   blacklist_flag, approval_status, created_at
            FROM contractors
            WHERE contractor_id = %s
            """,
            (contractor_id,),
        )
        return cursor.fetchone()


def get_pending_contractors():
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT contractor_id, contractor_name, email, previous_projects,
                   avg_delay_days, avg_budget_overrun, fraud_rate,
                   blacklist_flag, approval_status, created_at
            FROM contractors
            WHERE approval_status = 'PENDING'
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()

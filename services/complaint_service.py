from database.connection import get_db_cursor


def add_complaint(data, user_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO complaints (
                project_id, user_id, complaint_text, complaint_date, status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["project_id"],
                user_id,
                data["complaint_text"],
                data["complaint_date"],
                data.get("status", "OPEN"),
            ),
        )
        return cursor.lastrowid


def get_complaints_count(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            "SELECT COUNT(*) AS complaints_count FROM complaints WHERE project_id = %s",
            (project_id,),
        )
        row = cursor.fetchone() or {}
        return int(row.get("complaints_count") or 0)

from database.connection import get_db_cursor

def create_project(data):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO projects (
                project_name, project_type, department, state_name, district,
                budget, approved_work_quantity, expected_completion_days,
                contractor_id, officer_id, action_state, fraud_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
            """,
            (
                data["project_name"],
                data["project_type"],
                data["department"],
                data["state_name"],
                data["district"],
                data["budget"],
                data["approved_work_quantity"],
                data["expected_completion_days"],
                data.get("contractor_id"),
                data.get("officer_id"),
                data.get("action_state", "CREATED"),
            ),
        )
        return cursor.lastrowid


def get_project_by_id(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT project_id, project_name, project_type, department, state_name,
            district, budget, approved_work_quantity,
            expected_completion_days, contractor_id, officer_id, action_state,
            fraud_score, created_at
            FROM projects
            WHERE project_id = %s
            """,
            (project_id,),
        )
        return cursor.fetchone()



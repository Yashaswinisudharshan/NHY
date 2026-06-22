from database.connection import get_db_cursor

def _ensure_project_assigned_to_officer(project_id, officer_id):
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            "SELECT project_id FROM projects WHERE project_id = %s AND officer_id = %s",
            (project_id, officer_id),
        )
        if not cursor.fetchone():
            raise PermissionError("Officer is not assigned to this project")


        ...
def add_inspection(data, officer_id):
    _ensure_project_assigned_to_officer(data["project_id"], officer_id)
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO inspections (
                project_id, officer_id, inspection_date, verified_work_quantity,
                inspection_status, geo_tagged_proof_submitted, proof_document_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["project_id"],
                officer_id,
                data["inspection_date"],
                data["verified_work_quantity"],
                data.get("inspection_status", "PENDING"),
                data.get("geo_tagged_proof_submitted", 0),
                data.get("proof_document_count", 0),
            ),
        )
        return cursor.lastrowid

def get_invoices_for_officer(officer_id):
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            """
            SELECT i.*
            FROM invoices i
            JOIN projects p
                ON i.project_id = p.project_id
            WHERE p.officer_id = %s
            ORDER BY i.created_at DESC
            """,
            (officer_id,)
        )

        return cursor.fetchall()


def update_invoice_status(invoice_id, status, officer_id):
    allowed_status = ["APPROVED", "REJECTED"]

    if status not in allowed_status:
        raise ValueError("Status must be APPROVED or REJECTED")

    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            """
            UPDATE invoices i
            JOIN projects p
                ON i.project_id = p.project_id
            SET i.status = %s
            WHERE i.invoice_id = %s
              AND p.officer_id = %s
            """,
            (status, invoice_id, officer_id)
        )

        return cursor.rowcount > 0


def complete_inspection_if_no_pending_invoices(project_id, officer_id):
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE project_id = %s
              AND officer_id = %s
            """,
            (project_id, officer_id),
        )

        if not cursor.fetchone():
            raise LookupError("Project is not assigned to this inspection officer")

        cursor.execute(
            """
            SELECT COUNT(*) AS pending_invoice_count
            FROM invoices
            WHERE project_id = %s
              AND status = 'PENDING'
            """,
            (project_id,),
        )

        pending_invoice_count = int(
            (cursor.fetchone() or {}).get("pending_invoice_count") or 0
        )

        if pending_invoice_count > 0:
            return {
                "inspection_completed": False,
                "pending_invoice_count": pending_invoice_count,
                "message": "Inspection cannot be completed while invoices are pending",
            }

        cursor.execute(
            """
            UPDATE inspections
            SET inspection_status = 'COMPLETED'
            WHERE project_id = %s
              AND officer_id = %s
              AND inspection_status <> 'COMPLETED'
            """,
            (project_id, officer_id),
        )

        updated_count = cursor.rowcount

        if updated_count == 0:
            cursor.execute(
                """
                SELECT COUNT(*) AS inspection_count
                FROM inspections
                WHERE project_id = %s
                  AND officer_id = %s
                """,
                (project_id, officer_id),
            )

            inspection_count = int(
                (cursor.fetchone() or {}).get("inspection_count") or 0
            )

            if inspection_count == 0:
                raise LookupError("Inspection not found for this project and officer")

            return {
                "inspection_completed": True,
                "pending_invoice_count": 0,
                "updated_inspection_count": 0,
                "message": "Inspection was already completed",
            }
        
        return {
            "inspection_completed": True,
            "pending_invoice_count": 0,
            "updated_inspection_count": updated_count,
            "message": "Inspection marked as completed",
        }

def get_latest_inspection(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT inspection_status,
                   DATEDIFF(CURDATE(), inspection_date) AS last_inspection_days_ago,
                   geo_tagged_proof_submitted,
                   proof_document_count,
                   verified_work_quantity
            FROM inspections
            WHERE project_id = %s
            ORDER BY inspection_date DESC, inspection_id DESC
            LIMIT 1
            """,
            (project_id,),
        )
        inspection = cursor.fetchone()

    if not inspection:
        return {
            "inspection_status": "PENDING",
            "last_inspection_days_ago": None,
            "geo_tagged_proof_submitted": 0,
            "proof_document_count": 0,
            "verified_work_quantity": 0,
        }

    return {
        "inspection_status": inspection["inspection_status"],
        "last_inspection_days_ago": int(inspection["last_inspection_days_ago"] or 0),
        "geo_tagged_proof_submitted": int(
            inspection["geo_tagged_proof_submitted"] or 0
        ),
        "proof_document_count": int(inspection["proof_document_count"] or 0),
        "verified_work_quantity": float(inspection["verified_work_quantity"] or 0),
    }


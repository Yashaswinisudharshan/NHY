from database.connection import get_db_cursor


def add_invoice(data, contractor_id):
    _ensure_project_assigned_to_contractor(data["project_id"], contractor_id)
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO invoices (
                project_id, contractor_id, vendor_id, invoice_amount,
                invoice_date, work_quantity_claimed, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["project_id"],
                contractor_id,
                data["vendor_id"],
                data["invoice_amount"],
                data["invoice_date"],
                data["work_quantity_claimed"],
                data.get("status", "PENDING"),
            ),
        )
        return cursor.lastrowid


def _ensure_project_assigned_to_contractor(project_id, contractor_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT project_id
            FROM projects
            WHERE project_id = %s
              AND contractor_id = %s
            """,
            (project_id, contractor_id),
        )
        if not cursor.fetchone():
            raise PermissionError("Contractor is not assigned to this project")


def get_project_invoice_stats(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS invoice_count,
                COALESCE(AVG(invoice_amount), 0) AS average_invoice_amount,
                COALESCE(MAX(invoice_amount), 0) AS largest_invoice_amount,
                COUNT(DISTINCT DATE_FORMAT(invoice_date, '%Y-%m')) AS active_months
            FROM invoices
            WHERE project_id = %s
            """,
            (project_id,),
        )
        stats = cursor.fetchone() or {}

    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT COALESCE(MAX(vendor_invoice_count), 0) AS same_vendor_invoice_count
            FROM (
                SELECT COUNT(*) AS vendor_invoice_count
                FROM invoices
                WHERE project_id = %s
                GROUP BY vendor_id
            ) vendor_counts
            """,
            (project_id,),
        )
        vendor_stats = cursor.fetchone() or {}

    invoice_count = int(stats.get("invoice_count") or 0)
    active_months = int(stats.get("active_months") or 0)
    payment_frequency = invoice_count / active_months if active_months else 0

    return {
        "invoice_count": invoice_count,
        "average_invoice_amount": float(stats.get("average_invoice_amount") or 0),
        "largest_invoice_amount": float(stats.get("largest_invoice_amount") or 0),
        "same_vendor_invoice_count": int(
            vendor_stats.get("same_vendor_invoice_count") or 0
        ),
        "payment_frequency_per_month": round(payment_frequency, 2),
    }

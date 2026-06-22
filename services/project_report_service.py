from database.connection import get_db_cursor
from services.complaint_service import get_complaints_count
from services.inspection_service import get_latest_inspection
from services.invoice_service import get_project_invoice_stats


def submit_project_report(data):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO project_reports (
                project_id, amount_claimed, amount_released,
                work_completion_percent, claimed_work_quantity,
                actual_days_since_start, submitted_by, submission_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["project_id"],
                data["amount_claimed"],
                data["amount_released"],
                data["work_completion_percent"],
                data["claimed_work_quantity"],
                data["actual_days_since_start"],
                data["submitted_by"],
                data["submission_date"],
            ),
        )
        return cursor.lastrowid


def build_fraud_input_json(project_id):
    project = _get_project_with_contractor(project_id)
    if not project:
        raise LookupError("Project not found")

    report = _get_latest_project_report(project_id)
    if not report:
        raise LookupError("Project report not found")

    invoice_stats = get_project_invoice_stats(project_id)
    inspection = get_latest_inspection(project_id)
    complaints_count = get_complaints_count(project_id)

    fraud_input = {
        "project_id": int(project["project_id"]),
        "project_type": project["project_type"],
        "department": project["department"],
        "state": project["state_name"],
        "district": project["district"],
        "approved_budget": float(project["budget"] or 0),

        "amount_claimed": float(report["amount_claimed"] or 0),
        "amount_released": float(report["amount_released"] or 0),
        "work_completion_percent": float(report["work_completion_percent"] or 0),

        "expected_completion_days": int(project["expected_completion_days"] or 0),
        "actual_days_since_start": int(report["actual_days_since_start"] or 0),

        "invoice_count": int(invoice_stats["invoice_count"] or 0),
        "average_invoice_amount": float(invoice_stats["average_invoice_amount"] or 0),
        "largest_invoice_amount": float(invoice_stats["largest_invoice_amount"] or 0),
        "payment_frequency_per_month": float(invoice_stats["payment_frequency_per_month"] or 0),
        "same_vendor_invoice_count": int(invoice_stats["same_vendor_invoice_count"] or 0),

        "inspection_status": inspection["inspection_status"],
        "last_inspection_days_ago": int(inspection["last_inspection_days_ago"] or 0),
        "geo_tagged_proof_submitted": int(inspection["geo_tagged_proof_submitted"] or 0),
        "proof_document_count": int(inspection["proof_document_count"] or 0),

        "complaints_count": int(complaints_count or 0),

        "contractor_previous_projects": int(project["previous_projects"] or 0),
        "contractor_avg_delay_days": float(project["avg_delay_days"] or 0),
        "contractor_avg_budget_overrun": float(project["avg_budget_overrun"] or 0),
        "contractor_blacklist_flag": int(project["blacklist_flag"] or 0),

        "approved_work_quantity": float(project["approved_work_quantity"] or 0),
        "claimed_work_quantity": float(report["claimed_work_quantity"] or 0),
        "verified_work_quantity": float(inspection["verified_work_quantity"] or 0),
    }

    derived_fields = _calculate_derived_fields(fraud_input)
    fraud_input.update(derived_fields)

    return fraud_input


def _get_project_with_contractor(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT p.project_id, p.project_type, p.department, p.state_name,
                   p.district, p.budget, p.approved_work_quantity,
                   p.expected_completion_days, c.previous_projects,
                   c.avg_delay_days, c.avg_budget_overrun, c.blacklist_flag
            FROM projects p
            LEFT JOIN contractors c ON p.contractor_id = c.contractor_id
            WHERE p.project_id = %s
            """,
            (project_id,),
        )
        return cursor.fetchone()


def _get_latest_project_report(project_id):
    with get_db_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT amount_claimed, amount_released, work_completion_percent,
                   claimed_work_quantity, actual_days_since_start
            FROM project_reports
            WHERE project_id = %s
            ORDER BY submission_date DESC, report_id DESC
            LIMIT 1
            """,
            (project_id,),
        )
        return cursor.fetchone()


def _calculate_derived_fields(fraud_input):
    expected_days = fraud_input["expected_completion_days"]
    claimed_quantity = fraud_input["claimed_work_quantity"]
    approved_budget = fraud_input["approved_budget"]

    delay_ratio = (
        fraud_input["actual_days_since_start"] / expected_days if expected_days else 0
    )

    quantity_mismatch_ratio = (
        (claimed_quantity - fraud_input["verified_work_quantity"]) / claimed_quantity
        if claimed_quantity
        else 0
    )

    budget_claim_ratio = (
        fraud_input["amount_claimed"] / approved_budget if approved_budget else 0
    )

    work_money_gap = abs(
        budget_claim_ratio - (fraud_input["work_completion_percent"] / 100)
    )

    return {
        "delay_ratio": delay_ratio,
        "quantity_mismatch_ratio": quantity_mismatch_ratio,
        "budget_claim_ratio": budget_claim_ratio,
        "work_money_gap": work_money_gap,
    }
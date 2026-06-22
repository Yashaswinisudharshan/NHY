from datetime import date, datetime
import calendar
from database.connection import get_db_cursor

class OfficialReportNotFoundError(Exception):
    pass

def _month_value(report_month):
    if isinstance(report_month, datetime):
        return report_month.date()
    if isinstance(report_month, date):
        return report_month
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            parsed = datetime.strptime(report_month, fmt)
            return date(parsed.year, parsed.month, 1)
        except ValueError:
            pass
    raise ValueError("month must be YYYY-MM or YYYY-MM-DD")


def _month_range(report_month):
    d = _month_value(report_month)

    start_date = date(d.year, d.month, 1)
    last_day = calendar.monthrange(d.year, d.month)[1]
    end_date = date(d.year, d.month, last_day)

    return start_date, end_date


def _month_string(report_month):
    return _month_value(report_month).isoformat()


def _to_int(value):
    return int(value or 0)


def _risk_level_and_reason(
    reported_beneficiaries,
    actual_paid_beneficiaries,
    beneficiary_difference,
    reported_amount_spent,
    actual_amount_paid,
    amount_difference,
):
    if actual_amount_paid > reported_amount_spent:
        return "OVERPAYMENT", f"Actual amount paid is higher than reported amount by {abs(amount_difference)}."

    if actual_paid_beneficiaries > reported_beneficiaries:
        return "OVERPAYMENT", f"Actual paid beneficiaries are higher than reported beneficiaries by {abs(beneficiary_difference)}."

    if beneficiary_difference == 0 and amount_difference == 0:
        return "LOW", "Reported values match actual paid records."

    risk_level = "LOW"

    if beneficiary_difference > 0 or amount_difference > 0:
        risk_level = "MEDIUM"

    if reported_amount_spent > 0:
        difference_ratio = amount_difference / reported_amount_spent

        if difference_ratio > 0.25:
            risk_level = "CRITICAL"
        elif difference_ratio > 0.10:
            risk_level = "HIGH"

    reasons = []

    if beneficiary_difference > 0:
        reasons.append(
            f"Reported beneficiaries are higher than actual paid beneficiaries by {beneficiary_difference}."
        )

    if amount_difference > 0:
        reasons.append(
            f"Reported amount is higher than actual paid amount by {amount_difference}."
        )

    if not reasons:
        reasons.append("No positive mismatch detected.")

    return risk_level, " ".join(reasons)


def _build_result(report, payment_totals):
    reported_beneficiaries = _to_int(report["reported_beneficiaries"])
    reported_amount_spent = _to_int(report["reported_amount_spent"])

    actual_paid_beneficiaries = _to_int(payment_totals["actual_paid_beneficiaries"])
    actual_amount_paid = _to_int(payment_totals["actual_amount_paid"])

    beneficiary_difference = reported_beneficiaries - actual_paid_beneficiaries
    amount_difference = reported_amount_spent - actual_amount_paid

    risk_level, reason = _risk_level_and_reason(
        reported_beneficiaries,
        actual_paid_beneficiaries,
        beneficiary_difference,
        reported_amount_spent,
        actual_amount_paid,
        amount_difference,
    )

    return {
        "scheme_id": report["scheme_id"],
        "scheme_name": report["scheme_name"],
        "district": report["district"],
        "report_month": _month_string(report["report_month"]),
        "reported_beneficiaries": reported_beneficiaries,
        "actual_paid_beneficiaries": actual_paid_beneficiaries,
        "beneficiary_difference": beneficiary_difference,
        "reported_amount_spent": reported_amount_spent,
        "actual_amount_paid": actual_amount_paid,
        "amount_difference": amount_difference,
        "fraud_risk_level": risk_level,
        "fraud_reason": reason,
    }


def _fetch_official_report(scheme_id, district, report_month):
    start_date, end_date = _month_range(report_month)
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            """
            SELECT scheme_id, scheme_name, district, report_month,
                   reported_beneficiaries, reported_amount_spent
            FROM official_reports
            WHERE scheme_id = %s
              AND district = %s
              AND report_month BETWEEN %s AND %s
            """,
            (scheme_id, district, start_date, end_date),
        )
        return cursor.fetchone()


def _fetch_payment_totals(scheme_id, district, report_month):
    start_date, end_date = _month_range(report_month)

    with get_db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("""
            SELECT
                COUNT(DISTINCT beneficiary_id) AS actual_paid_beneficiaries,
                COALESCE(SUM(amount), 0) AS actual_amount_paid
            FROM payment_records
            WHERE scheme_id = %s
            AND district = %s
            AND payment_month BETWEEN %s AND %s
            AND payment_status = 'PAID'
        """, (scheme_id, district, start_date, end_date))

        totals = cursor.fetchone()

    return totals or {
        "actual_paid_beneficiaries": 0,
        "actual_amount_paid": 0
    }


def calculate_district_fraud(scheme_id, district, report_month):
    report = _fetch_official_report(scheme_id, district, report_month)

    if not report:
        raise OfficialReportNotFoundError("Official report does not exist")

    payment_totals = _fetch_payment_totals(scheme_id, district, report_month)

    result = _build_result(report, payment_totals)

    save_fraud_result(result)

    return result


def calculate_all_district_fraud(scheme_id, report_month):
    start_date, end_date = _month_range(report_month)

    with get_db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("""
            SELECT scheme_id, scheme_name, district, report_month,
                reported_beneficiaries, reported_amount_spent
            FROM official_reports
            WHERE scheme_id = %s
            AND report_month BETWEEN %s AND %s
            ORDER BY district ASC, scheme_name ASC
        """, (scheme_id, start_date, end_date))

        reports = cursor.fetchall()

    if not reports:
        raise OfficialReportNotFoundError(
            "No official reports found for this scheme and month"
        )

    results = []

    for report in reports:
        payment_totals = _fetch_payment_totals(
            report["scheme_id"],
            report["district"],
            report["report_month"]
        )

        result = _build_result(report, payment_totals)

        save_fraud_result(result)

        results.append(result)

    return results


def calculate_overall_fraud(scheme_id, report_month):
    start_date, end_date = _month_range(report_month)

    with get_db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("""
            SELECT
                COALESCE(SUM(reported_beneficiaries), 0) AS total_reported_beneficiaries,
                COALESCE(SUM(reported_amount_spent), 0) AS total_reported_amount_spent,
                COUNT(*) AS report_count
            FROM official_reports
            WHERE scheme_id = %s
            AND report_month BETWEEN %s AND %s
        """, (scheme_id, start_date, end_date))

        report_totals = cursor.fetchone()

    if not report_totals or _to_int(report_totals["report_count"]) == 0:
        raise OfficialReportNotFoundError(
            "No official reports found for this scheme and month"
        )

    with get_db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("""
            SELECT
                COUNT(DISTINCT beneficiary_id) AS total_actual_paid_beneficiaries,
                COALESCE(SUM(amount), 0) AS total_actual_amount_paid
            FROM payment_records
            WHERE scheme_id = %s
            AND payment_month BETWEEN %s AND %s
            AND payment_status = 'PAID'
        """, (scheme_id, start_date, end_date))

        payment_totals = cursor.fetchone() or {}

    total_reported_beneficiaries = _to_int(
        report_totals["total_reported_beneficiaries"]
    )

    total_reported_amount_spent = _to_int(
        report_totals["total_reported_amount_spent"]
    )

    total_actual_paid_beneficiaries = _to_int(
        payment_totals.get("total_actual_paid_beneficiaries")
    )

    total_actual_amount_paid = _to_int(
        payment_totals.get("total_actual_amount_paid")
    )

    total_beneficiary_difference = (
        total_reported_beneficiaries - total_actual_paid_beneficiaries
    )

    total_amount_difference = (
        total_reported_amount_spent - total_actual_amount_paid
    )

    risk_level, reason = _risk_level_and_reason(
        total_reported_beneficiaries,
        total_actual_paid_beneficiaries,
        total_beneficiary_difference,
        total_reported_amount_spent,
        total_actual_amount_paid,
        total_amount_difference,
    )

    return {
        "scheme_id": scheme_id,
        "report_month": start_date.isoformat(),
        "total_reported_beneficiaries": total_reported_beneficiaries,
        "total_actual_paid_beneficiaries": total_actual_paid_beneficiaries,
        "total_beneficiary_difference": total_beneficiary_difference,
        "total_reported_amount_spent": total_reported_amount_spent,
        "total_actual_amount_paid": total_actual_amount_paid,
        "total_amount_difference": total_amount_difference,
        "overall_scheme_fraud_risk_level": risk_level,
        "summary_reason": reason,
    }


def save_fraud_result(result):
    with get_db_cursor() as (conn, cursor):
        cursor.execute("""
            INSERT INTO fraud_results (
                scheme_id,
                scheme_name,
                district,
                report_month,
                reported_beneficiaries,
                actual_paid_beneficiaries,
                beneficiary_difference,
                reported_amount_spent,
                actual_amount_paid,
                amount_difference,
                fraud_risk_level,
                fraud_reason
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            result["scheme_id"],
            result["scheme_name"],
            result["district"],
            _month_value(result["report_month"]),
            result["reported_beneficiaries"],
            result["actual_paid_beneficiaries"],
            result["beneficiary_difference"],
            result["reported_amount_spent"],
            result["actual_amount_paid"],
            result["amount_difference"],
            result["fraud_risk_level"],
            result["fraud_reason"]
        ))

        fraud_id = cursor.lastrowid

    return fraud_id
import csv
import json
from database.connection import get_db_cursor
import re
import io
from datetime import datetime

def import_payment_csv(upload_file):
    payment_json = []

    text = upload_file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    insert_query = """
        INSERT INTO payment_records (
            scheme_id,
            beneficiary_id,
            state_name,
            district,
            payment_month,
            amount,
            payment_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    with get_db_cursor() as (_, cursor):
        for row in reader:
            payment_record = {
                "scheme_id": int(row["scheme_id"]),
                "beneficiary_id": row["beneficiary_id"],
                "state_name": row["state_name"],
                "district": row["district"],
                "payment_month": row["payment_month"],
                "amount": int(row["amount"]),
                "payment_status": row["payment_status"],
            }

            payment_json.append(payment_record)

            cursor.execute(
                insert_query,
                (
                    payment_record["scheme_id"],
                    payment_record["beneficiary_id"],
                    payment_record["state_name"],
                    payment_record["district"],
                    payment_record["payment_month"],
                    payment_record["amount"],
                    payment_record["payment_status"],
                ),
            )

    return payment_json


def _required_match(pattern, text, label, flags=0):
    match = re.search(pattern, text, flags)
    if not match:
        raise ValueError(f"Missing or invalid {label}")
    return match.group(1).strip()

def parse_report_text(upload_file):
    text = upload_file.file.read().decode("utf-8")
# Form of the report text for testing purposes

    """GOVERNMENT OF TELANGANA
    Department of Agriculture and Farmers Welfare

    MONTHLY IMPLEMENTATION REPORT

    Scheme Name: PM Kisan Samman Nidhi
    Scheme ID: 1

    District: Hyderabad

    Reporting Month: June 2025

    Summary:

    During June 2025, the PM Kisan Samman Nidhi scheme was successfully implemented across Hyderabad district. A total of 125000 eligible beneficiaries received financial assistance through Direct Benefit Transfer (DBT).

    The total amount spent under the scheme during the reporting period was Rs. 750000000.

    The payments were verified through district-level monitoring and beneficiary records maintained by the Department of Agriculture and Farmers Welfare.

    Submitted By:
    District Agriculture Officer, Hyderabad

    Submission Date:
    05 July 2025
    """

    scheme_name = _required_match(r"Scheme Name:\s*(.+)", text, "scheme name")
    scheme_id = int(_required_match(r"Scheme ID:\s*(\d+)", text, "scheme id"))
    district = _required_match(r"District:\s*(.+)", text, "district")
    month_text = _required_match(r"Reporting Month:\s*(.+)", text, "reporting month")
    report_month = datetime.strptime(month_text, "%B %Y").strftime("%Y-%m-01")

    beneficiaries = int(
        re.search(r"total of\s*(\d+)\s*eligible beneficiaries", text, re.IGNORECASE).group(1)
    )

    amount_spent = int(
        re.search(r"spent.*?Rs\.\s*(\d+)", text, re.IGNORECASE | re.DOTALL).group(1)
    )

    submitted_by = re.search(
        r"Submitted By:\s*\n(.+)", text, re.IGNORECASE
    ).group(1).strip()

    submitted_at_text = re.search(
        r"Submission Date:\s*\n(.+)", text, re.IGNORECASE
    ).group(1).strip()

    submitted_at = datetime.strptime(
        submitted_at_text, "%d %B %Y"
    ).strftime("%Y-%m-%d")

    report_json = {
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "district": district,
        "report_month": report_month,
        "reported_beneficiaries": beneficiaries,
        "reported_amount_spent": amount_spent,
        "submitted_by": submitted_by,
        "submitted_at": submitted_at
    }

    return report_json


def insert_official_report(report_data):
    query = """
    INSERT INTO official_reports (
        scheme_id,
        scheme_name,
        district,
        report_month,
        reported_beneficiaries,
        reported_amount_spent,
        submitted_by,
        submitted_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        report_data["scheme_id"],
        report_data["scheme_name"],
        report_data["district"],
        report_data["report_month"],
        report_data["reported_beneficiaries"],
        report_data["reported_amount_spent"],
        report_data["submitted_by"],
        report_data["submitted_at"]
    )

    with get_db_cursor() as (conn, cursor):
        cursor.execute(query, values)


def process_report_file(file_path):
    report_json = parse_report_text(file_path)

    print("Extracted JSON:")
    print(json.dumps(report_json, indent=4))

    insert_official_report(report_json)

    print("Report inserted successfully into official_reports table.")

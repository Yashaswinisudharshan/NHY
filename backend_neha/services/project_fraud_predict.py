import os
import pickle
import pandas as pd
from services.project_fraud_train import get_risk_level,get_rule_based_reasons
from services.project_report_service import build_fraud_input_json
from database.connection import get_db_cursor
from services.inspection_service import complete_inspection_if_no_pending_invoices
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_FILE = BASE_DIR / "models" / "fraud_model.pkl"

def predict_fraud(project_id):
    officer_id = get_project_officer_id(project_id)

    inspection_result = complete_inspection_if_no_pending_invoices(
        project_id,
        officer_id
    )
    input_data=build_fraud_input_json(project_id)
    with MODEL_FILE.open("rb") as file:
        trained_pipeline = pickle.load(file)

    input_row = pd.DataFrame([{k: v for k, v in input_data.items() if k != "project_id"}])
    fraud_probability = trained_pipeline.predict_proba(input_row)[0][1]
    fraud_score = round(float(fraud_probability), 4)
    update_fraud_results(project_id,fraud_score,input_data)
    return {
        "fraud_score": fraud_score,
        "risk_level": get_risk_level(fraud_score),
        "reasons": get_rule_based_reasons(input_data),
    }

def get_project_officer_id(project_id):
    with get_db_cursor(dictionary=True) as (_, cursor):
        cursor.execute(
            """
            SELECT officer_id
            FROM projects
            WHERE project_id = %s
            """,
            (project_id,),
        )

        project = cursor.fetchone()

        if not project:
            raise LookupError("Project not found")

        return project["officer_id"]

def update_fraud_results(project_id, fraud_score, input_data):
    with get_db_cursor() as (_, cursor):

        # Update project fraud score and mark project as done
        cursor.execute(
            """
            UPDATE projects
            SET fraud_score = %s,
                action_state = 'DONE'
            WHERE project_id = %s
            """,
            (
                fraud_score,
                project_id,
            ),
        )
        # Update contractor statistics
        cursor.execute(
            """
            UPDATE contractors c
            JOIN (
                SELECT
                    p.contractor_id,
                    COUNT(*) AS completed_projects,
                    AVG(GREATEST(r.actual_days_since_start - p.expected_completion_days, 0)) AS avg_delay_days,
                    AVG(pr.fraud_score) AS fraud_rate
                    FROM projects p
                    JOIN project_reports r ON r.project_id = p.project_id
                    JOIN projects pr ON pr.project_id = p.project_id
                    WHERE p.contractor_id = (
                        SELECT contractor_id FROM projects WHERE project_id = %s
                    )
                    AND p.fraud_score IS NOT NULL
                    GROUP BY p.contractor_id
                ) stats ON stats.contractor_id = c.contractor_id
                SET
                    c.previous_projects = stats.completed_projects,
                    c.avg_delay_days = stats.avg_delay_days,
                    c.fraud_rate = stats.fraud_rate,
                    c.blacklist_flag = CASE WHEN stats.fraud_rate >= 0.7 THEN 1 ELSE c.blacklist_flag END
            """,
            ( project_id,
            ),
        )


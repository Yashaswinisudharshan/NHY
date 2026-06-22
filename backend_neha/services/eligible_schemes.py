from database.connection import get_db_cursor


def get_eligible_schemes_for_user(user_id):
    with get_db_cursor(dictionary=True) as (_, cursor):

        cursor.execute(
            """
            SELECT age, caste, state, district
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )

        user = cursor.fetchone()

        if not user:
            return []

        cursor.execute(
            """
            SELECT scheme_name, money_per_person
            FROM schemes
            WHERE min_age <= %s
              AND (max_age IS NULL OR max_age >= %s)
              AND (LOWER(caste) = LOWER(%s) OR LOWER(caste) = 'all')
              AND (LOWER(state) = LOWER(%s) OR LOWER(state) = 'all')
              AND (LOWER(district) = LOWER(%s) OR LOWER(district) = 'all')
            """,
            (
                user["age"],
                user["age"],
                user["caste"],
                user["state"],
                user["district"],
            ),
        )

        return cursor.fetchall()
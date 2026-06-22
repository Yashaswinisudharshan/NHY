import mysql
from mysql.connector import Error as MySQLError
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nehavoma",        
    database="gov_projects"
    )   


PUBLIC_PROFILE_FIELDS = (
    "user_id",
    "full_name",
    "age",
    "caste",
    "state",
    "district",
    "aadhaar_number",
    "email",
)


def find_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT user_id, full_name, age, caste, state, district,
               aadhaar_number, email, password_hash
        FROM users
        WHERE email = %s
        """,
        (email,),
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def find_user_by_aadhaar(aadhaar_number):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id FROM users WHERE aadhaar_number = %s",
        (aadhaar_number,),
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def get_user_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT full_name, age, caste, state, district, email, aadhaar_number
        FROM users
        WHERE user_id = %s
        """,
        (user_id,),
    )

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return profile


def create_user(data):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (
                full_name, age, caste, state, district,
                aadhaar_number, email, password_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["full_name"],
                data["age"],
                data["caste"],
                data["state"],
                data["district"],
                data["aadhaar_number"],
                data["email"],
                data["password_hash"],
            ),
        )

        conn.commit()

        return cursor.lastrowid

    except MySQLError as exc:
        if conn:
            conn.rollback()

        if exc.errno == 1062:
            message = str(exc).lower()

            if "aadhaar" in message:
                raise ValueError("Aadhaar number is already registered") from exc

            if "email" in message:
                raise ValueError("Email address is already registered") from exc

            raise ValueError("User already exists") from exc

        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
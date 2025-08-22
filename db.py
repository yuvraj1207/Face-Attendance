# db.py
import mysql.connector
from mysql.connector import Error

# Update these to match your XAMPP/MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # default XAMPP user
    "password": "",         # empty if you didn’t set one
    "database": "faceapp",  # your database
}

def get_db_connection():
    """
    Returns a mysql.connector connection.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return None


def init_db():
    """
    Optional: Creates the 'users' table if not exists.
    Run this once at the start.
    """
    conn = get_db_connection()
    if not conn:
        print("[DB] Could not connect to DB to initialize table.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            encoding LONGBLOB NOT NULL
        )
        """)
        conn.commit()
        print("[DB] Users table ready.")
    except Error as e:
        print(f"[DB] init_db error: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_user(full_name, username, encoding_bytes):
    """
    Insert a new user with face encoding.
    encoding_bytes: bytes object
    """
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (full_name, username, encoding) VALUES (%s, %s, %s)",
            (full_name, username, encoding_bytes)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB] insert_user error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    """
    Returns a list of tuples: (full_name, username, encoding_bytes)
    """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_name, username, encoding FROM users")
        return cursor.fetchall()
    except Error as e:
        print(f"[DB] get_all_users error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

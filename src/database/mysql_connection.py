
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Find the project root and load its .env file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    """
    Establish and return a connection to the local MySQL database.
    """

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection


if __name__ == "__main__":

    conn = None

    try:
        conn = get_connection()

        print("Successfully connected to MySQL!")

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]

        print(f"Total customers: {customer_count}")

        cursor.close()

    except mysql.connector.Error as error:
        print("MySQL connection error:", error)

    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Connection closed.")


import json
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from mysql_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

TABLES = ["customers", "products", "orders"]


def json_serializer(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    raise TypeError(f"Type {type(value)} not serializable")


def extract_table(cursor, table_name):

    query = f"SELECT * FROM `{table_name}`"
    cursor.execute(query)

    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    records = [
        dict(zip(columns, row))
        for row in rows
    ]

    return records


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        for table in TABLES:

            records = extract_table(cursor, table)

            output_file = OUTPUT_DIR / f"{table}.json"

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(
                    records,
                    file,
                    indent=4,
                    default=json_serializer
                )

            print(f"{table}: {len(records)} records extracted")

        print("Initial extraction completed!")

    except Exception as error:
        print("Extraction failed:", error)
        raise

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()

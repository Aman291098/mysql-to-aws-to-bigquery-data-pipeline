
import json
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

from src.database.mysql_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SNAPSHOT_DIR = PROJECT_ROOT / "data" / "processed" / "snapshots"
EVENT_DIR = PROJECT_ROOT / "data" / "cdc" / "events"

TABLE_CONFIG = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id"
}


def normalize_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.isoformat()

    return value


def normalize_record(record):
    return {
        key: normalize_value(value)
        for key, value in record.items()
    }


def read_snapshot(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def fetch_current_data(connection, table_name):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"SELECT * FROM `{table_name}`")
        records = cursor.fetchall()

        return [
            normalize_record(record)
            for record in records
        ]

    finally:
        cursor.close()


def detect_changes(table_name, primary_key, old_records, new_records):

    old_data = {
        record[primary_key]: record
        for record in old_records
    }

    new_data = {
        record[primary_key]: record
        for record in new_records
    }

    events = []

    event_time = datetime.now(timezone.utc).isoformat()

    # Detect INSERT and UPDATE
    for record_id, new_record in new_data.items():

        if record_id not in old_data:
            operation = "INSERT"

        elif old_data[record_id] != new_record:
            operation = "UPDATE"

        else:
            continue

        events.append({
            "table": table_name,
            "operation": operation,
            "primary_key": record_id,
            "event_timestamp": event_time,
            "data": new_record
        })

    # Detect DELETE
    for record_id, old_record in old_data.items():

        if record_id not in new_data:

            events.append({
                "table": table_name,
                "operation": "DELETE",
                "primary_key": record_id,
                "event_timestamp": event_time,
                "data": old_record
            })

    return events


def save_snapshot(table_name, records):

    snapshot_file = SNAPSHOT_DIR / f"{table_name}.json"

    with open(snapshot_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, default=str)


def main():

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_DIR.mkdir(parents=True, exist_ok=True)

    connection = None
    pending_snapshots = {}
    all_events = []

    try:

        connection = get_connection()

        # Step 1: Read old snapshot and fetch current MySQL data
        for table_name, primary_key in TABLE_CONFIG.items():

            print(f"\nProcessing: {table_name}")

            snapshot_file = SNAPSHOT_DIR / f"{table_name}.json"

            if not snapshot_file.exists():
                raise FileNotFoundError(
                    f"Snapshot missing: {snapshot_file}. "
                    "Run create_snapshot.py first."
                )

            old_records = read_snapshot(snapshot_file)

            new_records = fetch_current_data(
                connection,
                table_name
            )

            # Step 2: Detect changes
            events = detect_changes(
                table_name,
                primary_key,
                old_records,
                new_records
            )

            all_events.extend(events)

            pending_snapshots[table_name] = new_records

            # Print operation counts
            for operation in ["INSERT", "UPDATE", "DELETE"]:

                count = sum(
                    event["operation"] == operation
                    for event in events
                )

                print(f"{operation}: {count}")

        # Step 3: Save events before updating snapshots
        if all_events:

            event_timestamp = datetime.now(timezone.utc).strftime(
                "%Y%m%d_%H%M%S_%f"
            )

            output_file = (
                EVENT_DIR / f"cdc_events_{event_timestamp}.json"
            )

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(all_events, file, indent=4, default=str)

            print(f"\nEvents saved: {output_file}")

        else:
            print("\nNo new changes detected.")

        # Step 4: Update snapshots only after event saving succeeds
        for table_name, records in pending_snapshots.items():
            save_snapshot(table_name, records)

        print("\nSnapshots updated successfully.")

        print(f"Total CDC events: {len(all_events)}")

    except Exception as error:

        print("\nCDC processing failed:", error)
        raise

    finally:

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()

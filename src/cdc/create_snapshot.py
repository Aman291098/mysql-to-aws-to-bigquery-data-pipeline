
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "processed" / "snapshots"

TABLES = ["customers", "products", "orders"]


def main():

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    for table in TABLES:

        source_file = RAW_DIR / f"{table}.json"
        snapshot_file = SNAPSHOT_DIR / f"{table}.json"

        if not source_file.exists():
            raise FileNotFoundError(
                f"Initial data not found: {source_file}"
            )

        shutil.copy2(source_file, snapshot_file)

        print(f"Snapshot created: {table}.json")

    print("\nInitial snapshots created successfully!")


if __name__ == "__main__":
    main()

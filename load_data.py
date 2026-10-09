import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "cell-count.csv"
DB_PATH = ROOT / "immune_response.db"
SCHEMA_PATH = ROOT / "schema.sql"

CELL_POPULATIONS = (
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
)


def initialize_database():
    if DB_PATH.exists():
        DB_PATH.unlink()

    schema = SCHEMA_PATH.read_text()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)


def load_data():
    seen_subjects = {}
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        with CSV_PATH.open(newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                subject_id = row["subject"]

                subject = (
                    row["project"],
                    row["condition"],
                    int(row["age"]),
                    row["sex"],
                    row["treatment"],
                    row["response"],
                )

                if subject_id not in seen_subjects:
                    connection.execute(
                        """
                        INSERT INTO subjects (subject_id, project, condition, age, sex, treatment, response)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (subject_id, *subject),
                    )
                    seen_subjects[subject_id] = subject

                elif seen_subjects[subject_id] != subject:
                    raise ValueError(
                        f"Inconsistent metadata for subject {subject_id}"
                    )

                connection.execute(
                    """
                    INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start)
                    VALUES (?, ?, ?, ?)
                    """,
                    (row["sample"], row["subject"], row["sample_type"], int(row["time_from_treatment_start"])),
                )

                connection.executemany(
                    """
                    INSERT INTO cell_counts (sample_id, population, count)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (row["sample"], population, int(row[population]))
                        for population in CELL_POPULATIONS
                    ],
                )


def main():
    initialize_database()
    load_data()


if __name__ == "__main__":
    main()

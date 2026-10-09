PRAGMA foreign_keys = ON;

CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    condition TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    sex TEXT NOT NULL,
    treatment TEXT NOT NULL,
    response TEXT
);

CREATE TABLE samples (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    sample_type TEXT NOT NULL,
    time_from_treatment_start INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

CREATE TABLE cell_counts (
    sample_id TEXT NOT NULL,
    population TEXT NOT NULL,
    count INTEGER NOT NULL CHECK (count >= 0),
    PRIMARY KEY (sample_id, population),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id) ON DELETE CASCADE
);

CREATE VIEW sample_frequencies AS
SELECT
    sample_id AS sample,
    SUM(count) OVER (PARTITION BY sample_id) AS total_count,
    population,
    count,
    100.0 * count / SUM(count) OVER (PARTITION BY sample_id) AS percentage
FROM cell_counts;

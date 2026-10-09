
# Immune Response Explorer

An interactive tool for exploring immune cell composition and treatment response in melanoma patients, developed for Loblaw Bio.
The application examines five immune cell populations across biological samples, compares miraclib responders and nonresponders, and supports cohort-level queries.

## Getting started

Requires Python 3.11+ and Make.

From the repository root:

```bash
make setup
make pipeline
make dashboard
```

| Command | What it does |
|---|---|
| `make setup` | Installs Python dependencies |
| `make pipeline` | Loads the CSV into SQLite and runs the analysis |
| `make dashboard` | Starts the Streamlit dashboard |
| `make test` | Runs the automated tests |

Run `make pipeline` before starting the dashboard. It generates `immune_response.db` from the included `cell-count.csv`.

### Dashboard

**Local URL:** [http://localhost:8501](http://localhost:8501)

In GitHub Codespaces, run `make dashboard`, then open port **8501** using the **Ports** tab or the forwarded-port notification.

## Database design

The SQLite database uses three related tables:

- **`subjects`** stores patient metadata, including condition, treatment, and response.
- **`samples`** stores each biological sample and its collection time.
- **`cell_counts`** stores the five immune population counts per sample.

Separating these entities avoids repeating patient information across samples and allows queries at both the subject and sample levels.

The `sample_frequencies` SQL view calculates each population's percentage of the total measured cells in its sample. These values are derived when queried rather than stored separately.

## Analysis and application

`load_data.py` handles CSV ingestion and database initialization. `analysis.py` contains the cohort queries and statistical comparisons.

For response analysis, baseline groups are compared using Welch's t-test, with Cohen's d reporting effect size and Benjamini–Hochberg correction accounting for multiple comparisons. Follow-up analysis compares each patient's Day 7 and Day 14 measurements with their own baseline.

The Streamlit dashboard organizes the results into three views:

- **Overview:** individual sample composition and relative frequencies.
- **Response Analysis:** baseline and longitudinal responder comparisons.
- **Cohort Explorer:** baseline cohort records, demographic breakdowns, and a separate B-cell query.

Charts and shared interface components are organized under `app/`. Tests are located in `tests/`.

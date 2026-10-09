import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "immune_response.db"


def get_miraclib_response_cohort():
    query = """
        SELECT
            s.sample_id,
            s.subject_id,
            s.time_from_treatment_start AS day,
            sub.response,
            f.population,
            f.count,
            f.percentage
        FROM samples s
        JOIN subjects sub
            ON sub.subject_id = s.subject_id
        JOIN sample_frequencies f
            ON f.sample = s.sample_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND sub.response IN ('yes', 'no')
        ORDER BY
            s.subject_id,
            s.time_from_treatment_start,
            f.population
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def summarize_baseline(cohort):
    baseline = cohort[cohort["day"] == 0]
    summary = (
        baseline
        .groupby(["population", "response"])["percentage"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
            skew="skew",
        )
        .round(2)
    )
    return summary


def cohens_d(group_a, group_b):
    n_a = len(group_a)
    n_b = len(group_b)
    pooled_std = np.sqrt(
        (
            (n_a - 1) * group_a.var(ddof=1)
            + (n_b - 1) * group_b.var(ddof=1)
        )
        / (n_a + n_b - 2)
    )
    return (group_a.mean() - group_b.mean()) / pooled_std


def compare_baseline_response(cohort):
    baseline = cohort[cohort["day"] == 0]
    results = []
    for population, group in baseline.groupby("population"):
        responders = group.loc[
            group["response"] == "yes", "percentage"
        ]
        nonresponders = group.loc[
            group["response"] == "no", "percentage"
        ]
        statistic, p_value = ttest_ind(
            responders,
            nonresponders,
            equal_var=False,
        )
        results.append(
            {
                "population": population,
                "responder_mean": responders.mean(),
                "nonresponder_mean": nonresponders.mean(),
                "difference": responders.mean() - nonresponders.mean(),
                "effect_size": cohens_d(responders, nonresponders),
                "statistic": statistic,
                "p_value": p_value,
            }
        )

    results = pd.DataFrame(results)
    results["adjusted_p_value"] = multipletests(
        results["p_value"],
        method="fdr_bh",
    )[1]
    results["significant"] = results["adjusted_p_value"] < 0.05

    return results


def compare_changes_from_baseline(cohort):
    changes = (
        cohort
        .pivot(
            index=["subject_id", "response", "population"],
            columns="day",
            values="percentage",
        )
        .reset_index()
    )

    changes["day_7_change"] = changes[7] - changes[0]
    changes["day_14_change"] = changes[14] - changes[0]
    results = []

    for population, group in changes.groupby("population"):
        for day in (7, 14):
            column = f"day_{day}_change"

            responders = group.loc[
                group["response"] == "yes", column
            ]

            nonresponders = group.loc[
                group["response"] == "no", column
            ]

            statistic, p_value = ttest_ind(
                responders,
                nonresponders,
                equal_var=False,
            )

            results.append(
                {
                    "population": population,
                    "day": day,
                    "responder_change": responders.mean(),
                    "nonresponder_change": nonresponders.mean(),
                    "difference": responders.mean() - nonresponders.mean(),
                    "effect_size": cohens_d(responders, nonresponders),
                    "p_value": p_value,
                }
            )

    results = pd.DataFrame(results)
    results["adjusted_p_value"] = multipletests(
        results["p_value"],
        method="fdr_bh",
    )[1]
    results["significant"] = results["adjusted_p_value"] < 0.05

    return results


def get_baseline_cohort_breakdown():
    query = """
        WITH baseline_cohort AS (
            SELECT
                sub.subject_id,
                sub.project,
                sub.response,
                sub.sex,
                s.sample_id
            FROM subjects sub
            JOIN samples s
                ON s.subject_id = sub.subject_id
            WHERE sub.condition = 'melanoma'
              AND sub.treatment = 'miraclib'
              AND s.sample_type = 'PBMC'
              AND s.time_from_treatment_start = 0
        )
        SELECT
            'project' AS breakdown,
            project AS category,
            COUNT(DISTINCT sample_id) AS count
        FROM baseline_cohort
        GROUP BY project

        UNION ALL

        SELECT
            'response',
            response,
            COUNT(DISTINCT subject_id)
        FROM baseline_cohort
        GROUP BY response

        UNION ALL

        SELECT
            'sex',
            sex,
            COUNT(DISTINCT subject_id)
        FROM baseline_cohort
        GROUP BY sex
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def get_responder_b_cell_average():
    query = """
        SELECT
            ROUND(AVG(cc.count), 2) AS average_b_cells
        FROM subjects sub
        JOIN samples s
            ON s.subject_id = sub.subject_id
        JOIN cell_counts cc
            ON cc.sample_id = s.sample_id
        WHERE sub.condition = 'melanoma'
          AND sub.sex = 'M'
          AND sub.response = 'yes'
          AND s.time_from_treatment_start = 0
          AND cc.population = 'b_cell'
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def get_baseline_miraclib_samples():
    query = """
        SELECT
            s.sample_id AS sample,
            sub.subject_id AS subject,
            sub.project,
            sub.response,
            sub.sex
        FROM subjects sub
        JOIN samples s
            ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND s.time_from_treatment_start = 0
        ORDER BY
            sub.project,
            sub.subject_id
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def main():
    cohort = get_miraclib_response_cohort()
    print(f"\nRows: {len(cohort):,}")
    print(f"Subjects: {cohort['subject_id'].nunique():,}")

    print("\nBaseline distributions:")
    print(summarize_baseline(cohort))

    print("\nBaseline response comparison:")
    print(compare_baseline_response(cohort).round(4).to_string(index=False))

    print("\nChange from baseline:")
    print(compare_changes_from_baseline(cohort).round(4).to_string(index=False))

    print("\nBaseline cohort breakdown:")
    print(get_baseline_cohort_breakdown().to_string(index=False))

    print("\nAverage B-cell count:")
    print(get_responder_b_cell_average().to_string(index=False))


if __name__ == "__main__":
    main()

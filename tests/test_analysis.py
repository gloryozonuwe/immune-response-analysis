import pytest
from analysis import (
    get_baseline_cohort_breakdown,
    get_baseline_miraclib_samples,
    get_miraclib_response_cohort,
    get_responder_b_cell_average,
)


def test_baseline_cohort():
    samples = get_baseline_miraclib_samples()
    assert len(samples) == 656
    assert samples["sample"].is_unique
    assert samples["subject"].nunique() == 656


def test_baseline_cohort_breakdown():
    breakdown = get_baseline_cohort_breakdown()
    expected = {
        ("project", "prj1"): 384,
        ("project", "prj3"): 272,
        ("response", "yes"): 331,
        ("response", "no"): 325,
        ("sex", "M"): 344,
        ("sex", "F"): 312,
    }

    actual = {
        (row.breakdown, row.category): row.count
        for row in breakdown.itertuples(index=False)
    }
    assert actual == expected


def test_response_cohort_has_complete_timepoints():
    cohort = get_miraclib_response_cohort()
    assert cohort["subject_id"].nunique() == 656
    assert len(cohort) == 656 * 3 * 5

    observations = cohort.groupby(
        ["subject_id", "population"]
    )["day"].agg(lambda days: set(days))

    assert all(days == {0, 7, 14} for days in observations)


def test_responder_b_cell_average():
    result = get_responder_b_cell_average()
    average = result.loc[0, "average_b_cells"]
    assert average == pytest.approx(10206.15)

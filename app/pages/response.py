import streamlit as st

from analysis import (
    compare_baseline_response,
    compare_changes_from_baseline,
    get_miraclib_response_cohort,
)
from app.charts import (
    longitudinal_change_chart,
    response_boxplots,
)
from app.components import (
    render_header,
    render_response_finding,
    render_section_intro,
    render_statistics_table,
    render_effect_size_explainer,
    render_subsection,
    render_longitudinal_finding,
    render_longitudinal_table,
)


def render_response():
    render_header(active="Response Analysis")
    render_section_intro(
        number="02",
        label="Response",
        title="Immune composition<br>and treatment response",
        description=(
            "Baseline PBMC samples from melanoma patients receiving miraclib are compared between responders and nonresponders. Baseline is "
            "shown first because it is the clinically relevant timepoint for evaluating whether immune composition may help predict response."
        ),
    )
    cohort = get_miraclib_response_cohort()
    baseline_results = compare_baseline_response(cohort)
    response_figure = response_boxplots(
        cohort,
        day=0,
    )
    st.plotly_chart(
        response_figure,
        width="stretch",
        config={"displayModeBar": False},
    )
    render_response_finding(baseline_results)
    render_statistics_table(baseline_results)
    render_effect_size_explainer()
    render_subsection(
        label="Longitudinal",
        title="Change after treatment",
        description=(
            "For each patient, Day 7 and Day 14 immune frequencies are compared with that patient's own baseline. This preserves the "
            "repeated-measures structure rather than treating follow-up samples as independent observations."
        ),
    )
    change_results = compare_changes_from_baseline(cohort)
    change_figure = longitudinal_change_chart(cohort)
    st.plotly_chart(
        change_figure,
        width="stretch",
        config={"displayModeBar": False},
    )
    render_longitudinal_finding()
    render_longitudinal_table(change_results)

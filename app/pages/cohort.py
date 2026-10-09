import streamlit as st

from analysis import (
    get_baseline_cohort_breakdown,
    get_baseline_miraclib_samples,
    get_responder_b_cell_average,
)
from app.charts import (
    cohort_breakdown_chart,
)
from app.components import (
    render_cohort_definition,
    render_cohort_insight,
    render_header,
    render_subsection,
    render_section_intro,
)


def render_cohort():
    render_header(active="Cohort Explorer")
    render_section_intro(
        number="03",
        label="Cohort Explorer",
        title="Who is represented<br>in the analysis?",
        description=(
            "Explore the baseline melanoma cohort treated with miraclib, see how patients are distributed across projects, response,"
            "and sex, and examine a broader B-cell insight."
        ),
    )
    cohort = get_baseline_miraclib_samples()
    breakdown = get_baseline_cohort_breakdown()
    b_cell_average = get_responder_b_cell_average()
    render_cohort_definition(len(cohort))
    st.dataframe(
        cohort.style.set_properties(**{'background-color': '#1e1e1e', 'color': '#ffffff'}),
        width="stretch",
        hide_index=True,
    )
    render_subsection(
        label="Cohort breakdown",
        title="Composition of the baseline cohort",
        description=(
            "The 656 matching baseline samples span two projects. Response and sex counts describe the distinct subjects "
            "represented in this cohort."
        ),
    )
    breakdown_figure = cohort_breakdown_chart(breakdown)
    st.plotly_chart(
        breakdown_figure,
        width="stretch",
        config={"displayModeBar": False},
    )
    average = b_cell_average.loc[0, "average_b_cells"]
    render_cohort_insight(average)

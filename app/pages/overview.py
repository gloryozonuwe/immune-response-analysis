from pathlib import Path
import streamlit as st

from app.charts import (
    sample_composition_chart,
)
from app.components import (
    render_composition_table,
    render_header,
    render_hero,
    render_sample_context,
    render_section_intro,
    sample_search,
)
from app.data import (
    get_sample,
    get_sample_composition
)

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "cell-count.csv"


def render_overview():
    render_header(active="Overview")
    render_hero()
    st.html(
        '<div class="dataset-action">'
        'Source data · 10,500 biological samples'
        '</div>'
    )
    with CSV_PATH.open("rb") as file:
        st.download_button(
            "Download source dataset ↓",
            data=file,
            file_name="cell-count.csv",
            mime="text/csv",
        )

    render_section_intro(
        number="01",
        label="Composition",
        title="Immune composition<br>across samples",
        description=(
            "Each biological sample contains counts for five immune cell populations. Converting those counts to relative frequencies "
            "lets us compare composition between samples even when total measured cell counts differ."
        ),
    )
    sample_id = sample_search()
    sample = get_sample(sample_id)
    composition = get_sample_composition(sample_id)
    render_sample_context(sample, composition)
    figure = sample_composition_chart(composition)
    st.plotly_chart(
        figure,
        width="stretch",
        config={"displayModeBar": False},
    )
    render_composition_table(composition)

from pathlib import Path
import streamlit as st
from app.components import load_styles
from app.pages.cohort import render_cohort
from app.pages.overview import render_overview
from app.pages.response import render_response

ROOT = Path(__file__).resolve().parent
CSS_PATH = ROOT / "styles.css"
PAGES = {
    "response": render_response,
    "cohort": render_cohort,
}


def main():
    st.set_page_config(
        page_title="Immune Response Explorer | Loblaw Bio",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    load_styles(CSS_PATH)

    page = st.query_params.get("page")

    if page is None:
        render_overview()
        return

    if page not in PAGES:
        st.query_params.clear()
        st.rerun()

    PAGES[page]()


if __name__ == "__main__":
    main()

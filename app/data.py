import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "immune_response.db"


@st.cache_data
def get_sample(sample_id):
    query = """
        SELECT
            s.sample_id,
            sub.condition,
            s.sample_type,
            s.time_from_treatment_start AS day
        FROM samples s
        JOIN subjects sub
            ON sub.subject_id = s.subject_id
        WHERE s.sample_id = ?
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(sample_id,),
        )


@st.cache_data
def get_sample_composition(sample_id):
    query = """
        SELECT
            sample,
            total_count,
            population,
            count,
            percentage
        FROM sample_frequencies
        WHERE sample = ?
        ORDER BY
            CASE population
                WHEN 'b_cell' THEN 1
                WHEN 'cd4_t_cell' THEN 2
                WHEN 'cd8_t_cell' THEN 3
                WHEN 'monocyte' THEN 4
                WHEN 'nk_cell' THEN 5
            END
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(sample_id,),
        )


@st.cache_data
def sample_exists(sample_id):
    query = """
        SELECT 1
        FROM samples
        WHERE sample_id = ?
        LIMIT 1
    """

    with sqlite3.connect(DB_PATH) as connection:
        result = connection.execute(
            query,
            (sample_id,),
        ).fetchone()

    return result is not None

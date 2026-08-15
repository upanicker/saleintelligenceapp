"""Data ingestion tab."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import data_warnings, read_csv


def render(sample_path: Path) -> pd.DataFrame:
    st.markdown("### Data ingestion")
    st.caption("Upload and validate your opportunity CSV. The active data powers the other two tabs.")
    uploaded = st.file_uploader("Upload opportunity CSV", type=["csv"])
    if uploaded is not None:
        try:
            data, missing = read_csv(uploaded)
        except (UnicodeDecodeError, pd.errors.ParserError) as error:
            st.error(f"This file could not be read as a CSV: {error}")
            data, missing = None, []
        if missing:
            st.error("Missing required columns: " + ", ".join(missing))
        elif data is not None:
            st.session_state["opportunity_data"] = data
            st.success(f"Loaded {uploaded.name}: {len(data):,} opportunities ready for analysis.")

    if "opportunity_data" not in st.session_state:
        data, missing = read_csv(sample_path)
        if missing or data is None:  # Guard for an accidentally changed bundled file.
            st.error("The bundled sample data is invalid.")
            st.stop()
        st.session_state["opportunity_data"] = data
        st.info("Using the bundled sample data until you upload a CSV.")

    data = st.session_state["opportunity_data"]
    one, two, three = st.columns(3)
    one.metric("Records ready", f"{len(data):,}")
    two.metric("Columns detected", f"{len(data.columns):,}")
    three.metric("Required fields", "Validated")
    for warning in data_warnings(data):
        st.warning(warning)
    with st.expander("Preview imported data"):
        st.dataframe(data.head(15), width="stretch", hide_index=True)
    return data

"""Streamlit Sales Intelligence application."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.settings import CURRENCY_CACHE_TTL_SECONDS
from src.components import exploration, ingestion, intelligence
from src.currency import get_usd_to_inr_rate


APP_DIR = Path(__file__).parent
SAMPLE_DATA = APP_DIR / "sales_opportunities_sample.csv"

st.set_page_config(page_title="Sales Intelligence", page_icon="📈", layout="wide")


@st.cache_data(ttl=CURRENCY_CACHE_TTL_SECONDS, show_spinner=False)
def cached_exchange_rate() -> tuple[float, str, str]:
    return get_usd_to_inr_rate()


def main() -> None:
    st.title("Sales Intelligence")
    st.caption("From opportunity data to an executive decision view.")
    rate, rate_date, rate_source = cached_exchange_rate()
    with st.sidebar:
        st.header("Display settings")
        currency = st.radio("Currency", ["USD", "INR"], horizontal=True)
        if st.button("Refresh USD → INR rate"):
            cached_exchange_rate.clear()
            st.rerun()
        st.caption(f"{rate_source} · 1 USD = ₹{rate:,.2f} · {rate_date}")
        st.divider()
        st.caption("Currency conversion affects displayed values only; source calculations stay in USD.")
    ingestion_tab, exploration_tab, intelligence_tab = st.tabs(["1 · Data ingestion", "2 · Data exploration", "3 · Decision making"])
    with ingestion_tab:
        data = ingestion.render(SAMPLE_DATA)
    active_data = st.session_state.get("opportunity_data", data)
    with exploration_tab:
        exploration.render(active_data, currency, rate)
    with intelligence_tab:
        intelligence.render(active_data, currency, rate)


if __name__ == "__main__":
    main()

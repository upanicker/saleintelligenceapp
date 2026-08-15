"""Interactive opportunity exploration tab."""

from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from config.settings import DEFAULT_LARGE_DEAL_THRESHOLD_USD
from src.formatters import currency_column, currency_label, money
from src.metrics import filtered_data


FILTER_COLUMNS = {
    "Region": "Region", "Country": "Country", "Stage": "Stage", "Sales rep": "Sales Rep",
    "Product": "Product", "Industry": "Industry", "Close quarter": "Close Quarter",
}


def _filter_controls(data: pd.DataFrame) -> tuple[dict[str, list[str]], str, float]:
    st.markdown("#### Find opportunities")
    search = st.text_input("Search opportunity or account", placeholder="Search by opportunity or account")
    selections: dict[str, list[str]] = {}
    columns = st.columns(4)
    for index, (label, field) in enumerate(FILTER_COLUMNS.items()):
        with columns[index % 4]:
            values = sorted(data[field].dropna().astype(str).unique().tolist())
            selections[field] = st.multiselect(label, values, default=values, key=f"filter_{field}")
    threshold = st.number_input(
        "Large opportunity threshold (USD)", min_value=0.0,
        value=DEFAULT_LARGE_DEAL_THRESHOLD_USD, step=5_000.0,
    )
    return selections, search, threshold


def _detail_panel(opportunity: pd.Series, currency: str, rate: float) -> None:
    st.markdown("#### Opportunity detail")
    left, right = st.columns(2)
    with left:
        st.subheader(opportunity["Opportunity Name"])
        st.caption(f"{opportunity['Opportunity ID']} · {opportunity['Account']}")
        st.metric("Amount", money(float(opportunity["Amount ($)"]), currency, rate))
        st.write(f"**Stage:** {opportunity['Stage']}")
        st.write(f"**Probability:** {opportunity['Probability']:.0%}")
        st.write(f"**Close quarter:** {opportunity['Close Quarter']}")
    with right:
        st.write(f"**Sales rep:** {opportunity['Sales Rep']}")
        st.write(f"**Region:** {opportunity['Region']}")
        st.write(f"**Product:** {opportunity['Product']}")
        st.write(f"**Industry:** {opportunity['Industry']}")
        st.write(f"**Opportunity type:** {opportunity.get('Opportunity Type', '—')}")
    timeline = pd.DataFrame({
        "Milestone": ["Created", "Expected close"],
        "Date": [opportunity.get("Created Date"), opportunity.get("Close Date")],
    })
    st.caption("Key timeline")
    st.dataframe(timeline, width="stretch", hide_index=True)


def render(data: pd.DataFrame, currency: str, rate: float) -> None:
    st.markdown("### Data exploration")
    st.caption("Filter, search, sort, page through, and inspect opportunities.")
    selections, search, threshold = _filter_controls(data)
    filtered = filtered_data(data, selections, search)
    amount_display = currency_column(filtered["Amount ($)"], currency, rate)
    weighted_display = currency_column(filtered["Weighted Pipeline ($)"], currency, rate)
    total = float(amount_display.sum())
    weighted = float(weighted_display.sum())
    average = total / len(filtered) if len(filtered) else 0.0
    metrics = st.columns(4)
    metrics[0].metric("Total opportunities", f"{len(filtered):,}")
    metrics[1].metric("Pipeline value", money(float(filtered['Amount ($)'].sum()), currency, rate))
    metrics[2].metric("Weighted pipeline", money(float(filtered['Weighted Pipeline ($)'].sum()), currency, rate))
    average_text = f"₹{average:,.0f}" if currency == "INR" else f"${average:,.0f}"
    metrics[3].metric("Average deal size", average_text)
    if filtered.empty:
        st.warning("No opportunities match the selected filters.")
        return

    st.markdown("#### Opportunities")
    sortable = filtered.copy()
    display_amount_column = currency_label(currency)
    sortable[display_amount_column] = amount_display
    sort_options = ["Opportunity Name", "Account", "Region", "Country", "Stage", display_amount_column, "Probability", "Close Date", "Sales Rep", "Product", "Industry", "Close Quarter"]
    controls = st.columns(3)
    sort_by = controls[0].selectbox("Sort by", sort_options, index=sort_options.index(display_amount_column))
    descending = controls[1].toggle("Descending", value=True)
    page_size = controls[2].selectbox("Rows per page", [10, 25, 50, 100], index=1)
    sorted_data = sortable.sort_values(sort_by, ascending=not descending, na_position="last")
    total_pages = max(1, math.ceil(len(sorted_data) / page_size))
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * page_size
    page_data = sorted_data.iloc[start:start + page_size].copy()
    page_data["Large opportunity"] = page_data["Amount ($)"] >= threshold
    columns = ["Opportunity Name", "Account", "Region", "Country", "Stage", display_amount_column, "Probability", "Close Quarter", "Sales Rep", "Product", "Industry", "Large opportunity"]
    shown = page_data[columns]
    styled = shown.style.map(
        lambda is_large: "background-color: #fff3cd; font-weight: 700" if is_large else "",
        subset=["Large opportunity"],
    ).format({display_amount_column: ("₹{:,.0f}" if currency == "INR" else "${:,.0f}"), "Probability": "{:.0%}"})
    event = st.dataframe(styled, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")
    st.caption(f"Showing {len(page_data):,} of {len(filtered):,} opportunities · Page {page} of {total_pages}. Highlighted rows meet the large-deal threshold.")
    selected_rows = event.selection.rows if hasattr(event, "selection") else []
    if selected_rows:
        st.session_state["selected_opportunity_id"] = page_data.iloc[selected_rows[0]]["Opportunity ID"]
    selected_id = st.session_state.get("selected_opportunity_id", page_data.iloc[0]["Opportunity ID"])
    chosen = filtered.loc[filtered["Opportunity ID"].eq(selected_id)]
    if chosen.empty:
        chosen = page_data.iloc[[0]]
    _detail_panel(chosen.iloc[0], currency, rate)

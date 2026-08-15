"""Decision-making dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import DEFAULT_REVENUE_TARGET_USD, OPEN_STAGES
from src.formatters import money
from src.metrics import executive_metrics, region_performance


def _bar(data: pd.DataFrame, x: str, y: str, title: str, color: str):
    figure = px.bar(data, x=x, y=y, title=title, color_discrete_sequence=[color])
    figure.update_layout(showlegend=False, margin=dict(l=8, r=8, t=46, b=8), height=320)
    return figure


def render(data: pd.DataFrame, currency: str, rate: float) -> None:
    st.markdown("### Sales intelligence dashboard")
    st.caption("Executive pipeline health, source of business, and conversion signals.")
    target_default = DEFAULT_REVENUE_TARGET_USD * (rate if currency == "INR" else 1)
    target = st.number_input(
        f"Revenue target ({currency}) for pipeline coverage", min_value=1.0,
        value=float(target_default), step=50_000.0,
    )
    target_usd = target / rate if currency == "INR" else target
    stats = executive_metrics(data, target_usd)
    scorecards = st.columns(6)
    values = [
        money(stats["total_pipeline"], currency, rate), money(stats["weighted_pipeline"], currency, rate),
        money(stats["won_revenue"], currency, rate), f"{stats['win_rate']:.0%}",
        money(stats["average_deal"], currency, rate), f"{stats['pipeline_coverage']:.1f}×",
    ]
    for card, label, value in zip(scorecards, ["Total pipeline", "Weighted pipeline", "Won revenue", "Win rate", "Average deal size", "Pipeline coverage"], values):
        card.metric(label, value)

    region = region_performance(data)
    region["Display Pipeline"] = region["Pipeline"] * (rate if currency == "INR" else 1)
    region_label = f"Pipeline ({currency})"
    left, right = st.columns([1.2, 1])
    with left:
        st.plotly_chart(_bar(region.sort_values("Display Pipeline"), "Display Pipeline", "Region", "Pipeline by region", "#2563eb"), width="stretch")
    with right:
        st.markdown("#### Region performance")
        table = region[["Region", "Opportunities", "Display Pipeline", "Win Rate"]].rename(columns={"Display Pipeline": region_label})
        st.dataframe(table.style.format({region_label: ("₹{:,.0f}" if currency == "INR" else "${:,.0f}"), "Win Rate": "{:.0%}"}), hide_index=True, width="stretch")

    st.markdown("#### Top 10 opportunities by value")
    top = data.nlargest(10, "Amount ($)").copy()
    top[region_label] = top["Amount ($)"] * (rate if currency == "INR" else 1)
    st.dataframe(top[["Opportunity Name", "Account", "Stage", region_label, "Sales Rep", "Close Quarter"]].style.format({region_label: ("₹{:,.0f}" if currency == "INR" else "${:,.0f}")}), hide_index=True, width="stretch")

    funnel, trend = st.columns(2)
    with funnel:
        funnel_data = data.groupby("Stage", as_index=False).agg(Opportunities=("Opportunity ID", "count")).sort_values("Opportunities")
        st.plotly_chart(_bar(funnel_data, "Opportunities", "Stage", "Sales funnel", "#14b8a6"), width="stretch")
    with trend:
        stage = data[data["Stage"].isin(OPEN_STAGES)].groupby("Stage", as_index=False).agg(Pipeline=("Amount ($)", "sum"))
        stage[region_label] = stage["Pipeline"] * (rate if currency == "INR" else 1)
        st.plotly_chart(_bar(stage.sort_values(region_label), region_label, "Stage", "Open pipeline by stage", "#8b5cf6"), width="stretch")

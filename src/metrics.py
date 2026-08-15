"""Shared business calculations for exploration and decision making."""

from __future__ import annotations

import pandas as pd

from config.settings import CLOSED_STAGES, OPEN_STAGES


def filtered_data(data: pd.DataFrame, selections: dict[str, list[str]], search: str = "") -> pd.DataFrame:
    result = data.copy()
    for column, values in selections.items():
        if values:
            result = result[result[column].astype(str).isin(values)]
    if search.strip():
        term = search.strip().casefold()
        result = result[
            result["Opportunity Name"].astype(str).str.casefold().str.contains(term, na=False)
            | result["Account"].astype(str).str.casefold().str.contains(term, na=False)
        ]
    return result


def executive_metrics(data: pd.DataFrame, revenue_target: float) -> dict[str, float]:
    open_deals = data[data["Stage"].isin(OPEN_STAGES)]
    closed_deals = data[data["Stage"].isin(CLOSED_STAGES)]
    total_pipeline = float(open_deals["Amount ($)"].sum())
    weighted_pipeline = float(open_deals["Weighted Pipeline ($)"].sum())
    won_revenue = float(data.loc[data["Stage"].eq("Closed Won"), "Amount ($)"].sum())
    win_rate = float(closed_deals["Stage"].eq("Closed Won").mean()) if not closed_deals.empty else 0.0
    average_deal = float(data["Amount ($)"].mean()) if not data.empty else 0.0
    coverage = total_pipeline / revenue_target if revenue_target else 0.0
    return {
        "total_pipeline": total_pipeline,
        "weighted_pipeline": weighted_pipeline,
        "won_revenue": won_revenue,
        "win_rate": win_rate,
        "average_deal": average_deal,
        "pipeline_coverage": coverage,
    }


def region_performance(data: pd.DataFrame) -> pd.DataFrame:
    result = data.groupby("Region", as_index=False).agg(
        Opportunities=("Opportunity ID", "count"),
        Pipeline=("Amount ($)", "sum"),
        Weighted_Pipeline=("Weighted Pipeline ($)", "sum"),
        Won=("Stage", lambda stages: stages.eq("Closed Won").sum()),
        Closed=("Stage", lambda stages: stages.isin(CLOSED_STAGES).sum()),
    )
    result["Win Rate"] = (result["Won"] / result["Closed"].replace(0, pd.NA)).fillna(0.0)
    return result.sort_values("Pipeline", ascending=False)

"""Display formatting helpers."""

from __future__ import annotations

import pandas as pd


def money(value: float, currency: str, usd_to_inr: float) -> str:
    if pd.isna(value):
        return "—"
    if currency == "INR":
        return f"₹{value * usd_to_inr:,.0f}"
    return f"${value:,.0f}"


def currency_column(values: pd.Series, currency: str, usd_to_inr: float) -> pd.Series:
    multiplier = usd_to_inr if currency == "INR" else 1
    return values * multiplier


def currency_label(currency: str) -> str:
    return "Amount (INR)" if currency == "INR" else "Amount (USD)"
